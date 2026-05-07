# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.
"""
AI surveillance brief — public-health interpretation layer over the
already-anonymised weekly aggregate export.

Three design rules govern this module:

1. **Privacy boundary** — the generator only sees the export envelope
   that has already been stripped of PHI (no local_child_id, no vitals,
   no notes, no operator initials). The allowlist :data:`SAFE_EXPORT_FIELDS`
   is the single chokepoint between storage and any generator.

2. **Two interchangeable generators behind one schema** — the default
   ``deterministic_template`` generator is rule-based and runs fully
   offline; ``llm_brief_v1`` calls a local LLM (Ollama or any
   Ollama-compatible server) when the implementer has explicitly opted
   in. Both produce the same :class:`AggregateBrief` shape so the UI
   renders identically and tests can assert against one schema.

3. **Edge-only intelligence** — the LLM path deliberately does NOT
   call hosted SaaS APIs (no Anthropic, no OpenAI). The product's core
   promise is that every layer — clinical calculation at the point of
   care, anonymisation at the device, AI interpretation — runs without
   internet. The implementer can run Ollama on the local node itself or
   on any host inside the clinic LAN; see docs/integrations/ollama.md.
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

# Allowlist of export envelope fields the brief generator may consume.
# Anything outside this set is dropped before reaching a generator. See
# apps/local-node/tests/test_brief.py::test_safe_payload_keeps_only_allowlisted_export_fields
# and ::test_safe_payload_drops_phi_like_fields_if_export_drift_introduces_them.
SAFE_EXPORT_FIELDS = frozenset(
    {
        "zone",
        "week",
        "indicator",
        "count",
        "baseline_mean",
        "baseline_std",
        "z_score",
        "flag",
        "severity",
        "signal_source",
        "climate_context",
        "quality_warnings",
        "contains_phi",
    }
)

# Climate context keys that are safe to forward. Note: the upstream
# export already strips ``notes``; this is a defence-in-depth filter.
SAFE_CLIMATE_FIELDS = frozenset(
    {
        "rainfall",
        "flooding",
        "heat_alert",
        "water_disruption",
        "vector_risk",
        "source",
        "confidence",
    }
)

DETERMINISTIC_GENERATOR = "deterministic_template"
LLM_GENERATOR = "llm_brief_v1"

SUPPORTED_LANGS = ("en", "es")
DEFAULT_LANG = "en"


def _normalize_lang(lang: str | None) -> str:
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


DISCLAIMER_BY_LANG = {
    "en": (
        "AI-assisted public health interpretation. Not a clinical diagnosis. "
        "Operates only on aggregate, de-identified zone-level signals. The "
        "underlying point-of-care assessment never leaves the clinic device."
    ),
    "es": (
        "Interpretación de salud pública asistida por IA. No es un diagnóstico clínico. "
        "Opera únicamente sobre señales agregadas y anonimizadas a nivel de zona. "
        "La evaluación clínica del punto de atención nunca sale del dispositivo de la clínica."
    ),
}


@dataclass(frozen=True)
class AggregateBrief:
    """Stable schema produced by every generator."""

    headline: str
    what_changed: str
    why_review_needed: str
    operational_considerations: list[str]
    data_quality_limits: list[str]
    escalation_recommendation: str
    generator: str
    generated_at: str
    language: str = DEFAULT_LANG
    disclaimer: str = ""
    used_payload: dict[str, Any] = field(default_factory=dict)

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


class BriefError(RuntimeError):
    """Raised when the brief cannot be produced."""


def safe_payload(export: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *export* containing only allowlisted fields.

    This is the single chokepoint between the storage layer and any
    generator. Both deterministic and LLM generators consume the output
    of this function, so a regression in the privacy boundary is caught
    by a single test rather than being scattered across generators.
    """
    payload: dict[str, Any] = {key: export[key] for key in SAFE_EXPORT_FIELDS if key in export}
    climate = payload.get("climate_context")
    if isinstance(climate, dict):
        payload["climate_context"] = {
            key: climate[key] for key in SAFE_CLIMATE_FIELDS if key in climate
        }
    return payload


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ────────────────────────────────────────────────────────────────────────
# Deterministic generator (default · offline)
# ────────────────────────────────────────────────────────────────────────

# Indicator → (headline phrase, case noun) per language.
INDICATOR_PHRASES = {
    "en": {
        "dengue_suspicion": ("dengue cluster signal", "suspected dengue cases"),
        "malaria_suspicion": ("malaria cluster signal", "suspected malaria cases"),
        "diarrheal_disease": ("diarrheal disease signal", "diarrheal disease cases"),
        "heat_related_illness": ("heat-related illness signal", "heat-related cases"),
        "respiratory_outbreak": ("respiratory outbreak signal", "respiratory cases"),
        "malnutrition_signal": (
            "acute malnutrition signal",
            "children flagged for nutrition review",
        ),
    },
    "es": {
        "dengue_suspicion": ("señal de cluster de dengue", "casos sospechosos de dengue"),
        "malaria_suspicion": ("señal de cluster de malaria", "casos sospechosos de malaria"),
        "diarrheal_disease": ("señal de enfermedad diarreica", "casos de enfermedad diarreica"),
        "heat_related_illness": (
            "señal de evento asociado a calor",
            "casos asociados al calor",
        ),
        "respiratory_outbreak": ("señal de brote respiratorio", "casos respiratorios"),
        "malnutrition_signal": (
            "señal de malnutrición aguda",
            "niños marcados para revisión nutricional",
        ),
    },
}


def _phrase_for(indicator: str, lang: str) -> tuple[str, str]:
    return INDICATOR_PHRASES[lang].get(
        indicator,
        (f"{indicator.replace('_', ' ')} signal", "cases"),
    )


def _percent_above_baseline(count: float | int | None, baseline_mean: float | int | None) -> float | None:
    if count is None or baseline_mean is None:
        return None
    if baseline_mean <= 0:
        return None
    try:
        return round(((float(count) - float(baseline_mean)) / float(baseline_mean)) * 100.0, 1)
    except (TypeError, ValueError):
        return None


CLIMATE_FACTOR_PHRASES = {
    "en": {
        "rainfall_moderate": "recent moderate rainfall reported",
        "rainfall_heavy": "recent heavy rainfall reported",
        "flooding_reported": "standing water / flooding reported in the zone",
        "heat_alert_yes": "an active heat alert applies to the zone",
        "water_disruption_yes": "an interruption to safe water supply was reported",
        "vector_risk_increased": "the operator marked vector risk as increased",
    },
    "es": {
        "rainfall_moderate": "se reportaron lluvias moderadas recientes",
        "rainfall_heavy": "se reportaron lluvias fuertes recientes",
        "flooding_reported": "se reportó agua estancada o inundación en la zona",
        "heat_alert_yes": "hay una alerta de calor activa en la zona",
        "water_disruption_yes": "se reportó una interrupción del suministro de agua segura",
        "vector_risk_increased": "el operador marcó el riesgo vectorial como aumentado",
    },
}


def _climate_factors(climate: dict[str, Any] | None, lang: str) -> list[str]:
    """Translate structured climate fields into human factors.

    Rule-based on purpose: the generator never claims causation. It only
    notes the operator-recorded conditions that public health responders
    typically associate with the indicator.
    """
    if not climate:
        return []
    table = CLIMATE_FACTOR_PHRASES[lang]
    factors: list[str] = []
    rainfall = climate.get("rainfall")
    if rainfall == "moderate":
        factors.append(table["rainfall_moderate"])
    elif rainfall == "heavy":
        factors.append(table["rainfall_heavy"])
    if climate.get("flooding") == "reported":
        factors.append(table["flooding_reported"])
    if climate.get("heat_alert") == "yes":
        factors.append(table["heat_alert_yes"])
    if climate.get("water_disruption") == "yes":
        factors.append(table["water_disruption_yes"])
    if climate.get("vector_risk") == "increased":
        factors.append(table["vector_risk_increased"])
    return factors


QUALITY_CAVEATS_BY_LANG = {
    "en": {
        "_none": "No quality warnings flagged for this signal.",
        "prepilot_thresholds_not_field_calibrated": (
            "Pre-pilot thresholds are not yet calibrated against local field data."
        ),
        "vaccination_schedule_pending_moh_validation": (
            "The vaccination reference schedule is pending Ministry of Health validation."
        ),
        "no_climate_context_recorded": (
            "No climate context was recorded for this zone-week, so environmental "
            "interpretation is unavailable."
        ),
        "signal_uses_synthetic_demo_data": (
            "This signal was produced from synthetic walkthrough data and must not "
            "drive real-world public health action."
        ),
    },
    "es": {
        "_none": "No hay advertencias de calidad para esta señal.",
        "prepilot_thresholds_not_field_calibrated": (
            "Los umbrales pre-piloto aún no están calibrados con datos de campo locales."
        ),
        "vaccination_schedule_pending_moh_validation": (
            "El esquema de vacunación de referencia está pendiente de validación del "
            "Ministerio de Salud."
        ),
        "no_climate_context_recorded": (
            "No se registró contexto climático para esta zona-semana, por lo que la "
            "interpretación ambiental no está disponible."
        ),
        "signal_uses_synthetic_demo_data": (
            "Esta señal se produjo a partir de datos sintéticos de demostración y no "
            "debe orientar acciones reales de salud pública."
        ),
    },
}


def _quality_caveats(warnings: list[str] | None, lang: str) -> list[str]:
    """Translate machine warnings into operator-facing caveats."""
    table = QUALITY_CAVEATS_BY_LANG[lang]
    if not warnings:
        return [table["_none"]]
    return [table.get(code, code.replace("_", " ").capitalize()) for code in warnings]


OPERATIONAL_BY_LANG = {
    "en": {
        "dengue_suspicion": [
            "Coordinate vector control / fumigation review with local authorities.",
            "Re-stock paracetamol, oral rehydration salts and rapid dengue NS1 kits if available.",
        ],
        "malaria_suspicion": [
            "Verify rapid diagnostic test (RDT) stock and chemoprophylaxis availability.",
            "Coordinate vector control where Anopheles breeding sites are likely.",
        ],
        "diarrheal_disease": [
            "Verify availability of oral rehydration salts and zinc.",
            "Reinforce community messaging about safe water and handwashing.",
        ],
        "heat_related_illness": [
            "Reinforce hydration and shaded-rest messaging in the affected zone.",
            "Verify capacity to triage heat-stroke at the clinic.",
        ],
        "respiratory_outbreak": [
            "Reinforce respiratory etiquette and verify mask supply.",
            "Coordinate sample referral to the nearest reference laboratory.",
        ],
        "malnutrition_signal": [
            "Re-screen flagged children with weight-for-height or MUAC.",
            "Coordinate with the nutritional supplementation programme.",
        ],
        "_severe": "Escalate to the local health authority within 24 hours.",
        "_moderate": "Notify the supervisor and monitor next week's count closely.",
        "_water_disruption": (
            "Coordinate with the water authority — supply interruption was recorded."
        ),
    },
    "es": {
        "dengue_suspicion": [
            "Coordina con las autoridades locales el control vectorial y la fumigación.",
            "Repón paracetamol, sales de rehidratación oral y pruebas rápidas NS1 de dengue si están disponibles.",
        ],
        "malaria_suspicion": [
            "Verifica el stock de pruebas rápidas (RDT) y la disponibilidad de quimioprofilaxis.",
            "Coordina el control vectorial donde sea probable la cría de Anopheles.",
        ],
        "diarrheal_disease": [
            "Verifica disponibilidad de sales de rehidratación oral y zinc.",
            "Refuerza el mensaje comunitario sobre agua segura y lavado de manos.",
        ],
        "heat_related_illness": [
            "Refuerza el mensaje de hidratación y descanso a la sombra en la zona afectada.",
            "Verifica la capacidad para triar golpe de calor en la clínica.",
        ],
        "respiratory_outbreak": [
            "Refuerza la etiqueta respiratoria y verifica el suministro de mascarillas.",
            "Coordina la referencia de muestras al laboratorio de referencia más cercano.",
        ],
        "malnutrition_signal": [
            "Re-tamiza a los niños señalados con peso-para-talla o MUAC.",
            "Coordina con el programa de suplementación nutricional.",
        ],
        "_severe": "Escala a la autoridad local de salud dentro de las próximas 24 horas.",
        "_moderate": "Notifica al supervisor y monitorea de cerca el conteo de la próxima semana.",
        "_water_disruption": (
            "Coordina con la autoridad de agua — se registró una interrupción del suministro."
        ),
    },
}


def _operational_considerations(
    *,
    indicator: str,
    flag: str | None,
    z_score: float | None,
    climate: dict[str, Any] | None,
    lang: str,
) -> list[str]:
    table = OPERATIONAL_BY_LANG[lang]
    items: list[str] = list(table.get(indicator, []))
    severe = (flag or "").endswith("high_severity") or (z_score is not None and z_score >= 4.0)
    if severe:
        items.append(table["_severe"])
    elif (z_score or 0) >= 2.0:
        items.append(table["_moderate"])
    if climate and climate.get("water_disruption") == "yes":
        items.append(table["_water_disruption"])
    return items


NARRATIVE_BY_LANG = {
    "en": {
        "default_zone": "the zone",
        "default_week": "this week",
        "what_changed_with_pct": (
            "{count} {case_phrase} reported in {zone} for {week}, against a "
            "rolling baseline mean of {mean} ({sign}{pct}%)."
        ),
        "what_changed_no_pct": (
            "{count} {case_phrase} reported in {zone} for {week} (baseline mean {mean})."
        ),
        "z_score": "The current count z-score is {z}.",
        "no_data": "Insufficient data to summarise the change for this week.",
        "why_high": (
            "The current count exceeds the rolling baseline by a margin the "
            "anomaly detector classifies as high severity. Statistical, not clinical."
        ),
        "why_anomaly": (
            "The current count is above the rolling baseline threshold. Statistical "
            "signal only; clinician review recommended before action."
        ),
        "why_insufficient": (
            "The baseline window is too small for a reliable comparison. The signal "
            "should be interpreted with caution and re-evaluated next week."
        ),
        "why_normal": (
            "The current count sits within the expected baseline. No anomaly is "
            "flagged — this brief is provided as a routine summary."
        ),
        "context_join": "Operator-recorded environmental context: {factors}.",
        "factors_separator": "; ",
        "escalation_high": (
            "Escalate to the local public health authority and consider activating "
            "the zone's outbreak protocol within 24 hours."
        ),
        "escalation_moderate": (
            "Notify the supervising public health officer and increase the reporting "
            "cadence for the zone."
        ),
        "escalation_none": "No escalation required at this time. Continue routine reporting.",
    },
    "es": {
        "default_zone": "la zona",
        "default_week": "esta semana",
        "what_changed_with_pct": (
            "{count} {case_phrase} reportados en {zone} para {week}, frente a una "
            "media móvil base de {mean} ({sign}{pct}%)."
        ),
        "what_changed_no_pct": (
            "{count} {case_phrase} reportados en {zone} para {week} (media base {mean})."
        ),
        "z_score": "El z-score del conteo actual es {z}.",
        "no_data": "Datos insuficientes para resumir el cambio de esta semana.",
        "why_high": (
            "El conteo actual supera la línea base móvil por un margen que el detector "
            "de anomalías clasifica como alta severidad. Señal estadística, no clínica."
        ),
        "why_anomaly": (
            "El conteo actual está por encima del umbral de la línea base móvil. Solo "
            "señal estadística; se recomienda revisión clínica antes de actuar."
        ),
        "why_insufficient": (
            "La ventana base es demasiado pequeña para una comparación confiable. La "
            "señal debe interpretarse con cautela y reevaluarse la próxima semana."
        ),
        "why_normal": (
            "El conteo actual está dentro de la línea base esperada. No hay anomalía "
            "marcada — este briefing se entrega como resumen de rutina."
        ),
        "context_join": "Contexto ambiental registrado por el operador: {factors}.",
        "factors_separator": "; ",
        "escalation_high": (
            "Escala a la autoridad local de salud pública y considera activar el "
            "protocolo de brote de la zona dentro de las próximas 24 horas."
        ),
        "escalation_moderate": (
            "Notifica al oficial supervisor de salud pública y aumenta la cadencia "
            "de reporte para la zona."
        ),
        "escalation_none": "No se requiere escalamiento en este momento. Continúa el reporte de rutina.",
    },
}


def _generate_deterministic(payload: dict[str, Any], lang: str) -> AggregateBrief:
    text = NARRATIVE_BY_LANG[lang]
    headline_phrase, case_phrase = _phrase_for(payload.get("indicator", ""), lang)
    zone = payload.get("zone") or text["default_zone"]
    week = payload.get("week") or text["default_week"]
    flag = payload.get("flag")
    z_score = payload.get("z_score")
    count = payload.get("count")
    baseline_mean = payload.get("baseline_mean")
    climate = payload.get("climate_context")
    warnings = payload.get("quality_warnings", [])
    pct = _percent_above_baseline(count, baseline_mean)

    headline = f"{headline_phrase[:1].upper()}{headline_phrase[1:]} · {zone} · {week}"

    parts_changed: list[str] = []
    if count is not None and baseline_mean is not None:
        mean_rounded = round(float(baseline_mean), 1)
        if pct is not None:
            parts_changed.append(
                text["what_changed_with_pct"].format(
                    count=int(count),
                    case_phrase=case_phrase,
                    zone=zone,
                    week=week,
                    mean=mean_rounded,
                    sign="+" if pct >= 0 else "",
                    pct=pct,
                )
            )
        else:
            parts_changed.append(
                text["what_changed_no_pct"].format(
                    count=int(count),
                    case_phrase=case_phrase,
                    zone=zone,
                    week=week,
                    mean=mean_rounded,
                )
            )
    if z_score is not None:
        parts_changed.append(text["z_score"].format(z=round(float(z_score), 2)))
    if not parts_changed:
        parts_changed.append(text["no_data"])
    what_changed = " ".join(parts_changed)

    if flag and flag.endswith("high_severity"):
        why_review = text["why_high"]
    elif flag == "anomaly":
        why_review = text["why_anomaly"]
    elif flag == "insufficient_baseline":
        why_review = text["why_insufficient"]
    else:
        why_review = text["why_normal"]

    factors = _climate_factors(climate, lang)
    if factors:
        why_review += " " + text["context_join"].format(
            factors=text["factors_separator"].join(factors)
        )

    operational = _operational_considerations(
        indicator=payload.get("indicator", ""),
        flag=flag,
        z_score=float(z_score) if z_score is not None else None,
        climate=climate,
        lang=lang,
    )

    if flag and flag.endswith("high_severity"):
        escalation = text["escalation_high"]
    elif (z_score or 0) >= 2.0:
        escalation = text["escalation_moderate"]
    else:
        escalation = text["escalation_none"]

    return AggregateBrief(
        headline=headline,
        what_changed=what_changed,
        why_review_needed=why_review,
        operational_considerations=operational,
        data_quality_limits=_quality_caveats(warnings, lang),
        escalation_recommendation=escalation,
        generator=DETERMINISTIC_GENERATOR,
        generated_at=_utc_now(),
        language=lang,
        disclaimer=DISCLAIMER_BY_LANG[lang],
        used_payload=payload,
    )


# ────────────────────────────────────────────────────────────────────────
# Local LLM generator (optional · Ollama or any Ollama-compatible server)
# ────────────────────────────────────────────────────────────────────────
#
# Why Ollama only and not Anthropic/OpenAI:
#
# KYNODE Pediatric is an offline-first edge HIS. Calling a hosted SaaS
# LLM would break the core promise of the product — that the entire
# intelligence stack runs at the clinic, without internet. Instead, this
# module talks to an Ollama-compatible server (default: localhost:11434),
# which the implementer runs on the same machine as the local node or on
# a small server inside the clinic LAN. The data the brief uses already
# went through `safe_payload`, so no PHI ever leaves the box even when
# the operator points the endpoint at a custom URL.
#
# Activation contract:
#   - KYNODE_AI_BRIEF_PROVIDER=ollama       → opt in
#   - KYNODE_AI_BRIEF_ENDPOINT (optional)   → defaults to http://localhost:11434/api/chat
#   - KYNODE_AI_BRIEF_MODEL    (optional)   → defaults to llama3.2
#
# If the env var is unset (default), the deterministic generator runs.

LLM_PROVIDER_ENV = "KYNODE_AI_BRIEF_PROVIDER"
LLM_ENDPOINT_ENV = "KYNODE_AI_BRIEF_ENDPOINT"
LLM_MODEL_ENV = "KYNODE_AI_BRIEF_MODEL"

OLLAMA_PROVIDER = "ollama"
OLLAMA_DEFAULT_ENDPOINT = "http://localhost:11434/api/chat"
OLLAMA_DEFAULT_MODEL = "llama3.2"
OLLAMA_TIMEOUT_SECONDS = 25

LLM_SYSTEM_PROMPT_BY_LANG = {
    "en": (
        "You are a public health analyst summarising a privacy-bounded, aggregate "
        "weekly surveillance signal for a local clinic. The payload contains zero "
        "patient identifiers. You MUST NOT diagnose, prescribe, or attribute a "
        "single cause to the signal. Respond with strict JSON matching this schema, "
        "no extra commentary:\n"
        "{\n"
        '  "headline": "<one-line summary including indicator, zone, week>",\n'
        '  "what_changed": "<two short sentences quantifying the change vs baseline>",\n'
        '  "why_review_needed": "<two short sentences explaining the statistical signal>",\n'
        '  "operational_considerations": ["<short bullet 1>", "<short bullet 2>", ...],\n'
        '  "data_quality_limits": ["<short caveat 1>", "<short caveat 2>", ...],\n'
        '  "escalation_recommendation": "<one short sentence>"\n'
        "}\n"
        "Language: respond in English. Tone: clinical, neutral, operational. "
        "Never claim a diagnosis."
    ),
    "es": (
        "Eres un analista de salud pública resumiendo una señal de vigilancia "
        "semanal agregada y con privacidad acotada para una clínica local. La "
        "carga útil no contiene identificadores de pacientes. NO debes diagnosticar, "
        "prescribir ni atribuir una causa única a la señal. Responde con JSON "
        "estricto que coincida con este esquema, sin comentarios adicionales:\n"
        "{\n"
        '  "headline": "<resumen de una línea con indicador, zona, semana>",\n'
        '  "what_changed": "<dos oraciones cortas cuantificando el cambio vs línea base>",\n'
        '  "why_review_needed": "<dos oraciones cortas explicando la señal estadística>",\n'
        '  "operational_considerations": ["<bullet corto 1>", "<bullet corto 2>", ...],\n'
        '  "data_quality_limits": ["<caveat corto 1>", "<caveat corto 2>", ...],\n'
        '  "escalation_recommendation": "<una oración corta>"\n'
        "}\n"
        "Idioma: responde en español neutro latinoamericano (sin voseo). Tono: "
        "clínico, neutro, operativo. Nunca afirmes un diagnóstico."
    ),
}


def _llm_enabled() -> bool:
    """The LLM path is enabled only when an Ollama-compatible provider is set.

    Other strings (legacy "anthropic", "openai", typos) are intentionally
    treated as not-enabled so a misconfiguration silently falls back to
    the deterministic generator instead of attempting an outbound call.
    """
    return os.environ.get(LLM_PROVIDER_ENV, "").strip().lower() == OLLAMA_PROVIDER


def _resolve_endpoint() -> str:
    return os.environ.get(LLM_ENDPOINT_ENV, "").strip() or OLLAMA_DEFAULT_ENDPOINT


def _resolve_model() -> str:
    return os.environ.get(LLM_MODEL_ENV, "").strip() or OLLAMA_DEFAULT_MODEL


# ────────────────────────────────────────────────────────────────────────
# Endpoint trust boundary
# ────────────────────────────────────────────────────────────────────────
#
# The product's promise is "no hosted SaaS API is ever called". Refusing
# unknown providers in `_llm_enabled` is necessary but not sufficient —
# an operator could still set KYNODE_AI_BRIEF_ENDPOINT to a public URL
# and effectively turn the brief into a hosted call.
#
# We enforce a default trust boundary at the resolver level: only
# loopback (127.0.0.1, ::1) and RFC1918 / link-local / unique-local
# addresses are accepted. If the operator deliberately wants to point at
# a public endpoint (e.g. their own hosted Ollama behind a VPN they
# trust), they set KYNODE_AI_BRIEF_ALLOW_PUBLIC=true and accept that
# the trust boundary is now their responsibility, not the product's.

ALLOW_PUBLIC_ENV = "KYNODE_AI_BRIEF_ALLOW_PUBLIC"


# Cloud-provider link-local metadata endpoints. Even though they live in
# the link-local range (and would therefore pass the generic check
# below), they are well-known SSRF targets — IAM tokens, instance
# credentials, etc. Reject them explicitly so a misconfigured Ollama
# endpoint can never be tricked into hitting them.
_CLOUD_METADATA_IPS = frozenset(
    {
        "169.254.169.254",   # AWS, GCP, Azure (IMDSv1 / IMDSv2 endpoint)
        "100.100.100.200",   # Alibaba Cloud
        "169.254.170.2",     # AWS ECS task metadata
        "fd00:ec2::254",     # AWS IMDSv2 IPv6
    }
)


def _hostname_is_private(host: str) -> bool:
    """Return True if *host* is loopback, RFC1918 or otherwise non-public.

    Hostnames that resolve to public IPs are rejected here because we
    cannot guarantee at config time what they resolve to at call time.
    The operator must opt out via :data:`ALLOW_PUBLIC_ENV` to use them.

    Cloud-provider metadata IPs (AWS / GCP / Azure / Alibaba) are
    rejected even though they are technically link-local — they are
    classic SSRF targets and our brief endpoint should never reach them
    by accident.
    """
    if not host:
        return False
    if host.lower() in _CLOUD_METADATA_IPS:
        return False
    if host in {"localhost", "host.docker.internal"}:
        return True
    # IPv4 / IPv6 literal
    try:
        addr = ipaddress.ip_address(host)
        if str(addr) in _CLOUD_METADATA_IPS:
            return False
        return (
            addr.is_loopback
            or addr.is_private
            or addr.is_link_local
            or addr.is_unspecified
        )
    except ValueError:
        pass
    # Hostname with a TLD that is unambiguously local. We keep this
    # narrow so a tricky DNS like `localhost.evil.com` does not match.
    return host.endswith((".local", ".lan", ".internal", ".intranet"))


def _endpoint_is_trusted(endpoint: str) -> bool:
    """Return True if the endpoint is on an offline-safe network.

    `KYNODE_AI_BRIEF_ALLOW_PUBLIC=true` overrides this check; the operator
    explicitly accepts that the brief now leaves the device's trust zone.
    """
    if os.environ.get(ALLOW_PUBLIC_ENV, "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    parsed = urllib_parse.urlparse(endpoint)
    return _hostname_is_private(parsed.hostname or "")


def _llm_request_body(
    model: str,
    payload: dict[str, Any],
    lang: str = DEFAULT_LANG,
) -> dict[str, Any]:
    """Build the Ollama /api/chat body. The same body works against any
    server that implements the Ollama chat API (LM Studio, llama.cpp's
    server when run with the `--api ollama` adapter, etc.)."""
    system_prompt = LLM_SYSTEM_PROMPT_BY_LANG[_normalize_lang(lang)]
    user_message = (
        "Aggregate weekly surveillance payload (no PHI):\n"
        + json.dumps(payload, sort_keys=True)
    )
    return {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }


def _llm_extract_text(response_body: dict[str, Any]) -> str:
    try:
        return response_body["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise BriefError("Could not parse Ollama response.") from exc


def _llm_call(payload: dict[str, Any], lang: str = DEFAULT_LANG) -> dict[str, Any]:
    """Call the configured local LLM with a privacy-bounded payload.

    No API key is needed — Ollama listens on localhost (or the configured
    LAN endpoint) without authentication. We refuse to dial out to a
    public IP unless the operator has explicitly set
    `KYNODE_AI_BRIEF_ALLOW_PUBLIC=true`; see docs/integrations/ollama.md.
    """
    endpoint = _resolve_endpoint()
    if not _endpoint_is_trusted(endpoint):
        raise BriefError(
            f"Refusing to call brief endpoint {endpoint!r}: only loopback / "
            "private-network hosts are trusted by default. Set "
            f"{ALLOW_PUBLIC_ENV}=true to override (you accept the trust boundary)."
        )
    model = _resolve_model()
    body = _llm_request_body(model, payload, lang)
    request_obj = urllib_request.Request(
        endpoint,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(request_obj, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            response_body = json.loads(response.read())
    except (urllib_error.URLError, urllib_error.HTTPError, TimeoutError) as exc:
        raise BriefError(f"Local LLM request failed: {exc}") from exc
    text = _llm_extract_text(response_body)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise BriefError("Local LLM response was not valid JSON.") from exc


def _coerce_bullets(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


# ────────────────────────────────────────────────────────────────────────
# Clinical safety gate (post-LLM)
# ────────────────────────────────────────────────────────────────────────
#
# The LLM path is opt-in and runs offline, but it is still a generative
# system. We MUST NOT render text that could be misread as a diagnosis,
# a prescription, a treatment recommendation, or a single-cause causal
# claim — even if a small local model decides to produce it.
#
# When the gate trips, we throw the LLM output away and fall back to the
# deterministic generator. The reason is recorded in audit_events via
# the surrounding service so reviewers can see why the LLM brief was
# rejected.

class UnsafeBriefError(BriefError):
    """Raised when the LLM output contains clinically-unsafe phrasing.

    Subclass of BriefError so the existing fallback path
    (generate_brief → except BriefError → deterministic) catches it
    without any extra wiring.
    """

    def __init__(self, matched: list[str], language: str) -> None:
        super().__init__(
            f"Clinical safety gate rejected LLM brief in {language!r}: "
            f"matched {matched!r}"
        )
        self.matched = matched
        self.language = language


# Phrases the LLM must NEVER emit. Keys are language codes; each list is
# a set of compiled regexes. We use whole-word boundaries (`\b`) where the
# language allows, plus tolerant whitespace, so trivial paraphrasing
# (mixed case, plurals, accents) does not slip through.
_UNSAFE_PATTERNS_BY_LANG: dict[str, list[re.Pattern[str]]] = {
    "en": [
        # ── Diagnosis ────────────────────────────────────────────────
        # `diagnostic` alone would match the legitimate "rapid
        # diagnostic test (RDT)" in our own malaria template. We allow
        # the noun phrase "diagnostic test" but block the verb forms
        # and the standalone noun "diagnosis", as well as the
        # "definitive/confirmed diagnostic" phrasings that appear when
        # an LLM tries to stand in for a clinician.
        re.compile(r"\b(diagnose[ds]?|diagnosing|diagnosis|diagnoses)\b", re.IGNORECASE),
        re.compile(r"\b(?:make|provide|reach)\s+(?:a\s+)?diagnos(?:is|tic)\b", re.IGNORECASE),
        re.compile(
            r"\b(?:definitive|confirmed|likely|probable|presumptive)\s+diagnos(?:is|tic)\b",
            re.IGNORECASE,
        ),
        re.compile(r"\b(?:this|the\s+signal|the\s+data)\s+(?:indicates|suggests|implies|means)\s+\w+\s+(?:infection|disease|condition)\b", re.IGNORECASE),
        re.compile(r"\b(?:likely|probable|suspected|confirmed)\s+(?:dengue|malaria|cholera|typhoid)\s+(?:serotype|strain|species|infection)\b", re.IGNORECASE),
        # ── Prescription / pharmaceutical orders ─────────────────────
        re.compile(r"\b(prescrib(?:e|ed|ing|tion)|prescription|recommended\s+therapy)\b", re.IGNORECASE),
        re.compile(r"\b(administer|dose\s+of|dosage)\b", re.IGNORECASE),
        # ── Treatment / therapy / clinical action verbs ──────────────
        re.compile(r"\b(?:start|begin|initiate|continue|stop)\s+(?:\w+\s+)?(?:treatment|therapy|antibiotic|antimalarial|antiviral|chemoprophylaxis)\b", re.IGNORECASE),
        re.compile(r"\b(?:treatment|therapy)\s+(?:protocol|plan|regimen|course)\b", re.IGNORECASE),
        re.compile(
            r"\btreat(?:ment)?(?:\s+the\s+patient|\s+children|\s+the\s+child|\s+infants?|\s+with\s+\w+)\b",
            re.IGNORECASE,
        ),
        re.compile(r"\b(?:hospitalize|hospitalise|admit)\b", re.IGNORECASE),
        re.compile(r"\brefer\s+(?:to|for)\s+(?:\w+\s+){0,3}(?:hospital|icu|nicu|emergency|paediatric|pediatric|inpatient|ward|admission)\b", re.IGNORECASE),
        # ── Causal / attribution claims ──────────────────────────────
        re.compile(r"\b(?:is|was|were|are)\s+caused\s+by\b", re.IGNORECASE),
        re.compile(r"\b(?:caused|provoked|triggered|driven|fueled)\s+by\s+(?:the\s+)?(?:rain|flood|water|heat|climate|outbreak)\b", re.IGNORECASE),
        # ── Outbreak / disease-confirmation claims ───────────────────
        re.compile(r"\b(?:confirmed|active|ongoing|definitive|established)\s+(?:outbreak|epidemic|cases?)\b", re.IGNORECASE),
        re.compile(r"\boutbreak\s+(?:is\s+)?confirmed\b", re.IGNORECASE),
        re.compile(r"\b(?:this|signal|cluster)\s+(?:proves|confirms|demonstrates|establishes)\s+(?:an?\s+)?\w*", re.IGNORECASE),
    ],
    "es": [
        # ── Diagnóstico ──────────────────────────────────────────────
        # `diagnostic[oa]s?` por sí solo matchearía el sustantivo inglés
        # "diagnostic" en frases legítimas como "rapid diagnostic test
        # (RDT)". Requerimos contexto español alrededor del adjetivo y
        # mantenemos el sustantivo con tilde y los verbos como anchors
        # inequívocamente españoles.
        re.compile(
            r"(?:\b(?:el|los|las|un|una|para|de|sin|hacer|emitir|dar|confirmar)\s+diagn[oó]stic[oa]s?\b)",
            re.IGNORECASE,
        ),
        re.compile(r"\b(diagn[óo]stico|diagnosticar|diagnostique[ns]?)\b", re.IGNORECASE),
        re.compile(
            r"\b(?:diagn[óo]stico|cuadro)\s+(?:definitivo|confirmado|probable|presuntivo|sugestivo)\b",
            re.IGNORECASE,
        ),
        re.compile(r"\b(?:esto|la\s+se[ñn]al|los\s+datos)\s+(?:indica|sugiere|implica|significa)\s+(?:una?\s+)?(?:infecci[óo]n|enfermedad)\b", re.IGNORECASE),
        # "Probable dengue serotype 2" / "Probable serotipo de dengue 2"
        # / "Sospechada infección por malaria" — disease attribution.
        re.compile(r"\b(?:probable|sospechad[oa]|confirmad[oa]|presuntiv[oa])\s+(?:dengue|malaria|c[óo]lera|tifoidea|serotipo|cepa|especie|infecci[óo]n)\b", re.IGNORECASE),
        re.compile(r"\bserotipo\s+(?:de\s+)?(?:dengue|malaria|c[óo]lera|tifoidea)\b", re.IGNORECASE),
        # ── Prescripción / órdenes farmacéuticas ─────────────────────
        re.compile(r"\b(prescrib[ie](?:ndo|r|en)?|prescripci[óo]n|recetar?|terapia\s+recomendada)\b", re.IGNORECASE),
        re.compile(r"\b(administrar?|dosificaci[óo]n)\b", re.IGNORECASE),
        # ── Tratamiento / terapia / acción clínica ───────────────────
        re.compile(r"\b(?:iniciar|comenzar|empezar|continuar|detener|suspender)\s+(?:\w+\s+)?(?:tratamiento|terapia|antibi[óo]tic[oa]s?|antimal[áa]ric[oa]s?|antiviral|quimioprofilaxis)\b", re.IGNORECASE),
        re.compile(r"\b(?:tratamiento|terapia)\s+(?:antibi[óo]tica|antimal[áa]rica|antiviral|protocolo|plan|esquema|regimen)\b", re.IGNORECASE),
        re.compile(r"\bprotocolo\s+(?:de\s+)?(?:tratamiento|terapia)\b", re.IGNORECASE),
        re.compile(r"\btratar\s+(?:al?\s+)?(?:paciente|ni[ñn]o|lactante)\b", re.IGNORECASE),
        re.compile(r"\b(?:hospitalizar|ingresar|internar|referir)\s+(?:a\s+)?(?:los?\s+)?(?:ni[ñn]os?|pacientes?|lactantes?|hospital|uci|emergencia)\b", re.IGNORECASE),
        # ── Atribución causal ────────────────────────────────────────
        re.compile(r"\b(causad[oa]s?\s+por|provocad[oa]s?\s+por|generad[oa]s?\s+por)\b", re.IGNORECASE),
        # ── Afirmación de brote confirmado ───────────────────────────
        re.compile(r"\b(?:brote|epidemia|casos?)\s+(?:confirmad[oa]s?|activ[oa]s?|definitiv[oa]s?|establecid[oa]s?)\b", re.IGNORECASE),
        re.compile(r"\b(?:esto|esta\s+se[ñn]al|el\s+cl[uú]ster)\s+(?:prueba|confirma|demuestra|establece)\b", re.IGNORECASE),
    ],
}


def _validate_brief_safety(raw: dict[str, Any], lang: str) -> None:
    """Raise :class:`UnsafeBriefError` if any rendered text matches a
    forbidden clinical phrase. The check looks at every visible field —
    headline, narrative, bullets, escalation — because the UI renders
    all of them. Raw payload echoes (`used_payload`) are NOT checked
    because they hold the original numbers that the rest of the system
    already rendered safely.

    The validator scans **every** supported language's patterns, not
    only the one the operator asked for. Small local models (llama3.2,
    qwen2.5:0.5b, phi3:mini) routinely ignore the language directive in
    the system prompt and reply in the wrong tongue — an English
    request that comes back with ``Diagnosticar brote de dengue ahora``
    must still be rejected. The :class:`UnsafeBriefError` keeps the
    requested language only as error metadata so audit logs can trace
    which UI session triggered the rejection.
    """
    rendered_pieces: list[str] = [
        str(raw.get("headline", "")),
        str(raw.get("what_changed", "")),
        str(raw.get("why_review_needed", "")),
        str(raw.get("escalation_recommendation", "")),
    ]
    rendered_pieces.extend(_coerce_bullets(raw.get("operational_considerations")))
    rendered_pieces.extend(_coerce_bullets(raw.get("data_quality_limits")))
    haystack = " ".join(piece for piece in rendered_pieces if piece)
    if not haystack.strip():
        return

    matched: list[str] = []
    for patterns in _UNSAFE_PATTERNS_BY_LANG.values():
        for pattern in patterns:
            match = pattern.search(haystack)
            if match:
                matched.append(match.group(0).lower())
    if matched:
        raise UnsafeBriefError(matched=sorted(set(matched)), language=lang)


def _generate_llm(payload: dict[str, Any], lang: str) -> AggregateBrief:
    raw = _llm_call(payload, lang)
    _validate_brief_safety(raw, lang)
    fallback_headline = "Surveillance brief" if lang == "en" else "Briefing de vigilancia"
    return AggregateBrief(
        headline=str(raw.get("headline", "")).strip() or fallback_headline,
        what_changed=str(raw.get("what_changed", "")).strip(),
        why_review_needed=str(raw.get("why_review_needed", "")).strip(),
        operational_considerations=_coerce_bullets(raw.get("operational_considerations")),
        data_quality_limits=_coerce_bullets(raw.get("data_quality_limits")),
        escalation_recommendation=str(raw.get("escalation_recommendation", "")).strip(),
        generator=LLM_GENERATOR,
        generated_at=_utc_now(),
        language=lang,
        disclaimer=DISCLAIMER_BY_LANG[lang],
        used_payload=payload,
    )


# ────────────────────────────────────────────────────────────────────────
# Public entry point
# ────────────────────────────────────────────────────────────────────────


def generate_brief(export: dict[str, Any], lang: str = DEFAULT_LANG) -> AggregateBrief:
    """Produce an :class:`AggregateBrief` from a privacy-bounded export.

    Falls back to the deterministic generator if the LLM path is not
    enabled, the endpoint is unreachable, the response is malformed, or
    the clinical safety gate trips on the LLM output. The deterministic
    path always produces a brief, so a hosted public review never sees
    an empty panel because the LLM is rate-limited, missing a model, or
    produced unsafe phrasing.
    """
    payload = safe_payload(export)
    resolved_lang = _normalize_lang(lang)
    if _llm_enabled():
        try:
            return _generate_llm(payload, resolved_lang)
        except BriefError:
            return _generate_deterministic(payload, resolved_lang)
    return _generate_deterministic(payload, resolved_lang)

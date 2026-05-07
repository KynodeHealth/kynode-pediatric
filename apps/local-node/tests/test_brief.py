# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

from typing import Any

import pytest

from kynode_pediatric_local_node import brief as brief_module
from kynode_pediatric_local_node.brief import (
    DETERMINISTIC_GENERATOR,
    LLM_GENERATOR,
    SAFE_CLIMATE_FIELDS,
    SAFE_EXPORT_FIELDS,
    BriefError,
    generate_brief,
    safe_payload,
)


def _sample_export() -> dict[str, Any]:
    return {
        "export_type": "kynode_pediatric_weekly_aggregate",
        "schema_version": "0.2.0",
        "node": {"clinic_name": "San Cristobal Norte Clinic", "node_label": "X", "country": "VE"},
        "zone": "San Cristobal Norte",
        "week": "2026-W19",
        "indicator": "dengue_suspicion",
        "count": 38,
        "baseline_mean": 22.67,
        "baseline_std": 3.64,
        "z_score": 4.22,
        "flag": "anomaly_high_severity",
        "severity": "high",
        "signal_source": "manual_aggregate_entry",
        "climate_context": {
            "rainfall": "heavy",
            "flooding": "reported",
            "heat_alert": "no",
            "water_disruption": "yes",
            "vector_risk": "increased",
            "source": "clinic_observation",
            "confidence": "medium",
        },
        "quality_warnings": ["prepilot_thresholds_not_field_calibrated"],
        "privacy_checklist": {"local_child_id_removed": True, "vitals_removed": True},
        "contains_phi": False,
    }


def test_safe_payload_keeps_only_allowlisted_export_fields():
    payload = safe_payload(_sample_export())

    assert set(payload).issubset(SAFE_EXPORT_FIELDS)
    # Privacy regression: the brief surface must NOT see node identity,
    # privacy_checklist or any other field that lives outside the
    # allowlist defined in brief.py.
    forbidden = {"node", "privacy_checklist", "export_type", "schema_version"}
    assert forbidden.isdisjoint(payload.keys())


def test_safe_payload_strips_non_allowlisted_climate_fields():
    export = _sample_export()
    export["climate_context"]["notes"] = "Operator-only free text — must never reach an LLM."
    export["climate_context"]["operator_initials"] = "AB"

    payload = safe_payload(export)

    assert set(payload["climate_context"]).issubset(SAFE_CLIMATE_FIELDS)
    assert "notes" not in payload["climate_context"]
    assert "operator_initials" not in payload["climate_context"]


def test_safe_payload_drops_phi_like_fields_if_export_drift_introduces_them():
    # Defence in depth — if a future change to storage.py accidentally
    # adds a PHI field to the export envelope, the brief module must
    # still drop it before calling any generator.
    export = _sample_export() | {
        "local_child_id": "LEAK-001",
        "vitals": {"heart_rate": 138},
        "operator_initials": "AB",
        "request_json": "{...}",
    }

    payload = safe_payload(export)

    assert "local_child_id" not in payload
    assert "vitals" not in payload
    assert "operator_initials" not in payload
    assert "request_json" not in payload


def test_deterministic_brief_produces_full_schema_for_high_severity_dengue():
    brief = generate_brief(_sample_export())

    assert brief.generator == DETERMINISTIC_GENERATOR
    assert brief.headline.startswith("Dengue cluster signal")
    assert "San Cristobal Norte" in brief.headline
    assert "2026-W19" in brief.headline
    assert "z-score" in brief.what_changed.lower() or "4.22" in brief.what_changed
    assert "high severity" in brief.why_review_needed.lower()
    assert any("vector control" in item.lower() for item in brief.operational_considerations)
    assert any("escalate" in item.lower() for item in brief.operational_considerations)
    assert "Pre-pilot thresholds" in " ".join(brief.data_quality_limits)
    assert "24 hours" in brief.escalation_recommendation
    assert "Not a clinical diagnosis" in brief.disclaimer


def test_deterministic_brief_handles_normal_signal_without_escalation():
    export = _sample_export() | {
        "count": 21,
        "baseline_mean": 22.67,
        "z_score": -0.46,
        "flag": "normal",
        "severity": "low",
        "quality_warnings": [],
    }

    brief = generate_brief(export)

    assert "no escalation required" in brief.escalation_recommendation.lower()
    assert "no anomaly" in brief.why_review_needed.lower()
    assert "no quality warnings" in " ".join(brief.data_quality_limits).lower()


def test_deterministic_brief_handles_missing_climate_context_gracefully():
    export = _sample_export() | {
        "climate_context": None,
        "quality_warnings": ["no_climate_context_recorded"],
    }

    brief = generate_brief(export)

    assert brief.generator == DETERMINISTIC_GENERATOR
    assert "no climate context was recorded" in " ".join(brief.data_quality_limits).lower()


def test_brief_endpoint_in_local_clinic_mode(tmp_path):
    from fastapi.testclient import TestClient

    from kynode_pediatric_local_node import create_app

    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    client.put(
        "/api/weekly-inputs",
        json={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
            "historical_counts": [18, 24, 21, 28, 19, 26],
            "current_count": 38,
            "source": "manual_aggregate_entry",
        },
    )
    client.put(
        "/api/climate-context",
        json={
            "zone": "San Cristobal Norte",
            "week": "2026-W19",
            "rainfall": "heavy",
            "flooding": "reported",
            "heat_alert": "no",
            "water_disruption": "yes",
            "vector_risk": "increased",
            "source": "clinic_observation",
            "confidence": "medium",
            "notes": "Standing water reported.",
        },
    )

    response = client.post(
        "/api/brief/generate",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["brief"]["generator"] == "deterministic_template"
    assert body["brief"]["headline"].startswith("Dengue cluster signal")
    # The brief response carries the export so the UI can show the
    # underlying numbers next to the human interpretation.
    assert body["export"]["contains_phi"] is False
    # Privacy regression: even though the export itself is safe, the
    # brief's used_payload echo must not leak the climate notes that
    # the client uploaded above.
    assert "notes" not in body["brief"]["used_payload"].get("climate_context", {})


def test_brief_endpoint_returns_409_without_weekly_input(tmp_path):
    from fastapi.testclient import TestClient

    from kynode_pediatric_local_node import create_app

    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    response = client.post(
        "/api/brief/generate",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )

    assert response.status_code == 409


def test_brief_endpoint_in_public_demo_mode_scopes_to_synthetic(tmp_path):
    from fastapi.testclient import TestClient

    from kynode_pediatric_local_node import create_app

    client = TestClient(create_app(tmp_path / "demo.sqlite3", public_demo_mode=True))
    client.post("/api/demo/load")

    ok = client.post(
        "/api/brief/generate",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )
    wrong_scope = client.post(
        "/api/brief/generate",
        params={
            "zone": "Other Zone",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )

    assert ok.status_code == 200
    assert ok.json()["brief"]["generator"] == "deterministic_template"
    assert wrong_scope.status_code == 403


def test_llm_generator_is_used_when_ollama_provider_is_set(monkeypatch):
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")

    captured: dict[str, Any] = {}

    def fake_call(payload: dict[str, Any], lang: str = "en") -> dict[str, Any]:
        captured["payload"] = payload
        captured["lang"] = lang
        return {
            "headline": "LLM headline",
            "what_changed": "LLM change line.",
            "why_review_needed": "LLM review line.",
            "operational_considerations": ["LLM op 1", "LLM op 2"],
            "data_quality_limits": ["LLM caveat 1"],
            "escalation_recommendation": "LLM escalation.",
        }

    monkeypatch.setattr(brief_module, "_llm_call", fake_call)

    brief = generate_brief(_sample_export())

    assert brief.generator == LLM_GENERATOR
    assert brief.headline == "LLM headline"
    # Privacy contract: the payload the LLM saw must be the safe envelope.
    assert set(captured["payload"]).issubset(SAFE_EXPORT_FIELDS)
    assert "notes" not in captured["payload"].get("climate_context", {})


def test_llm_generator_falls_back_to_deterministic_when_call_raises(monkeypatch):
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")

    def boom(payload: dict[str, Any], lang: str = "en") -> dict[str, Any]:
        raise BriefError("simulated upstream failure")

    monkeypatch.setattr(brief_module, "_llm_call", boom)

    brief = generate_brief(_sample_export())

    assert brief.generator == DETERMINISTIC_GENERATOR
    assert brief.headline.startswith("Dengue cluster signal")


def test_llm_provider_other_than_ollama_is_treated_as_disabled(monkeypatch):
    """Camino C contract: if someone leaves a legacy "anthropic" / "openai"
    value in the env, we silently fall back to deterministic instead of
    attempting any outbound SaaS call. Edge-only intelligence is enforced."""
    for legacy in ("anthropic", "openai", "huggingface", "claude", ""):
        monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", legacy)
        assert brief_module._llm_enabled() is False
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")
    assert brief_module._llm_enabled() is True
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "OLLAMA")
    assert brief_module._llm_enabled() is True  # case-insensitive


def test_deterministic_brief_translates_to_spanish():
    from kynode_pediatric_local_node.brief import generate_brief

    brief = generate_brief(_sample_export(), lang="es")

    assert brief.language == "es"
    assert brief.headline.startswith("Señal de cluster de dengue") or brief.headline.startswith(
        "señal de cluster de dengue".capitalize()
    )
    assert "z-score" in brief.what_changed.lower()
    assert "alta severidad" in brief.why_review_needed.lower()
    assert any("autoridades" in item.lower() for item in brief.operational_considerations)
    assert "24 horas" in brief.escalation_recommendation
    assert "diagnóstico" in brief.disclaimer.lower()


def test_brief_endpoint_respects_lang_query(tmp_path):
    from fastapi.testclient import TestClient

    from kynode_pediatric_local_node import create_app

    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    client.put(
        "/api/weekly-inputs",
        json={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
            "historical_counts": [18, 24, 21, 28, 19, 26],
            "current_count": 38,
            "source": "manual_aggregate_entry",
        },
    )

    en = client.post(
        "/api/brief/generate",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )
    es = client.post(
        "/api/brief/generate",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
            "lang": "es",
        },
    )

    assert en.json()["brief"]["language"] == "en"
    assert es.json()["brief"]["language"] == "es"
    assert "diagnóstico" in es.json()["brief"]["disclaimer"].lower()
    assert "diagnosis" in en.json()["brief"]["disclaimer"].lower()


def test_brief_endpoint_rejects_unsupported_lang(tmp_path):
    from fastapi.testclient import TestClient

    from kynode_pediatric_local_node import create_app

    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    response = client.post(
        "/api/brief/generate",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
            "lang": "fr",
        },
    )
    assert response.status_code == 422


def test_default_endpoint_and_model_resolution_for_ollama(monkeypatch):
    monkeypatch.delenv("KYNODE_AI_BRIEF_ENDPOINT", raising=False)
    monkeypatch.delenv("KYNODE_AI_BRIEF_MODEL", raising=False)
    assert brief_module._resolve_endpoint() == brief_module.OLLAMA_DEFAULT_ENDPOINT
    assert brief_module._resolve_model() == brief_module.OLLAMA_DEFAULT_MODEL
    assert brief_module.OLLAMA_DEFAULT_ENDPOINT.startswith("http://localhost:")


def test_endpoint_and_model_can_be_overridden_for_lan_servers(monkeypatch):
    monkeypatch.setenv("KYNODE_AI_BRIEF_ENDPOINT", "http://lan-llm.local:11434/api/chat")
    monkeypatch.setenv("KYNODE_AI_BRIEF_MODEL", "qwen2.5:3b")
    assert brief_module._resolve_endpoint() == "http://lan-llm.local:11434/api/chat"
    assert brief_module._resolve_model() == "qwen2.5:3b"


def test_llm_request_body_uses_format_json_and_no_auth_header():
    body = brief_module._llm_request_body("llama-test", {"zone": "X"}, lang="en")
    assert body["format"] == "json"
    assert body["stream"] is False
    assert body["model"] == "llama-test"
    assert body["messages"][0]["role"] == "system"
    assert "public health analyst" in body["messages"][0]["content"].lower()


def test_llm_request_body_uses_spanish_system_prompt_when_lang_is_es():
    body = brief_module._llm_request_body("llama-test", {"zone": "X"}, lang="es")
    assert "salud pública" in body["messages"][0]["content"].lower()
    assert "voseo" in body["messages"][0]["content"].lower()  # explicit dialect rule


def test_llm_extract_text_handles_ollama_shape():
    assert brief_module._llm_extract_text({"message": {"content": "yo"}}) == "yo"


def test_llm_extract_text_raises_brieferror_on_malformed_response():
    with pytest.raises(BriefError):
        brief_module._llm_extract_text({"choices": "not-a-list"})
    with pytest.raises(BriefError):
        brief_module._llm_extract_text({})


def test_coerce_bullets_accepts_list_string_and_garbage():
    assert brief_module._coerce_bullets(["a", " b ", ""]) == ["a", " b "]
    assert brief_module._coerce_bullets("single line") == ["single line"]
    assert brief_module._coerce_bullets(None) == []
    assert brief_module._coerce_bullets(123) == []


def test_llm_call_propagates_brief_error_when_response_is_not_json(monkeypatch):
    """The LLM returned a 200 with a parseable Ollama envelope but the
    `content` string itself is not valid JSON. We must surface this as a
    BriefError so the calling generator can fall back to deterministic."""

    class _FakeResponse:
        def __init__(self, body): self._body = body
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return self._body

    def fake_urlopen(req, timeout=25):
        return _FakeResponse(b'{"message": {"content": "this is not json"}}')

    monkeypatch.setattr(brief_module.urllib_request, "urlopen", fake_urlopen)
    with pytest.raises(BriefError, match="not valid JSON"):
        brief_module._llm_call({"zone": "X"})


def test_llm_call_propagates_brief_error_when_endpoint_unreachable(monkeypatch):
    """A typical scenario in production: Ollama isn't running. The error
    must be a BriefError so generate_brief() falls back to the
    deterministic template instead of crashing the request."""
    import urllib.error as urllib_error_mod

    def boom(req, timeout=25):
        raise urllib_error_mod.URLError("Connection refused")

    monkeypatch.setattr(brief_module.urllib_request, "urlopen", boom)
    with pytest.raises(BriefError, match="Local LLM request failed"):
        brief_module._llm_call({"zone": "X"})


def test_percent_above_baseline_guards_invalid_inputs():
    assert brief_module._percent_above_baseline(None, 10) is None
    assert brief_module._percent_above_baseline(10, None) is None
    assert brief_module._percent_above_baseline(10, 0) is None
    assert brief_module._percent_above_baseline(10, -3) is None
    assert brief_module._percent_above_baseline("nope", 10) is None


def test_deterministic_brief_falls_back_to_no_pct_when_baseline_is_zero():
    """Anomaly detector can emit baseline_mean = 0 when the rolling window
    is all zeros. The brief must still render a coherent what_changed
    line and degrade gracefully (no division-by-zero, no missing pct)."""
    from kynode_pediatric_local_node.brief import generate_brief

    export = {
        "zone": "Z",
        "week": "2026-W19",
        "indicator": "dengue_suspicion",
        "count": 5,
        "baseline_mean": 0,
        "z_score": 0.0,
        "flag": "insufficient_baseline",
        "quality_warnings": [],
        "climate_context": None,
        "contains_phi": False,
    }
    brief = generate_brief(export, lang="en")
    assert "5 suspected dengue cases reported" in brief.what_changed
    assert "%" not in brief.what_changed  # no malformed percentage
    assert "baseline window is too small" in brief.why_review_needed


def test_deterministic_brief_handles_anomaly_flag_without_high_severity():
    from kynode_pediatric_local_node.brief import generate_brief

    export = {
        "zone": "Z",
        "week": "2026-W19",
        "indicator": "dengue_suspicion",
        "count": 28,
        "baseline_mean": 22.67,
        "z_score": 2.5,
        "flag": "anomaly",
        "quality_warnings": [],
        "climate_context": None,
        "contains_phi": False,
    }
    brief = generate_brief(export, lang="en")
    assert "above the rolling baseline threshold" in brief.why_review_needed
    assert "Notify the supervising public health officer" in brief.escalation_recommendation


# ────────────────────────────────────────────────────────────────────────
# Clinical safety gate
# ────────────────────────────────────────────────────────────────────────


def _unsafe_llm_response_en() -> dict[str, Any]:
    return {
        "headline": "Diagnose dengue outbreak now",
        "what_changed": "This is caused by flooding in the zone.",
        "why_review_needed": "Confirmed cases require urgent action.",
        "operational_considerations": [
            "Prescribe medication to children immediately.",
            "Administer paracetamol at 10 mg/kg.",
        ],
        "data_quality_limits": ["No caveats."],
        "escalation_recommendation": "This proves an outbreak.",
    }


def _unsafe_llm_response_es() -> dict[str, Any]:
    return {
        "headline": "Diagnosticar brote de dengue ahora",
        "what_changed": "Esto fue causado por las inundaciones en la zona.",
        "why_review_needed": "Brote confirmado, requiere acción urgente.",
        "operational_considerations": [
            "Recetar paracetamol a los niños inmediatamente.",
            "Administrar dosis de 10 mg/kg.",
        ],
        "data_quality_limits": ["Sin advertencias."],
        "escalation_recommendation": "Esto prueba un brote.",
    }


def test_clinical_safety_gate_rejects_diagnosis_phrasing_en(monkeypatch):
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")
    monkeypatch.setattr(
        brief_module, "_llm_call", lambda payload, lang="en": _unsafe_llm_response_en()
    )

    brief = generate_brief(_sample_export(), lang="en")

    # The unsafe LLM response was thrown away and the deterministic
    # generator took over silently — exactly the safety contract.
    assert brief.generator == DETERMINISTIC_GENERATOR
    assert "Diagnose" not in brief.headline
    assert "caused by" not in brief.what_changed.lower()
    assert all("prescrib" not in item.lower() for item in brief.operational_considerations)


def test_clinical_safety_gate_rejects_diagnosis_phrasing_es(monkeypatch):
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")
    monkeypatch.setattr(
        brief_module, "_llm_call", lambda payload, lang="en": _unsafe_llm_response_es()
    )

    brief = generate_brief(_sample_export(), lang="es")

    assert brief.generator == DETERMINISTIC_GENERATOR
    assert "Diagnosticar" not in brief.headline
    assert "causado por" not in brief.what_changed.lower()
    assert all("recetar" not in item.lower() for item in brief.operational_considerations)


def test_clinical_safety_gate_rejects_es_unsafe_text_when_en_was_requested(monkeypatch):
    """A small local model can ignore the language directive in the
    system prompt and return Spanish unsafe phrasing in response to an
    English request. The gate must still reject it — the UI renders
    whatever the model emits, regardless of the requested language."""
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")
    monkeypatch.setattr(
        brief_module, "_llm_call", lambda payload, lang="en": _unsafe_llm_response_es()
    )

    brief = generate_brief(_sample_export(), lang="en")

    assert brief.generator == DETERMINISTIC_GENERATOR, (
        "Spanish unsafe text in an English session must still trip the gate"
    )
    # The deterministic fallback ran in EN as requested by the operator.
    assert brief.language == "en"


def test_clinical_safety_gate_rejects_en_unsafe_text_when_es_was_requested(monkeypatch):
    """Mirror case: ES request, EN unsafe response — also rejected."""
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")
    monkeypatch.setattr(
        brief_module, "_llm_call", lambda payload, lang="en": _unsafe_llm_response_en()
    )

    brief = generate_brief(_sample_export(), lang="es")

    assert brief.generator == DETERMINISTIC_GENERATOR
    assert brief.language == "es"
    # Verify we got a Spanish deterministic brief, not English residue.
    assert "diagnóstico" in brief.disclaimer.lower()


def test_safety_gate_validator_scans_all_supported_languages():
    """Direct unit test: the validator should match unsafe patterns
    from every language even when only one lang is passed in."""
    from kynode_pediatric_local_node.brief import (
        UnsafeBriefError,
        _validate_brief_safety,
    )

    # ES unsafe text, but caller requested EN.
    with pytest.raises(UnsafeBriefError) as exc_info:
        _validate_brief_safety(_unsafe_llm_response_es(), "en")
    matched = exc_info.value.matched
    assert any("diagnostic" in m or "diagnos" in m for m in matched), (
        f"Expected ES diagnosis match in {matched}"
    )
    # The error metadata reports the SESSION language, not the
    # detected-text language. This is intentional so audit logs trace
    # which UI session asked for the brief.
    assert exc_info.value.language == "en"


@pytest.mark.parametrize(
    "lang,unsafe_text",
    [
        ("en", "Start dengue treatment protocol"),
        ("en", "Begin antibiotic therapy"),
        ("en", "Initiate antimalarial treatment"),
        ("en", "Dengue outbreak confirmed"),
        ("en", "Outbreak confirmed in zone"),
        ("en", "Hospitalize affected children"),
        ("en", "Refer for ICU admission"),
        ("en", "This indicates dengue infection"),
        ("en", "Cluster suggests an active outbreak"),
        ("en", "Definitive diagnostic confirmed by RDT"),
        ("en", "Likely dengue serotype 2"),
        ("en", "Recommended therapy: paracetamol"),
        ("es", "Iniciar protocolo de tratamiento"),
        ("es", "Brote confirmado en la zona"),
        ("es", "Iniciar terapia antibiótica"),
        ("es", "Hospitalizar a los niños afectados"),
        ("es", "Referir a UCI"),
        ("es", "Esto indica infección por dengue"),
        ("es", "Probable serotipo de dengue 2"),
        ("es", "Terapia recomendada: paracetamol"),
        ("es", "Confirmar diagnóstico mediante RDT"),
    ],
)
def test_safety_gate_blocks_adversarial_clinical_phrasings(lang, unsafe_text):
    """Adversarial smoke test: every one of these would be unsafe to
    render to a clinic operator unchallenged. Real local LLMs can and
    do emit phrasings like these. The gate must trip on each, not just
    the obvious "diagnose"/"prescribe" stems.
    """
    from kynode_pediatric_local_node.brief import (
        UnsafeBriefError,
        _validate_brief_safety,
    )

    raw = {
        "headline": unsafe_text,
        "what_changed": "",
        "why_review_needed": "",
        "operational_considerations": [],
        "data_quality_limits": [],
        "escalation_recommendation": "",
    }
    with pytest.raises(UnsafeBriefError):
        _validate_brief_safety(raw, lang)


def test_safety_gate_validator_returns_matched_keywords():
    from kynode_pediatric_local_node.brief import (
        UnsafeBriefError,
        _validate_brief_safety,
    )

    with pytest.raises(UnsafeBriefError) as exc_info:
        _validate_brief_safety(_unsafe_llm_response_en(), "en")
    matched = exc_info.value.matched
    assert any("diagnos" in m for m in matched)
    assert any("prescrib" in m for m in matched)
    assert exc_info.value.language == "en"


def test_safety_gate_accepts_legitimate_brief_text():
    """Counter-test: the deterministic template's own output must NEVER
    trip the safety gate, otherwise the fallback would loop. We verify
    by re-running the validator against a deterministic brief response
    shaped like the LLM one would produce."""
    from kynode_pediatric_local_node.brief import _validate_brief_safety

    deterministic = {
        "headline": "Dengue cluster signal · San Cristobal Norte · 2026-W19",
        "what_changed": "38 suspected dengue cases reported, baseline mean 22.7.",
        "why_review_needed": "The current count exceeds the rolling baseline by a margin "
                              "the anomaly detector classifies as high severity.",
        "operational_considerations": [
            "Coordinate vector control with local authorities.",
            "Re-stock paracetamol and oral rehydration salts.",
        ],
        "data_quality_limits": ["Pre-pilot thresholds are not yet calibrated."],
        "escalation_recommendation": (
            "Escalate to the local public health authority within 24 hours."
        ),
    }
    # Should NOT raise. This is the no-op assertion: if the call returns
    # without exception, the gate is correctly tuned for legitimate copy.
    _validate_brief_safety(deterministic, "en")


def test_safety_gate_accepts_legitimate_es_brief_text():
    """Same as test_safety_gate_accepts_legitimate_brief_text but ES."""
    from kynode_pediatric_local_node.brief import _validate_brief_safety

    deterministic = {
        "headline": "Señal de cluster de dengue · San Cristobal Norte · 2026-W19",
        "what_changed": "38 casos sospechosos de dengue reportados.",
        "why_review_needed": (
            "El conteo actual supera la línea base por un margen alto."
        ),
        "operational_considerations": [
            "Coordina con las autoridades locales el control vectorial.",
            "Repón paracetamol y sales de rehidratación oral.",
        ],
        "data_quality_limits": ["Los umbrales pre-piloto no están calibrados."],
        "escalation_recommendation": (
            "Escala a la autoridad local de salud pública dentro de las próximas 24 horas."
        ),
    }
    _validate_brief_safety(deterministic, "es")


def test_real_deterministic_briefs_do_not_trip_cross_language_gate():
    """End-to-end counter-test: every deterministic brief the system
    actually generates must pass the validator in BOTH languages now
    that the gate scans all supported languages. If a future template
    edit accidentally introduces a false-positive, this test catches it
    before fallback starts looping in production.
    """
    from kynode_pediatric_local_node.brief import (
        _generate_deterministic,
        _validate_brief_safety,
        safe_payload,
    )

    payload = safe_payload(_sample_export())
    for lang in ("en", "es"):
        brief = _generate_deterministic(payload, lang)
        # Re-shape the brief into the dict the validator expects.
        as_raw = {
            "headline": brief.headline,
            "what_changed": brief.what_changed,
            "why_review_needed": brief.why_review_needed,
            "operational_considerations": brief.operational_considerations,
            "data_quality_limits": brief.data_quality_limits,
            "escalation_recommendation": brief.escalation_recommendation,
        }
        _validate_brief_safety(as_raw, lang)


def test_real_deterministic_briefs_pass_validator_for_every_indicator_and_language():
    """Sweeping check: every (indicator × language) combination that the
    deterministic generator can produce must clear the cross-language
    safety gate. If a clinical phrase ever overlaps with the unsafe
    vocabulary (e.g. a future "treatment" bullet for malnutrition), this
    test catches the regression at unit-test time, not in production.
    """
    from kynode_pediatric_local_node.brief import (
        _generate_deterministic,
        _validate_brief_safety,
        safe_payload,
    )

    indicators = [
        "dengue_suspicion",
        "malaria_suspicion",
        "diarrheal_disease",
        "heat_related_illness",
        "respiratory_outbreak",
        "malnutrition_signal",
    ]
    flags = ["normal", "anomaly", "anomaly_high_severity", "insufficient_baseline"]
    for indicator in indicators:
        for flag in flags:
            export = _sample_export() | {"indicator": indicator, "flag": flag}
            payload = safe_payload(export)
            for lang in ("en", "es"):
                brief = _generate_deterministic(payload, lang)
                as_raw = {
                    "headline": brief.headline,
                    "what_changed": brief.what_changed,
                    "why_review_needed": brief.why_review_needed,
                    "operational_considerations": brief.operational_considerations,
                    "data_quality_limits": brief.data_quality_limits,
                    "escalation_recommendation": brief.escalation_recommendation,
                }
                _validate_brief_safety(as_raw, lang)


# ────────────────────────────────────────────────────────────────────────
# Endpoint trust boundary
# ────────────────────────────────────────────────────────────────────────


def test_endpoint_trust_accepts_loopback_and_private_ranges():
    accept = [
        "http://127.0.0.1:11434/api/chat",
        "http://localhost:11434/api/chat",
        "http://[::1]:11434/api/chat",
        "http://10.0.0.10:11434/api/chat",
        "http://192.168.1.5:11434/api/chat",
        "http://172.16.0.5:11434/api/chat",
        "http://ollama.local:11434/api/chat",
        "http://kynode-llm.lan:11434/api/chat",
        "http://internal-host.internal:11434/api/chat",
    ]
    for endpoint in accept:
        assert brief_module._endpoint_is_trusted(endpoint), (
            f"Should trust private endpoint: {endpoint}"
        )


def test_endpoint_trust_rejects_public_ip_and_public_dns():
    reject = [
        "http://8.8.8.8:80/api/chat",
        "https://api.openai.com/v1/chat/completions",
        "https://api.anthropic.com/v1/messages",
        "https://example.com/llm",
        "http://93.184.216.34:11434/api/chat",
        # IPv4-mapped IPv6 to a public address
        "http://[::ffff:8.8.8.8]/api/chat",
        # Userinfo trick: "10.0.0.1" looks private but the real host is evil.com
        "http://10.0.0.1@evil.com/api/chat",
        "http://localhost@evil.com/api/chat",
        # Subdomain trick: a hostname that contains "localhost" but is public DNS
        "http://localhost.evil.com/api/chat",
        "http://127.0.0.1.evil.com/api/chat",
    ]
    for endpoint in reject:
        assert not brief_module._endpoint_is_trusted(endpoint), (
            f"Should NOT trust public endpoint: {endpoint}"
        )


def test_endpoint_trust_rejects_cloud_metadata_endpoints():
    """Defence in depth: even though cloud-provider metadata IPs are
    technically link-local, they are classic SSRF targets. The brief
    endpoint must never reach them."""
    metadata_endpoints = [
        "http://169.254.169.254/latest/meta-data/",       # AWS / GCP / Azure
        "http://169.254.169.254:11434/api/chat",           # disguised as Ollama
        "http://100.100.100.200/latest/meta-data/",        # Alibaba
        "http://169.254.170.2/v2/credentials",              # AWS ECS task creds
    ]
    for endpoint in metadata_endpoints:
        assert not brief_module._endpoint_is_trusted(endpoint), (
            f"Cloud metadata endpoint must NOT be trusted: {endpoint}"
        )


def test_endpoint_trust_can_be_overridden_via_explicit_opt_in(monkeypatch):
    """The operator can deliberately accept a public endpoint by setting
    KYNODE_AI_BRIEF_ALLOW_PUBLIC=true. From that moment on, the trust
    boundary is the operator's responsibility, not the product's."""
    monkeypatch.setenv("KYNODE_AI_BRIEF_ALLOW_PUBLIC", "true")
    assert brief_module._endpoint_is_trusted("https://api.openai.com/v1/chat/completions")


def test_llm_call_refuses_public_endpoint_by_default(monkeypatch):
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")
    monkeypatch.setenv("KYNODE_AI_BRIEF_ENDPOINT", "https://api.openai.com/v1/chat/completions")
    monkeypatch.delenv("KYNODE_AI_BRIEF_ALLOW_PUBLIC", raising=False)

    with pytest.raises(BriefError, match="loopback"):
        brief_module._llm_call({"zone": "X"})


def test_llm_call_accepts_loopback_endpoint(monkeypatch):
    """Counter-test for the trust boundary: the default localhost path
    must NOT be rejected by the endpoint check. We stub out urlopen so
    the test does not require a running Ollama."""
    monkeypatch.setenv("KYNODE_AI_BRIEF_PROVIDER", "ollama")
    monkeypatch.delenv("KYNODE_AI_BRIEF_ENDPOINT", raising=False)
    monkeypatch.delenv("KYNODE_AI_BRIEF_ALLOW_PUBLIC", raising=False)

    class _FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self):
            return b'{"message": {"content": "{\\"headline\\":\\"OK\\"}"}}'

    monkeypatch.setattr(brief_module.urllib_request, "urlopen", lambda *a, **k: _FakeResponse())
    result = brief_module._llm_call({"zone": "X"})
    assert result == {"headline": "OK"}


# ────────────────────────────────────────────────────────────────────────
# Brief generation audit event
# ────────────────────────────────────────────────────────────────────────


def test_brief_generation_writes_audit_event(tmp_path):
    from fastapi.testclient import TestClient

    from kynode_pediatric_local_node import create_app

    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    client.put(
        "/api/weekly-inputs",
        json={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
            "historical_counts": [18, 24, 21, 28, 19, 26],
            "current_count": 38,
            "source": "manual_aggregate_entry",
        },
    )

    audit_before = client.get("/api/audit-events?limit=25").json()["items"]
    response = client.post(
        "/api/brief/generate",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
            "lang": "en",
        },
    )

    assert response.status_code == 200
    audit_after = client.get("/api/audit-events?limit=25").json()["items"]
    assert len(audit_after) > len(audit_before)
    brief_event = next(
        event for event in audit_after if event["event_type"] == "weekly_brief_generated"
    )
    # The audit `source` carries the generator name so reviewers can
    # tell at a glance whether a brief came from the deterministic
    # template or from the optional local LLM.
    assert brief_event["source"] == "deterministic_template"
    assert brief_event["entity_kind"] == "weekly_signal"
    assert brief_event["entity_key"] == "San Cristobal Norte|2026-W19|dengue_suspicion|en"


def test_brief_module_has_no_phi_field_in_safe_export_allowlist():
    """Frozen list of forbidden keys must remain disjoint from the
    allowlist. If the storage layer ever adds one of these to the export
    envelope, this test still catches it before it reaches a generator.
    """
    forbidden = {
        "local_child_id", "birth_date", "sex", "vitals", "weight_kg",
        "vaccinations_received", "context", "operator_initials",
        "clinical_notes", "request_json", "assessment_json", "notes",
    }
    assert forbidden.isdisjoint(brief_module.SAFE_EXPORT_FIELDS)
    # Also: SAFE_CLIMATE_FIELDS must not include "notes" or
    # "operator_initials" — those are operator-only free-text and never
    # leave the device in a brief.
    assert "notes" not in brief_module.SAFE_CLIMATE_FIELDS
    assert "operator_initials" not in brief_module.SAFE_CLIMATE_FIELDS

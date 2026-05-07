# KYNODE Pediatric Local Node

The Local Node is the pre-pilot product surface for KYNODE Pediatric.

It is designed as a small offline clinic node:

1. Capture a pediatric encounter inside the clinic.
2. Run deterministic local support calculations.
3. Save the encounter in local SQLite storage.
4. Record weekly aggregate counts by zone and indicator.
5. Record structured weekly climate context.
6. Generate a transparent statistical signal.
7. Prepare an aggregate JSON export without PHI.
8. Render a plain-language surveillance brief over that aggregate export — deterministic by default, optionally enhanced by a local LLM (Ollama) running on the same machine or inside the clinic LAN.

## Product Position

KYNODE Pediatric is an offline pediatric climate-health surveillance layer built from the point of care.

The important boundary is not visual polish. The important boundary is data separation:

- Patient-level data remains local.
- Weekly aggregate signal is entered separately.
- Climate context is structured by zone/week.
- Export contains aggregate count and structured context only.

## Climate Context

No external weather API is used in v0.2. Climate context is entered locally once per zone/week.

Fields:

- rainfall: `none`, `light`, `moderate`, `heavy`, `unknown`;
- flooding: `no`, `reported`, `unknown`;
- heat alert: `no`, `yes`, `unknown`;
- water disruption: `no`, `yes`, `unknown`;
- vector risk: `normal`, `increased`, `unknown`;
- source: `clinic_observation`, `community_report`, `authority_bulletin`, `other`;
- confidence: `low`, `medium`, `high`.

Confidence means:

- `low`: single observation, no corroboration;
- `medium`: multiple observations or corroborated by community;
- `high`: corroborated by official authority bulletin.

The system does not claim climate causality and does not predict weather.

## Export Contract

The export endpoint returns `409` until weekly aggregate input exists. Missing climate context does not block export; it adds the warning `no_climate_context_recorded`.

Exported JSON removes:

- local child ID;
- birth date;
- vitals;
- growth measurements;
- vaccination details;
- clinical notes;
- climate notes;
- operator initials.

## Surveillance Brief

After preparing the aggregate export, the operator can press **Generate brief** on the Surveillance page. The endpoint `POST /api/brief/generate?zone=…&indicator=…&week=…&lang=en|es` re-fetches the privacy-bounded export and renders a structured brief: headline, what changed, why review is needed, operational considerations, data-quality limits, escalation recommendation. Two interchangeable generators sit behind the same schema:

- `deterministic_template` (default, always offline) — rule-based render driven by the aggregate signal and the structured climate context. No model uncertainty.
- `llm_brief_v1` (opt-in via `KYNODE_AI_BRIEF_PROVIDER=ollama`) — local LLM through Ollama or any Ollama-compatible server inside the clinic LAN. The endpoint is enforced to a private network by default; an explicit `KYNODE_AI_BRIEF_ALLOW_PUBLIC=true` is required before the call layer will dial out to a non-private host.

A clinical safety gate runs on the LLM output (EN + ES patterns scanned together, regardless of the requested UI language) and rejects diagnosis, prescription, treatment-protocol, dose, causal-claim and confirmed-outbreak phrasing. Rejected output is silently replaced by the deterministic generator. Every generated brief — by either path — writes a `weekly_brief_generated` audit row whose `source` column carries the generator name (`deterministic_template` or `llm_brief_v1`), so reviewers can trace which path produced each brief.

Configuration and Ollama setup are documented in [docs/integrations/ollama.md](../integrations/ollama.md) (Spanish: [ollama.es.md](../integrations/ollama.es.md)).

## What Exists In v0.2.0 Pre-Pilot

- FastAPI local service.
- SQLite local storage.
- Bilingual HTML/CSS/vanilla JS UI.
- Explicit synthetic walkthrough.
- Local assessment endpoint using the four alpha packages.
- Weekly aggregate signal input.
- Weekly climate context.
- Audit trail without PHI fields.
- Privacy-bounded aggregate export endpoint.
- Surveillance brief endpoint with deterministic default and opt-in local LLM (Ollama) — clinical safety gate, endpoint trust boundary and `weekly_brief_generated` audit event included.

## What Remains Grant-Funded Work

- Role-based access.
- Full offline sync with KYNODE edge.
- Full WHO IMCI rule coverage.
- Institutional export adapters.
- Field validation and threshold calibration with real aggregate data.
- Training materials for community health workers.

# Changelog

## v0.2.0-prepilot-local-node — 2026-05-06

Pre-pilot product release for the KYNODE Pediatric Local Node.

### Added

- Offline FastAPI clinic node under `apps/local-node/`.
- SQLite local encounter storage with backup-and-recreate schema policy.
- Node settings, weekly aggregate inputs, weekly climate context and local audit tables.
- Bilingual HTML/CSS/vanilla JS clinic UI (Inter Variable subset, shared design tokens, light/dark theme).
- Clinic mode as the default; no synthetic data loads silently.
- Explicit synthetic walkthrough mode with `synthetic_demo` source tagging.
- Public demo mode (`KYNODE_PUBLIC_DEMO_MODE=true`) for shareable hosted reviews — server resets the SQLite, locks all manual writes, exposes only the synthetic walkthrough flow.
- Local assessment flow composing the four alpha packages.
- Aggregate signal generation from weekly input only.
- Privacy-bounded weekly aggregate export endpoint with quality warnings + privacy checklist.
- Static-asset privacy denylist for SQLite/DB files under `/static/`.
- Gzip + immutable static cache headers.
- AI surveillance brief layer over the privacy-bounded weekly export (`POST /api/brief/generate`) with two interchangeable generators behind a single schema: a deterministic rule-based template (default, always offline) and an opt-in local LLM path that talks to Ollama on `localhost:11434` or any Ollama-compatible server inside the clinic LAN.
- Endpoint trust boundary: the brief LLM call refuses any non-loopback / non-private endpoint by default; the operator must explicitly set `KYNODE_AI_BRIEF_ALLOW_PUBLIC=true` to opt in to a public host. No hosted SaaS API is ever called by the product code.
- Clinical safety gate post-LLM: if the local model produces text containing diagnosis, prescription, treatment, dosing or causal-claim phrasing, the LLM output is discarded and the deterministic generator runs instead. The gate scans every supported language regardless of the requested UI language so a small local model that answers in the wrong tongue is still caught. The audit row records which generator actually produced the brief.
- Brief generation audit event (`weekly_brief_generated`) records the generator name in `source` so reviewers can trace whether each brief came from the deterministic template or the local LLM path.
- Bilingual (EN/ES) brief output with a stable `AggregateBrief` schema, a chip indicating which generator produced the brief, and a clinical disclaimer that follows it.
- `safe_payload()` chokepoint and `SAFE_EXPORT_FIELDS` allowlist guarantee zero PHI ever reaches the brief generator (deterministic or LLM).
- Optional Ollama integration documented at `docs/integrations/ollama.{md,es.md}` with install, model selection, LAN deployment, troubleshooting and removal steps.
- 184 tests, 95% coverage on `apps/local-node/` (97% on `brief.py`).

### Changed

- Assessment payloads no longer accept weekly baseline/current counts.
- Weekly surveillance input is a separate workflow from pediatric intake.
- Climate context is structured local observation by zone/week. No weather API, no causal attribution.

### Safety boundary

- Patient-level data stays on the device.
- Weekly export is aggregate-only and excludes operator initials and free-text notes.
- Audit schema records operational events only; never patient identifiers.
- Statistical support only. No autonomous diagnosis.

## v0.1.0-pregrant-alpha — 2026-05-04

This release is prepared for the UNICEF Climate & Health 2026 application.

### Added

- Standalone `growth-curves` package.
- Standalone `triage-ranges` package.
- Standalone `anomaly-detection` package.
- Standalone `vaccinations` package.
- Bilingual static demo under `demo/`.
- GitHub Actions CI workflow with coverage gate.
- GitHub Pages workflow for the demo.
- Component specs for growth curves, vaccinations and planned IMCI rules.

### Notes

- Demo data is synthetic.
- The alpha is not field-use validated clinical software.
- The IMCI rules package is planned but not shipped in this alpha.

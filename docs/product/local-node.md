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

## What Remains Grant-Funded Work

- Role-based access.
- Full offline sync with KYNODE edge.
- Full WHO IMCI rule coverage.
- Institutional export adapters.
- Field validation and threshold calibration with real aggregate data.
- Training materials for community health workers.

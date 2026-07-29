# Try the full synthetic flow

The hosted [KYNODE Pediatric Local Node](https://pediatric.kynode.io/) is a
public, synthetic-only walkthrough. It refuses manual clinical writes and never
accepts real patient data.

The page loads the fixed walkthrough automatically. A red **Public demo** banner
stays visible throughout the flow.

## 1. Review the synthetic assessment

Open the **Home** view. The demo has already loaded the synthetic child,
measurements, vaccination history, zone and week, then run the deterministic
assessment.

Review the four output groups:

- age-banded pediatric triage flags;
- WHO growth status;
- vaccination schedule status;
- syndrome indicator preview.

These outputs support human review. They are not diagnoses or autonomous
clinical decisions.

## 2. Save the synthetic encounter

Select **Save synthetic encounter**.

Open **Records** and confirm that:

- the synthetic encounter appears in local history;
- an operational audit event is visible;
- the interface continues to identify the walkthrough as synthetic.

The hosted demo uses a resettable demo database. This is not evidence of a field
deployment or durable patient storage.

## 3. Generate the synthetic aggregate signal

Open **Surveillance**. The fixed synthetic weekly counts and structured climate
context are already loaded.

Select **Generate synthetic aggregate signal**. The result shows the current
count, rolling baseline, z-score, flag and severity. The anomaly detector is
transparent statistics, not an outbreak declaration.

## 4. Prepare the PHI-free export

Select **Prepare synthetic aggregate export**.

Expand **Technical JSON preview** and verify:

```json
{
  "signal_source": "synthetic_demo",
  "contains_phi": false
}
```

The full [Public synthetic export API](export-schema.md) documents every field.
The same fixed response can be inspected directly:

[`GET /api/export/weekly`](https://pediatric.kynode.io/api/export/weekly?zone=San%20Cristobal%20Norte&indicator=dengue_suspicion&week=2026-W19)

## 5. Generate the surveillance brief

Select **Generate brief**.

The default generator is a deterministic offline template. An operator running
the Local Node inside a clinic may optionally configure a local Ollama-compatible
model. Either path receives only the privacy-bounded aggregate export. The model
does not receive patient-level data and does not make clinical decisions.

## What this walkthrough proves

- The four alpha packages compose into one runnable product flow.
- The Local Node keeps encounter data separate from aggregate surveillance input.
- The public demo refuses real clinical writes.
- The weekly export is inspectable and carries `contains_phi: false`.
- The brief consumes the aggregate export after the privacy boundary.

## What it does not prove

- field or clinical validation;
- production synchronization;
- calibrated outbreak thresholds;
- institutional adapter readiness;
- health outcomes or live clinical activity.

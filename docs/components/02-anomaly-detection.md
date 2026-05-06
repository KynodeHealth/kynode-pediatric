# Anomaly detection

## What this does

Reads the stream of pediatric consultations happening at the clinic, aggregates them into weekly counts per zone and per indicator, and flags when a count diverges from its rolling baseline beyond a configurable threshold.

In plain language: when dengue cases climb in one zone the week after heavy rains, this is the package that notices and raises a flag — without waiting for the slow monthly reporting cycle that often arrives after the outbreak has already moved.

## Why it matters

The default surveillance loop in most low-resource settings goes like this: the clinic fills paper forms, someone aggregates them into a monthly spreadsheet, that spreadsheet gets emailed to a regional health office, and weeks later a national figure shows up in a quarterly report. By the time anyone above the clinic sees a spike, the outbreak has either resolved or spread to three more districts.

KYNODE Pediatric shortens this loop dramatically. The aggregation and detection happen on the same edge node where the consultations are recorded. The signal goes upstream as soon as the clinic gets connectivity again — even if that's days later, it's still much faster than a paper-based monthly cycle.

## Indicators tracked

This package consumes outputs from the other packages in the module:

- **Acute respiratory illness**: count from triage records flagged with respiratory danger signs (from `imci-rules`).
- **Dengue suspicion**: count from triage records flagged with dengue-pattern fever (from `imci-rules`).
- **Diarrheal disease / dehydration**: count from triage records flagged with dehydration danger signs.
- **Heat-related illness**: count from triage records flagged with hyperthermia + climate metadata.
- **Acute malnutrition**: count of children flagged below -2 z-score for weight-for-height (from `growth-curves`).
- **Vaccination coverage gaps**: count of children identified as behind schedule per vaccine (from `vaccinations`).

Each indicator is tracked per zone and per week. Zones can be administrative (parish, municipality, district) and are configured per deployment.

## Method

Simple statistical comparison, deliberately. The package computes:

1. **Baseline**: rolling mean and standard deviation over the previous 4-6 weeks for each (zone, indicator) pair.
2. **Current week count**: aggregated from the consultations recorded that week.
3. **Z-score**: `(current_week - baseline_mean) / baseline_std_dev`.
4. **Flag**: emit an anomaly when z-score exceeds a configurable threshold (default 2.0, meaning roughly the 97.5th percentile of normal week-to-week variation).

We deliberately chose a transparent statistical method instead of an ML model. Reasons:

1. Public health authorities need to be able to read why a flag was raised. With z-score they can. With a deep model they cannot.
2. Calibration is straightforward: tune the threshold, tune the baseline window, done.
3. We do not have enough historical data per clinic to train a model meaningfully. Statistical baselines work with the data we do have.
4. False positives in this domain are cheap (someone checks the data); false negatives are expensive (an outbreak goes unnoticed). Statistical methods give you a clear knob to bias toward sensitivity.

If at some point we have years of data across many sites, an ML approach may make sense for specific indicators. We will not get there inside this grant period, and we will not pretend to.

## Inputs

- A stream of structured consultation records from the same edge node, written by the other packages in the module.
- Zone configuration (which administrative unit corresponds to which clinic).
- Threshold configuration (per indicator, optional override; defaults shipped with the package).

## Outputs

- A weekly aggregated record per (zone, indicator), with current count, baseline mean, baseline std, z-score, and flag status.
- An optional export adapter to push these records to: a partner NGO dashboard, a DHIS2 instance, an OpenMRS observation export, or a flat CSV/JSON for whatever pipeline the local health authority already uses.

Identifiers are stripped at the node before any record is exported. Patient-level data does not appear anywhere in the output of this package.

## Status

In active development. Target working state by 2026-05-15, with synthetic data tests covering the core statistical logic and at least one export adapter (DHIS2 web API).

Real calibration of thresholds against real consultation patterns happens during the early deployment phase post-grant — the defaults shipped with v0.x are placeholders informed by published epidemiological literature, not field data.

## API (planned)

```python
from kynode_pediatric.anomaly_detection import detect_anomalies

result = detect_anomalies(
    zone="san_cristobal_norte",
    indicator="dengue_suspicion",
    week="2026-W19",
    baseline_weeks=6,
    threshold_z=2.0,
)

# result.current_count == 47
# result.baseline_mean == 12.3
# result.baseline_std == 4.1
# result.z_score == 8.46
# result.flag == "anomaly"
# result.severity == "high"
```

## Open questions

- How to handle a clinic that has been offline for weeks and then dumps a backlog of consultations all at once. Naively this looks like a massive anomaly. We probably need a "data freshness" qualifier on the output.
- How to handle small zones where the baseline mean is close to zero. A single case can blow the z-score even when nothing real is happening. Some kind of minimum baseline floor is probably needed.
- Whether to publish per-zone surveillance signals to the public, or only to authorities. There are real tensions here between transparency and avoiding panic. We will decide this with input from public health partners during the deployment phase.

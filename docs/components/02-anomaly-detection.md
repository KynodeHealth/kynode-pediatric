# Anomaly detection

## What this does

Compares already aggregated weekly counts per zone and indicator against a rolling baseline, then flags when the current count diverges beyond a configurable threshold.

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
- **Growth-status concern**: count of children flagged below a configured growth threshold. Formal acute malnutrition assessment requires weight-for-height/length or MUAC and is not part of this alpha.
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

- Historical weekly counts for a zone-level indicator.
- Current weekly count for the same zone-level indicator.
- Threshold configuration, with a default z-score threshold of 2.0.

## Outputs

- Baseline mean.
- Baseline standard deviation.
- Z-score.
- Flag status: `normal`, `anomaly`, `anomaly_high_severity`, or `insufficient_baseline`.
- Severity and reason.

The package expects aggregate counts only. Patient-level data does not appear anywhere in the package API.

## Status

**Pre-pilot alpha.** Implemented as the standalone package `kynode-pediatric-anomaly-detection`, with synthetic tests covering the core statistical logic.

Real calibration of thresholds against real consultation patterns happens during the early deployment phase post-grant — the defaults shipped with v0.x are placeholders informed by published epidemiological literature, not field data.

## API

```python
from kynode_pediatric_anomaly_detection import detect_anomaly

result = detect_anomaly(
    historical_counts=[10, 12, 8, 11, 9, 13],
    current_count=47,
    threshold_z=2.0,
)

# result.baseline_mean == 10.5
# result.baseline_std == 1.71
# result.z_score == 21.37
# result.flag == "anomaly_high_severity"
# result.severity == "high"
```

## Open questions

- How to handle a clinic that has been offline for weeks and then dumps a backlog of consultations all at once. Naively this looks like a massive anomaly. We probably need a "data freshness" qualifier on the output.
- How to handle small zones where the baseline mean is close to zero. A single case can blow the z-score even when nothing real is happening. Some kind of minimum baseline floor is probably needed.
- Whether to publish per-zone surveillance signals to the public, or only to authorities. There are real tensions here between transparency and avoiding panic. We will decide this with input from public health partners during the deployment phase.

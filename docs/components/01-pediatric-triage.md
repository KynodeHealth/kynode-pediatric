# Pediatric triage

## What this does

Captures vital signs at the front desk of the clinic and applies age-specific reference ranges, so that a 2-year-old does not get measured against thresholds designed for an adult.

## Why it matters

Pediatric vital signs are different from adult ones. Heart rate, respiratory rate, temperature thresholds and oxygen saturation expectations all shift with age — sometimes substantially. A clinic that uses a generic adult triage tool will under-flag young children with sepsis (because their normal heart rates are higher than an adult's) and over-flag healthy infants with normal-for-age tachypnea.

Most rural clinics in Venezuela do not have a pediatric-specific triage form on paper. The nurse uses what she has and adjusts in her head. The point of this component is to take that mental work off her plate without taking the decision off her plate.

## Inputs

- Patient age in years. The alpha API accepts fractional years and falls back to adult ranges when age is unknown or invalid.
- Heart rate (beats per minute)
- Respiratory rate (breaths per minute)
- Temperature in degrees Celsius
- SpO₂ (oxygen saturation, percent)
- Optional: weight, height, capillary refill time

## Outputs

- A flag for each supplied measure: `normal`, `abnormal_low`, `abnormal_high`, `critical_low`, or `critical_high`.
- The age band used for classification.
- The reference range used for each supplied measure.

The alpha package does not compute a composite triage level. It marks individual vital signs for clinician review.

## Data sources

Reference ranges from:

- World Health Organization. *Pocket book of hospital care for children: guidelines for the management of common childhood illnesses* (2nd edition, 2013).
- WHO IMCI chart booklet (current version maintained by WHO Family, Women's, and Children's Health).

We will document the exact table and version used in the source code, so that anyone reading the rule can verify it against the published reference.

## Status

**Pre-pilot alpha.** Implemented as the standalone package `kynode-pediatric-triage-ranges`.

## API

```python
from kynode_pediatric_triage_ranges import classify_vitals, get_vital_ranges

result = classify_vitals(
    age_years=2,
    heart_rate=145,
    respiratory_rate=42,
    temperature_c=39.1,
    spo2=94,
)

# result.band_label == "toddler_1_3_years"
# result.flags["heart_rate"] == "abnormal_high"
# result.flags["respiratory_rate"] == "abnormal_high"
# result.flags["temperature_c"] == "abnormal_high"
# result.flags["spo2"] == "abnormal_low"
```

## Open questions

- Whether to add a separate composite triage level in a future package, or keep this package limited to vital-sign flags.
- How to represent estimated age explicitly in the UI layer during field pilots.

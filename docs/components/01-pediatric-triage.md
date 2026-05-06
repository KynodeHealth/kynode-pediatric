# Pediatric triage

## What this does

Captures vital signs at the front desk of the clinic and applies age-specific reference ranges, so that a 2-year-old does not get measured against thresholds designed for an adult.

## Why it matters

Pediatric vital signs are different from adult ones. Heart rate, respiratory rate, temperature thresholds and oxygen saturation expectations all shift with age — sometimes substantially. A clinic that uses a generic adult triage tool will under-flag young children with sepsis (because their normal heart rates are higher than an adult's) and over-flag healthy infants with normal-for-age tachypnea.

Most rural clinics in Venezuela do not have a pediatric-specific triage form on paper. The nurse uses what she has and adjusts in her head. The point of this component is to take that mental work off her plate without taking the decision off her plate.

## Inputs

- Patient age in months. The calculator uses age in months (not years) because the reference ranges shift quickly in the first few years — a 6-month-old and a 24-month-old are very different.
- Heart rate (beats per minute)
- Respiratory rate (breaths per minute)
- Temperature in degrees Celsius
- SpO₂ (oxygen saturation, percent)
- Optional: weight, height, capillary refill time

## Outputs

- A `normality` flag for each measure: `normal`, `abnormal_low`, or `abnormal_high`
- A composite `triage_level`: `green`, `yellow`, or `red`
- A `flagged_measures` list explaining which thresholds were crossed and what the reference range was

The composite triage level uses a simple precedence: any `red` measure makes the visit `red`. Any `yellow` without a `red` makes the visit `yellow`. Otherwise `green`.

## Data sources

Reference ranges from:

- World Health Organization. *Pocket book of hospital care for children: guidelines for the management of common childhood illnesses* (2nd edition, 2013).
- WHO IMCI chart booklet (current version maintained by WHO Family, Women's, and Children's Health).

We will document the exact table and version used in the source code, so that anyone reading the rule can verify it against the published reference.

## Status

**Spec stage.** Implementation begins after `growth-curves` and `vaccinations` reach working state. Targeted for the post-grant build phase if UNICEF funding lands; otherwise scheduled for later in 2026.

## API (planned)

```python
from kynode_pediatric.triage import triage

result = triage(
    age_months=24,
    heart_rate=145,
    respiratory_rate=42,
    temperature_c=39.1,
    spo2=94,
)

# result.triage_level == "yellow"
# result.flagged_measures == [
#     {"measure": "heart_rate", "value": 145, "expected_range": (90, 140), "flag": "abnormal_high"},
#     {"measure": "temperature_c", "value": 39.1, "expected_range": (36.0, 38.0), "flag": "abnormal_high"},
#     {"measure": "spo2", "value": 94, "expected_range": (95, 100), "flag": "abnormal_low"},
# ]
```

## Open questions

- Whether to expose the raw reference ranges as a public API (so a partner could plot a custom chart, for example), or keep them internal. Leaning toward exposing them — it makes auditing easier.
- How to handle the case where age is unknown (a foundling or a child whose mother does not have the date of birth). One option: require an estimated age and flag the result as `estimated`. Another option: refuse to triage and require entering an estimated age first. We will decide this with input from the clinicians on the pilot site before shipping.

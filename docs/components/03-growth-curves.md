# Growth Curves

## What This Does

`growth-curves` calculates WHO LMS z-scores and percentiles for child growth-status review. The alpha supports:

- `weight_for_age`
- `height_for_age`
- `bmi_for_age`

The public API is intentionally narrow and supports ages 0-60 months.

## Why It Matters

Growth tracking is one of the most reliable signals a clinic can capture during routine pediatric care. In climate-vulnerable settings, nutrition risk can worsen after food disruption, flooding, displacement or disease outbreaks. The package turns local measurements into structured growth-status flags without requiring internet access.

## API

```python
from kynode_pediatric_growth_curves import calculate_zscore

result = calculate_zscore(
    indicator="weight_for_age",
    age_months=24,
    sex="female",
    value=9.2,
)

# result.z_score
# result.percentile
# result.interpretation
# result.formula_used
```

## Outputs

- `z_score`
- `percentile`
- `interpretation`: `severely_low`, `low`, `normal`, `high`, or `very_high`
- `indicator`
- `formula_used`
- `source`
- `clinical_note`

## Data Source

The alpha bundles a compact WHO LMS reference table for 0-60 months. It interpolates between bundled age points when needed.

Formal deployment should replace this compact table with reviewed complete WHO tables or keep supported ages locked to explicitly reviewed points.

## Clinical Boundary

This package provides growth-status flags only. It does not diagnose acute malnutrition. Formal acute malnutrition assessment requires weight-for-height/length, MUAC and/or local clinical protocol.

## Status

Pre-pilot alpha. Implemented, tested and used by the bilingual demo.

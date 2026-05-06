# IMCI Rules

## What This Will Do

`imci-rules` will implement deterministic danger-sign rules based on WHO Integrated Management of Childhood Illness guidance.

This package is not included in the pregrant alpha. It is part of the work the grant would fund.

## Planned Scope

The first implementation should focus on rule groups that matter for climate-sensitive pediatric care:

- fever danger signs
- dehydration and diarrheal disease signs
- respiratory distress signs
- nutrition-related referral flags
- general danger signs for escalation

The package should return auditable flags, not diagnoses.

## Planned API Shape

```python
from kynode_pediatric_imci_rules import evaluate_danger_signs

result = evaluate_danger_signs(
    age_months=24,
    symptoms={
        "fever": True,
        "lethargy": False,
        "respiratory_distress": True,
    },
    vitals={
        "respiratory_rate": 44,
        "temperature_c": 39.8,
    },
)

# result.flags
# result.escalation_level
# result.rationale
```

The final API may change after clinical review.

## Design Rules

- Deterministic rules only.
- No generative AI in the alert path.
- Every flag must include a readable rationale.
- Every rule must cite the WHO source section used.
- The package must run offline and without database or cloud dependencies.

## Clinical Boundary

The package will support clinical review and escalation. It will not diagnose, prescribe or replace professional judgment.

## Status

Post-grant planned package. Not shipped in the pregrant alpha.

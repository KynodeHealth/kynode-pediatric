# Vaccinations

## What This Does

`vaccinations` compares a child's recorded vaccine doses against a configurable country schedule and returns:

- completed doses
- doses due now
- overdue doses
- upcoming doses
- unmatched records that need local reconciliation

The package is offline and uses bundled schedule JSON.

## Why It Matters

Missed vaccine doses are easy to lose in paper records, especially when families move between clinics. The package gives the local team a structured view of schedule status during the visit and can also support aggregate coverage-gap surveillance by zone.

## API

```python
from kynode_pediatric_vaccinations import get_vaccination_status

status = get_vaccination_status(
    birth_date="2024-08-15",
    vaccinations_received=[
        {"vaccine": "BCG", "date": "2024-08-16"},
        {"vaccine": "hepB_birth", "date": "2024-08-16"},
    ],
    country="VE",
    reference_date="2026-05-15",
)

# status.completed
# status.due
# status.overdue
# status.upcoming
# status.unmatched_received
```

## Schedule Source

The Venezuela alpha schedule is based on public SVPP 2025 recommendations and is marked:

```text
reference_schedule_pending_moh_validation
```

Formal field deployment must validate the schedule against MPPS/PAI guidance and local site policy.

## Clinical Boundary

This package does not decide whether a vaccine should be administered during a visit. It organizes schedule status for clinician and program review.

## Status

Pre-pilot alpha. Implemented, tested and used by the bilingual demo.

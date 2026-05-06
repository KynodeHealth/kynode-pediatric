# KYNODE Pediatric Vaccinations

Offline vaccination schedule status helpers for the KYNODE Pediatric pre-pilot alpha. The bundled Venezuela schedule is a reference schedule based on public SVPP 2025 recommendations and is marked pending ministerial validation.

```bash
python3 -m pip install -e .
python3 - <<'PY'
from kynode_pediatric_vaccinations import get_vaccination_status

status = get_vaccination_status(
    birth_date="2024-08-15",
    vaccinations_received=[{"vaccine": "BCG", "date": "2024-08-16"}],
    reference_date="2026-05-15",
)
print(status.overdue[:3])
PY
python3 -m pytest
```

This package does not decide whether a vaccine should be administered during a visit. It organizes schedule status for clinician review.

Spanish note: el calendario incluido es una referencia publica pendiente de validacion ministerial para despliegues formales.

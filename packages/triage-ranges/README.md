# KYNODE Pediatric Triage Ranges

Offline age-banded vital sign reference flags for point-of-care support. The package gives UI/audit hints only; it does not diagnose, prioritize autonomously or replace professional judgment.

```bash
pip install -e .
python - <<'PY'
from kynode_pediatric_triage_ranges import classify_vitals

print(classify_vitals(age_years=2, heart_rate=70, temperature_c=40, spo2=96))
PY
pytest
```

Spanish note: rangos de apoyo para triaje pediatrico. El sistema marca valores fuera de rango; el clinico decide.

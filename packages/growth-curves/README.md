# KYNODE Pediatric Growth Curves

Offline WHO LMS z-score helpers for pediatric growth status flags from 0-60 months. This package is deterministic, auditable and standalone; it does not call KYNODE core, a database or any cloud service.

```bash
python3 -m pip install -e .
python3 - <<'PY'
from kynode_pediatric_growth_curves import calculate_zscore

result = calculate_zscore("weight_for_age", age_months=24, sex="female", value=12.5)
print(result)
PY
python3 -m pytest
```

The bundled LMS data is a compact offline table derived from WHO Child Growth Standards / WHO Reference values and interpolated between available age points. Do not treat the output as a diagnosis; it is a growth-status flag for clinician review.

Spanish note: este paquete calcula percentiles y z-scores de apoyo. No diagnostica desnutricion ni sustituye criterio clinico.

# KYNODE Pediatric Anomaly Detection

Transparent rolling-baseline anomaly flags for aggregated pediatric climate-health indicators. This package uses simple statistics, not black-box ML.

```bash
python3 -m pip install -e .
python3 - <<'PY'
from kynode_pediatric_anomaly_detection import detect_anomaly

print(detect_anomaly([10, 12, 8, 11, 9, 13], 47))
PY
python3 -m pytest
```

Outputs are intended for aggregate surveillance review. They are not clinical diagnoses, outbreak declarations or automated public-health actions.

Spanish note: este paquete marca desviaciones estadisticas agregadas por zona/semana. No declara brotes por si solo.

# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import json
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for package in [
    "growth-curves",
    "triage-ranges",
    "anomaly-detection",
    "vaccinations",
]:
    sys.path.insert(0, str(ROOT / "packages" / package / "src"))

from kynode_pediatric_anomaly_detection import detect_anomaly  # noqa: E402
from kynode_pediatric_growth_curves import calculate_zscore  # noqa: E402
from kynode_pediatric_triage_ranges import classify_vitals  # noqa: E402
from kynode_pediatric_vaccinations import get_vaccination_status  # noqa: E402


def encode(value):
    if is_dataclass(value):
        return asdict(value)
    return value


def main() -> None:
    reference_date = "2026-05-06"
    generated_at = datetime.now(timezone.utc).isoformat()
    child = {
        "display_id": "DEMO-CHILD-024",
        "age_months": 24,
        "age_years": 2,
        "sex": "female",
        "zone": "San Cristobal Norte",
        "context": "Synthetic walkthrough. Recent heavy rains observed locally; clinic working offline.",
    }

    triage = classify_vitals(
        age_years=child["age_years"],
        heart_rate=138,
        respiratory_rate=36,
        temperature_c=39.2,
        spo2=97,
    )
    growth = calculate_zscore(
        "weight_for_age",
        age_months=child["age_months"],
        sex=child["sex"],
        value=9.2,
    )
    vaccinations = get_vaccination_status(
        birth_date="2024-05-06",
        vaccinations_received=[
            {"vaccine": "BCG", "date": "2024-05-06"},
            {"vaccine": "hepB_birth", "date": "2024-05-06"},
            {"vaccine": "pentavalent_1", "date": "2024-07-06"},
            {"vaccine": "polio_1", "date": "2024-07-06"},
            {"vaccine": "rotavirus_1", "date": "2024-07-06"},
            {"vaccine": "pcv_1", "date": "2024-07-06"},
            {"vaccine": "pentavalent_2", "date": "2024-09-06"},
        ],
        reference_date=reference_date,
    )
    signal = detect_anomaly(
        historical_counts=[18, 24, 21, 28, 19, 26],
        current_count=38,
        threshold_z=2.0,
        minimum_baseline_mean=3.0,
    )

    payload = {
        "meta": {
            "generated_at": generated_at,
            "demo_reference_date": reference_date,
            "demo_type": "synthetic",
            "language_default": "en",
        },
        "child": child,
        "triage": {
            **encode(triage),
            "values": {
                "heart_rate": 138,
                "respiratory_rate": 36,
                "temperature_c": 39.2,
                "spo2": 97,
            },
        },
        "growth": encode(growth),
        "vaccinations": encode(vaccinations),
        "signal": {
            **encode(signal),
            "zone": child["zone"],
            "week": "2026-W19",
            "indicator": "dengue_suspicion",
            "historical_counts": [18, 24, 21, 28, 19, 26],
            "current_count": 38,
            "signal_source": "synthetic_demo",
            "climate_context": {
                "rainfall": "heavy",
                "flooding": "reported",
                "heat_alert": "no",
                "water_disruption": "yes",
                "vector_risk": "increased",
                "source": "clinic_observation",
                "confidence": "medium",
            },
            "exportable_record": {
                "export_type": "kynode_pediatric_weekly_aggregate",
                "schema_version": "0.2.0",
                "zone": child["zone"],
                "week": "2026-W19",
                "indicator": "dengue_suspicion",
                "count": 38,
                "z_score": signal.z_score,
                "signal_source": "synthetic_demo",
                "contains_phi": False,
            },
        },
        "privacy": {
            "phi_boundary": "PHI stays inside the clinic. Only aggregated zone-level signal leaves the node.",
            "contains_real_patient_data": False,
            "clinical_boundary": "Statistical support only. No autonomous diagnosis.",
        },
    }

    output_path = Path(__file__).resolve().parent / "data" / "demo-output.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

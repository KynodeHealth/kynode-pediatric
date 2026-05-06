# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date
from typing import Any

from kynode_pediatric_growth_curves import calculate_zscore
from kynode_pediatric_triage_ranges import classify_vitals
from kynode_pediatric_vaccinations import get_vaccination_status

from .models import AssessmentRequest


PRIVACY_BOUNDARY = "Patient-level data stays on this device. Only aggregated zone-level signal is exportable."
CLINICAL_BOUNDARY = "Statistical support only. No autonomous diagnosis."
SURVEILLANCE_BOUNDARY = (
    "Weekly aggregate signals are generated from surveillance input, "
    "not from patient-level assessment payloads."
)


def _encode(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    return value


def completed_months(birth_date: date, reference_date: date) -> int:
    """Return completed months between birth and reference date."""
    if reference_date < birth_date:
        raise ValueError("reference_date cannot be before birth_date")
    months = (reference_date.year - birth_date.year) * 12 + (reference_date.month - birth_date.month)
    if reference_date.day < birth_date.day:
        months -= 1
    return months


def build_assessment(request: AssessmentRequest) -> dict[str, Any]:
    """Run local deterministic pediatric support calculations."""
    age_months = completed_months(request.birth_date, request.reference_date)
    if age_months > 60:
        raise ValueError("The pre-pilot growth package currently supports children up to 60 months.")

    triage = classify_vitals(
        age_years=age_months / 12,
        heart_rate=request.vitals.heart_rate,
        respiratory_rate=request.vitals.respiratory_rate,
        temperature_c=request.vitals.temperature_c,
        spo2=request.vitals.spo2,
    )
    growth = calculate_zscore(
        "weight_for_age",
        age_months=age_months,
        sex=request.sex,
        value=request.weight_kg,
    )
    vaccinations = get_vaccination_status(
        birth_date=request.birth_date,
        vaccinations_received=[
            {"vaccine": record.vaccine, "date": record.date}
            for record in request.vaccinations_received
        ],
        country="VE",
        reference_date=request.reference_date,
    )

    return {
        "child": {
            "local_child_id": request.local_child_id,
            "age_months": age_months,
            "sex": request.sex,
            "zone": request.zone,
            "context": request.context,
        },
        "triage": {
            **_encode(triage),
            "values": _encode(request.vitals.model_dump()),
        },
        "growth": _encode(growth),
        "vaccinations": _encode(vaccinations),
        "syndrome_indicator_preview": {
            "zone": request.zone,
            "week": request.week,
            "indicator": request.syndrome_indicator,
            "boundary": SURVEILLANCE_BOUNDARY,
        },
        "privacy": {
            "boundary": PRIVACY_BOUNDARY,
            "contains_patient_level_data": True,
            "exportable_from_assessment": False,
        },
        "quality_warnings": [
            "prepilot_thresholds_not_field_calibrated",
            "vaccination_schedule_pending_moh_validation",
        ],
        "clinical_note": CLINICAL_BOUNDARY,
    }

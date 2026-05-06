# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import math
from dataclasses import dataclass


CLINICAL_NOTE = (
    "Age-banded vital sign flag only. This output is not a diagnosis, triage "
    "order or treatment recommendation."
)


@dataclass(frozen=True)
class VitalRange:
    min: float
    max: float
    crit_min: float | None = None
    crit_max: float | None = None


@dataclass(frozen=True)
class VitalRangeSet:
    band_label: str
    heart_rate: VitalRange
    respiratory_rate: VitalRange
    systolic_bp: VitalRange
    diastolic_bp: VitalRange
    temperature_c: VitalRange
    spo2: VitalRange
    glucose_mg_dl: VitalRange


@dataclass(frozen=True)
class VitalClassification:
    band_label: str
    flags: dict[str, str]
    ranges: dict[str, tuple[float, float]]
    clinical_note: str = CLINICAL_NOTE


COMMON_TEMPERATURE = VitalRange(min=36.1, max=37.5, crit_min=35.0, crit_max=39.5)
COMMON_SPO2 = VitalRange(min=95, max=100, crit_min=90, crit_max=101)
COMMON_GLUCOSE = VitalRange(min=70, max=100, crit_min=54, crit_max=200)

RANGE_BANDS: tuple[tuple[float, VitalRangeSet], ...] = (
    (
        1,
        VitalRangeSet(
            band_label="infant_0_1_year",
            heart_rate=VitalRange(100, 160, 80, 200),
            respiratory_rate=VitalRange(30, 60, 20, 80),
            systolic_bp=VitalRange(70, 100, 55, 120),
            diastolic_bp=VitalRange(35, 65, 25, 80),
            temperature_c=COMMON_TEMPERATURE,
            spo2=COMMON_SPO2,
            glucose_mg_dl=COMMON_GLUCOSE,
        ),
    ),
    (
        3,
        VitalRangeSet(
            band_label="toddler_1_3_years",
            heart_rate=VitalRange(80, 130, 60, 180),
            respiratory_rate=VitalRange(22, 40, 18, 60),
            systolic_bp=VitalRange(80, 110, 65, 130),
            diastolic_bp=VitalRange(40, 70, 30, 85),
            temperature_c=COMMON_TEMPERATURE,
            spo2=COMMON_SPO2,
            glucose_mg_dl=COMMON_GLUCOSE,
        ),
    ),
    (
        12,
        VitalRangeSet(
            band_label="child_4_12_years",
            heart_rate=VitalRange(70, 110, 50, 160),
            respiratory_rate=VitalRange(18, 30, 14, 50),
            systolic_bp=VitalRange(90, 120, 75, 140),
            diastolic_bp=VitalRange(50, 80, 40, 95),
            temperature_c=COMMON_TEMPERATURE,
            spo2=COMMON_SPO2,
            glucose_mg_dl=COMMON_GLUCOSE,
        ),
    ),
    (
        17,
        VitalRangeSet(
            band_label="adolescent_13_17_years",
            heart_rate=VitalRange(60, 100, 45, 150),
            respiratory_rate=VitalRange(14, 22, 10, 40),
            systolic_bp=VitalRange(100, 130, 85, 160),
            diastolic_bp=VitalRange(55, 85, 45, 105),
            temperature_c=COMMON_TEMPERATURE,
            spo2=COMMON_SPO2,
            glucose_mg_dl=COMMON_GLUCOSE,
        ),
    ),
)

ADULT_RANGES = VitalRangeSet(
    band_label="adult_fallback_18_plus",
    heart_rate=VitalRange(60, 100, 40, 150),
    respiratory_rate=VitalRange(12, 20, 10, 30),
    systolic_bp=VitalRange(90, 140, 70, 180),
    diastolic_bp=VitalRange(60, 90, 40, 110),
    temperature_c=COMMON_TEMPERATURE,
    spo2=COMMON_SPO2,
    glucose_mg_dl=COMMON_GLUCOSE,
)


def get_vital_ranges(age_years: float | None) -> VitalRangeSet:
    """Return age-banded vital sign reference ranges.

    Unknown or invalid ages use the adult fallback, matching the defensive
    behavior in the KYNODE consultation UI.
    """
    if age_years is None:
        return ADULT_RANGES
    try:
        age = float(age_years)
    except (TypeError, ValueError):
        return ADULT_RANGES
    if not math.isfinite(age) or age < 0:
        return ADULT_RANGES
    for upper_age, ranges in RANGE_BANDS:
        if age <= upper_age:
            return ranges
    return ADULT_RANGES


def _flag_value(value: float, vital_range: VitalRange) -> str:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("vital values must be finite") from exc
    if not math.isfinite(numeric_value):
        raise ValueError("vital values must be finite")
    if vital_range.crit_min is not None and numeric_value < vital_range.crit_min:
        return "critical_low"
    if vital_range.crit_max is not None and numeric_value > vital_range.crit_max:
        return "critical_high"
    if numeric_value < vital_range.min:
        return "abnormal_low"
    if numeric_value > vital_range.max:
        return "abnormal_high"
    return "normal"


def classify_vitals(
    *,
    age_years: float | None,
    heart_rate: float | None = None,
    respiratory_rate: float | None = None,
    temperature_c: float | None = None,
    spo2: float | None = None,
) -> VitalClassification:
    """Classify provided vitals against age-adjusted reference ranges."""
    ranges = get_vital_ranges(age_years)
    values = {
        "heart_rate": (heart_rate, ranges.heart_rate),
        "respiratory_rate": (respiratory_rate, ranges.respiratory_rate),
        "temperature_c": (temperature_c, ranges.temperature_c),
        "spo2": (spo2, ranges.spo2),
    }
    flags: dict[str, str] = {}
    range_summary: dict[str, tuple[float, float]] = {}
    for name, (value, vital_range) in values.items():
        if value is None:
            continue
        flags[name] = _flag_value(value, vital_range)
        range_summary[name] = (vital_range.min, vital_range.max)
    return VitalClassification(
        band_label=ranges.band_label,
        flags=flags,
        ranges=range_summary,
    )

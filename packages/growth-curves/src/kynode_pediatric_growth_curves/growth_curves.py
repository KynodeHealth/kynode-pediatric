# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Mapping


SOURCE_NOTE = (
    "WHO Child Growth Standards (2006) and WHO Reference 2007; compact offline "
    "LMS table bundled for pre-pilot alpha. Missing age points are linearly "
    "interpolated."
)

CLINICAL_NOTE = (
    "Growth status flag only. This output is not a diagnosis and does not "
    "replace clinical judgment."
)
SUPPORTED_INDICATORS = {"weight_for_age", "height_for_age", "bmi_for_age"}
SUPPORTED_MAX_AGE_MONTHS = 60


@dataclass(frozen=True)
class GrowthCurveResult:
    z_score: float
    percentile: float
    interpretation: str
    indicator: str
    formula_used: str
    source: str
    clinical_note: str = CLINICAL_NOTE


@lru_cache(maxsize=1)
def _load_tables() -> Mapping[str, object]:
    data_path = resources.files("kynode_pediatric_growth_curves").joinpath(
        "data/who_lms_compact.json"
    )
    return json.loads(data_path.read_text(encoding="utf-8"))


def _normalize_sex(sex: str) -> str:
    if not isinstance(sex, str):
        raise ValueError("sex must be 'male' or 'female'")
    normalized = sex.strip().lower()
    if normalized in {"m", "male", "masculino"}:
        return "male"
    if normalized in {"f", "female", "femenino"}:
        return "female"
    raise ValueError("sex must be 'male' or 'female'")


def _interpolate_lms(table: Mapping[str, Mapping[str, float]], age_months: int) -> tuple[float, float, float]:
    ages = sorted(int(age) for age in table.keys())
    if age_months <= ages[0]:
        entry = table[str(ages[0])]
        return entry["L"], entry["M"], entry["S"]
    if age_months >= ages[-1]:
        entry = table[str(ages[-1])]
        return entry["L"], entry["M"], entry["S"]

    lower_age = max(age for age in ages if age <= age_months)
    upper_age = min(age for age in ages if age >= age_months)
    if lower_age == upper_age:
        entry = table[str(lower_age)]
        return entry["L"], entry["M"], entry["S"]

    low = table[str(lower_age)]
    high = table[str(upper_age)]
    fraction = (age_months - lower_age) / (upper_age - lower_age)
    l_value = low["L"] + fraction * (high["L"] - low["L"])
    m_value = low["M"] + fraction * (high["M"] - low["M"])
    s_value = low["S"] + fraction * (high["S"] - low["S"])
    return l_value, m_value, s_value


def _z_to_percentile(z_score: float) -> float:
    return round(0.5 * (1 + math.erf(z_score / math.sqrt(2))) * 100, 1)


def _interpret(z_score: float) -> str:
    if z_score < -3:
        return "severely_low"
    if z_score < -2:
        return "low"
    if z_score <= 2:
        return "normal"
    if z_score <= 3:
        return "high"
    return "very_high"


def calculate_zscore(indicator: str, age_months: int, sex: str, value: float) -> GrowthCurveResult:
    """Calculate an offline WHO LMS z-score for a growth-status flag.

    Supported indicators are ``weight_for_age``, ``height_for_age`` and
    ``bmi_for_age``. The function is deterministic and has no side effects.
    It returns a clinician-auditable formula string and a non-diagnostic
    interpretation flag.
    """
    if not isinstance(indicator, str):
        raise ValueError("indicator must be one of: weight_for_age, height_for_age, bmi_for_age")
    if not isinstance(age_months, int):
        raise ValueError("age_months must be an integer month value")
    if age_months < 0:
        raise ValueError("age_months cannot be negative")
    if age_months > SUPPORTED_MAX_AGE_MONTHS:
        raise ValueError(f"age_months exceeds alpha maximum ({SUPPORTED_MAX_AGE_MONTHS})")
    try:
        measurement = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("value must be a finite number greater than zero") from exc
    if not math.isfinite(measurement) or measurement <= 0:
        raise ValueError("value must be a finite number greater than zero")

    tables = _load_tables()
    if indicator not in SUPPORTED_INDICATORS:
        raise ValueError("indicator must be one of: weight_for_age, height_for_age, bmi_for_age")

    sex_key = _normalize_sex(sex)
    indicator_table = tables[indicator]
    if sex_key not in indicator_table:
        raise ValueError(f"no LMS data available for sex={sex_key!r} and indicator={indicator!r}")

    age_table = indicator_table[sex_key]
    max_age = max(int(age) for age in age_table.keys())
    if age_months > max_age:
        raise ValueError(f"age_months exceeds bundled table maximum ({max_age})")

    l_value, m_value, s_value = _interpolate_lms(age_table, age_months)
    if abs(l_value) > 1e-10:
        raw_z = ((measurement / m_value) ** l_value - 1) / (l_value * s_value)
        formula = (
            f"Z = (({measurement:.2f}/{m_value:.4f})^{l_value:.4f} - 1) / "
            f"({l_value:.4f} * {s_value:.5f}) = {raw_z:.2f}"
        )
    else:
        raw_z = math.log(measurement / m_value) / s_value
        formula = f"Z = ln({measurement:.2f}/{m_value:.4f}) / {s_value:.5f} = {raw_z:.2f}"

    z_score = max(-5.0, min(5.0, raw_z))
    formula_used = (
        f"indicator={indicator}; sex={sex_key}; age_months={age_months}; "
        f"L={l_value:.4f}; M={m_value:.4f}; S={s_value:.5f}; {formula}"
    )

    return GrowthCurveResult(
        z_score=round(z_score, 2),
        percentile=_z_to_percentile(z_score),
        interpretation=_interpret(z_score),
        indicator=indicator,
        formula_used=formula_used,
        source=SOURCE_NOTE,
    )

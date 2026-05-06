# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Sequence


CLINICAL_NOTE = (
    "Aggregate statistical signal only. This output is not a diagnosis, outbreak "
    "declaration or automated action trigger."
)


@dataclass(frozen=True)
class AnomalyResult:
    baseline_mean: float
    baseline_std: float
    z_score: float
    flag: str
    severity: str
    reason: str
    clinical_note: str = CLINICAL_NOTE


def detect_anomaly(
    historical_counts: Sequence[int | float],
    current_count: int | float,
    threshold_z: float = 2.0,
    minimum_baseline_mean: float = 3.0,
) -> AnomalyResult:
    """Compare the current weekly count against a rolling historical baseline.

    The function expects already aggregated zone-level counts, not patient-level
    records. It uses population standard deviation and a conservative minimum
    baseline mean guard to avoid over-interpreting very small zones.
    """
    try:
        current = float(current_count)
    except (TypeError, ValueError) as exc:
        raise ValueError("current_count must be finite") from exc
    if not math.isfinite(current):
        raise ValueError("current_count must be finite")
    if current < 0:
        raise ValueError("current_count cannot be negative")
    try:
        threshold = float(threshold_z)
        minimum_mean = float(minimum_baseline_mean)
    except (TypeError, ValueError) as exc:
        raise ValueError("threshold_z and minimum_baseline_mean must be finite") from exc
    if not math.isfinite(threshold) or not math.isfinite(minimum_mean):
        raise ValueError("threshold_z and minimum_baseline_mean must be finite")
    if threshold <= 0:
        raise ValueError("threshold_z must be greater than zero")
    if minimum_mean < 0:
        raise ValueError("minimum_baseline_mean cannot be negative")

    try:
        values = [float(value) for value in historical_counts]
    except (TypeError, ValueError) as exc:
        raise ValueError("historical_counts must contain finite values") from exc
    if any(not math.isfinite(value) for value in values):
        raise ValueError("historical_counts must contain finite values")
    if any(value < 0 for value in values):
        raise ValueError("historical_counts cannot contain negative values")
    if len(values) < 3:
        return AnomalyResult(
            baseline_mean=round(mean(values), 2) if values else 0.0,
            baseline_std=0.0,
            z_score=0.0,
            flag="insufficient_baseline",
            severity="low",
            reason="At least three historical counts are required.",
        )
    baseline_mean = mean(values)
    baseline_std = pstdev(values)

    if baseline_mean < minimum_mean:
        return AnomalyResult(
            baseline_mean=round(baseline_mean, 2),
            baseline_std=round(baseline_std, 2),
            z_score=0.0,
            flag="normal",
            severity="low",
            reason="Baseline mean is below the minimum threshold for anomaly flagging.",
        )

    effective_std = baseline_std if baseline_std > 0 else 1.0
    z_score = (current - baseline_mean) / effective_std
    if z_score < threshold:
        return AnomalyResult(
            baseline_mean=round(baseline_mean, 2),
            baseline_std=round(baseline_std, 2),
            z_score=round(z_score, 2),
            flag="normal",
            severity="low",
            reason="Current count is within the rolling baseline threshold.",
        )

    high_severity = z_score >= threshold * 2 or (
        baseline_mean > 0 and current >= baseline_mean * 3
    )
    return AnomalyResult(
        baseline_mean=round(baseline_mean, 2),
        baseline_std=round(baseline_std, 2),
        z_score=round(z_score, 2) if math.isfinite(z_score) else 0.0,
        flag="anomaly_high_severity" if high_severity else "anomaly",
        severity="high" if high_severity else "medium",
        reason="Current count exceeds the rolling baseline threshold.",
    )

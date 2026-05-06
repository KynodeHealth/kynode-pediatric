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
    if current_count < 0:
        raise ValueError("current_count cannot be negative")
    if threshold_z <= 0:
        raise ValueError("threshold_z must be greater than zero")
    if minimum_baseline_mean < 0:
        raise ValueError("minimum_baseline_mean cannot be negative")

    values = [float(value) for value in historical_counts]
    if len(values) < 3:
        return AnomalyResult(
            baseline_mean=round(mean(values), 2) if values else 0.0,
            baseline_std=0.0,
            z_score=0.0,
            flag="insufficient_baseline",
            severity="low",
            reason="At least three historical counts are required.",
        )
    if any(value < 0 for value in values):
        raise ValueError("historical_counts cannot contain negative values")

    baseline_mean = mean(values)
    baseline_std = pstdev(values)

    if baseline_mean < minimum_baseline_mean:
        return AnomalyResult(
            baseline_mean=round(baseline_mean, 2),
            baseline_std=round(baseline_std, 2),
            z_score=0.0,
            flag="normal",
            severity="low",
            reason="Baseline mean is below the minimum threshold for anomaly flagging.",
        )

    effective_std = baseline_std if baseline_std > 0 else 1.0
    z_score = (float(current_count) - baseline_mean) / effective_std
    if z_score < threshold_z:
        return AnomalyResult(
            baseline_mean=round(baseline_mean, 2),
            baseline_std=round(baseline_std, 2),
            z_score=round(z_score, 2),
            flag="normal",
            severity="low",
            reason="Current count is within the rolling baseline threshold.",
        )

    high_severity = z_score >= threshold_z * 2 or (
        baseline_mean > 0 and float(current_count) >= baseline_mean * 3
    )
    return AnomalyResult(
        baseline_mean=round(baseline_mean, 2),
        baseline_std=round(baseline_std, 2),
        z_score=round(z_score, 2) if math.isfinite(z_score) else 0.0,
        flag="anomaly_high_severity" if high_severity else "anomaly",
        severity="high" if high_severity else "medium",
        reason="Current count exceeds the rolling baseline threshold.",
    )

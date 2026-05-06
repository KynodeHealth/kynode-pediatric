from kynode_pediatric_anomaly_detection import detect_anomaly


def test_clear_dengue_anomaly_is_high_severity():
    result = detect_anomaly([10, 12, 8, 11, 9, 13], 47)
    assert result.flag == "anomaly_high_severity"
    assert result.severity == "high"
    assert result.z_score > 2


def test_stable_baseline_normal_current_count():
    result = detect_anomaly([10, 11, 10, 12, 11, 10], 12)
    assert result.flag == "normal"


def test_high_variance_baseline_reduces_flagging():
    result = detect_anomaly([3, 30, 7, 28, 12, 25], 31)
    assert result.flag == "normal"


def test_current_count_lower_than_baseline_does_not_flag():
    result = detect_anomaly([20, 22, 18, 21, 19, 23], 10)
    assert result.flag == "normal"
    assert result.z_score < 0


def test_zero_standard_deviation_does_not_divide_by_zero():
    result = detect_anomaly([10, 10, 10, 10], 13, threshold_z=2.0)
    assert result.flag in {"anomaly", "anomaly_high_severity"}
    assert result.z_score == 3.0


def test_low_baseline_mean_is_guarded():
    result = detect_anomaly([0, 1, 0, 1, 0, 1], 4, minimum_baseline_mean=3)
    assert result.flag == "normal"
    assert "minimum" in result.reason


def test_insufficient_history_returns_specific_flag():
    result = detect_anomaly([10, 11], 20)
    assert result.flag == "insufficient_baseline"


def test_negative_historical_count_is_rejected_before_baseline_check():
    try:
        detect_anomaly([-1, 2], 4)
    except ValueError as exc:
        assert "negative" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_non_finite_counts_are_rejected():
    try:
        detect_anomaly([10, 11, float("nan")], 12)
    except ValueError as exc:
        assert "finite" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_non_finite_threshold_is_rejected():
    try:
        detect_anomaly([10, 11, 12], 13, threshold_z=float("nan"))
    except ValueError as exc:
        assert "finite" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_custom_threshold_changes_result():
    default = detect_anomaly([10, 12, 8, 11, 9, 13], 13, threshold_z=2.0)
    sensitive = detect_anomaly([10, 12, 8, 11, 9, 13], 13, threshold_z=1.0)
    assert default.flag == "normal"
    assert sensitive.flag in {"anomaly", "anomaly_high_severity"}

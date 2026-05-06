from kynode_pediatric_growth_curves import calculate_zscore


def test_reference_fixture_weight_for_age_male_newborn():
    result = calculate_zscore("weight_for_age", 0, "male", 3.3464)
    assert abs(result.z_score) <= 0.01
    assert 49 <= result.percentile <= 51


def test_reference_fixture_weight_for_age_female_twelve_months():
    result = calculate_zscore("weight_for_age", 12, "female", 8.9481)
    assert abs(result.z_score) <= 0.01


def test_reference_fixture_height_for_age_male_twenty_four_months():
    result = calculate_zscore("height_for_age", 24, "male", 87.8161)
    assert abs(result.z_score) <= 0.01


def test_reference_fixture_bmi_for_age_female_sixty_months():
    result = calculate_zscore("bmi_for_age", 60, "female", 15.3677)
    assert abs(result.z_score) <= 0.01


def test_reference_fixture_height_for_age_female_sixty_months():
    result = calculate_zscore("height_for_age", 60, "female", 111.041)
    assert abs(result.z_score) <= 0.01


def test_reference_fixture_interpolated_month():
    result = calculate_zscore("weight_for_age", 14, "male", 10.25)
    assert result.indicator == "weight_for_age"
    assert result.formula_used


def test_age_sixty_supported():
    result = calculate_zscore("weight_for_age", 60, "male", 18.3)
    assert result.z_score is not None


def test_age_above_sixty_rejected_for_alpha_scope():
    try:
        calculate_zscore("weight_for_age", 61, "male", 19)
    except ValueError as exc:
        assert "alpha maximum" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_invalid_indicator_raises():
    try:
        calculate_zscore("weight_for_height", 24, "female", 12.5)
    except ValueError as exc:
        assert "indicator" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_negative_age_raises():
    try:
        calculate_zscore("weight_for_age", -1, "female", 12.5)
    except ValueError as exc:
        assert "negative" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_non_finite_measurement_rejected():
    try:
        calculate_zscore("weight_for_age", 12, "female", float("nan"))
    except ValueError as exc:
        assert "finite" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_extreme_z_score_is_clamped():
    low = calculate_zscore("weight_for_age", 12, "male", 0.2)
    high = calculate_zscore("weight_for_age", 12, "male", 80)
    assert low.z_score == -5.0
    assert high.z_score == 5.0


def test_percentile_bounds_and_clinical_note():
    result = calculate_zscore("weight_for_age", 24, "female", 12.5)
    assert 0 <= result.percentile <= 100
    assert "not a diagnosis" in result.clinical_note

from kynode_pediatric_triage_ranges import classify_vitals, get_vital_ranges


def test_newborn_heart_rate_120_is_normal():
    result = classify_vitals(age_years=0, heart_rate=120)
    assert result.band_label == "infant_0_1_year"
    assert result.flags["heart_rate"] == "normal"


def test_toddler_heart_rate_70_is_abnormal_low():
    result = classify_vitals(age_years=2, heart_rate=70)
    assert result.band_label == "toddler_1_3_years"
    assert result.flags["heart_rate"] == "abnormal_low"


def test_unknown_age_uses_adult_fallback():
    assert get_vital_ranges(None).band_label == "adult_fallback_18_plus"
    assert get_vital_ranges(-1).band_label == "adult_fallback_18_plus"


def test_spo2_89_is_critical_low():
    result = classify_vitals(age_years=8, spo2=89)
    assert result.flags["spo2"] == "critical_low"


def test_temperature_40_is_critical_high():
    result = classify_vitals(age_years=2, temperature_c=40)
    assert result.flags["temperature_c"] == "critical_high"


def test_missing_values_are_omitted():
    result = classify_vitals(age_years=2, heart_rate=100)
    assert result.flags == {"heart_rate": "normal"}
    assert "respiratory_rate" not in result.flags

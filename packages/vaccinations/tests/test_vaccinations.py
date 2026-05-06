from kynode_pediatric_vaccinations import get_vaccination_status


def test_newborn_without_vaccines_has_birth_doses_due():
    status = get_vaccination_status(
        birth_date="2026-05-15",
        vaccinations_received=[],
        reference_date="2026-05-15",
    )
    due_ids = {item["vaccine"] for item in status.due}
    assert {"BCG", "hepB_birth"} <= due_ids


def test_newborn_with_birth_doses_completed():
    status = get_vaccination_status(
        birth_date="2026-05-15",
        vaccinations_received=[
            {"vaccine": "BCG", "date": "2026-05-15"},
            {"vaccine": "hepB_birth", "date": "2026-05-15"},
        ],
        reference_date="2026-05-15",
    )
    completed_ids = {item["vaccine"] for item in status.completed}
    assert {"BCG", "hepB_birth"} <= completed_ids


def test_six_month_child_complete_to_date_has_no_overdue():
    received = [
        {"vaccine": "BCG", "date": "2025-11-15"},
        {"vaccine": "hepB_birth", "date": "2025-11-15"},
        {"vaccine": "pentavalent_1", "date": "2026-01-15"},
        {"vaccine": "polio_1", "date": "2026-01-15"},
        {"vaccine": "rotavirus_1", "date": "2026-01-15"},
        {"vaccine": "pcv_1", "date": "2026-01-15"},
        {"vaccine": "pentavalent_2", "date": "2026-03-15"},
        {"vaccine": "polio_2", "date": "2026-03-15"},
        {"vaccine": "rotavirus_2", "date": "2026-03-15"},
        {"vaccine": "pcv_2", "date": "2026-03-15"},
        {"vaccine": "pentavalent_3", "date": "2026-05-15"},
        {"vaccine": "polio_3", "date": "2026-05-15"},
        {"vaccine": "rotavirus_3", "date": "2026-05-15"},
        {"vaccine": "pcv_3", "date": "2026-05-15"},
    ]
    status = get_vaccination_status("2025-11-15", received, reference_date="2026-05-15")
    assert status.overdue == []


def test_eighteen_month_child_with_missing_doses_has_overdue():
    status = get_vaccination_status(
        birth_date="2024-11-15",
        vaccinations_received=[
            {"vaccine": "BCG", "date": "2024-11-15"},
            {"vaccine": "hepB_birth", "date": "2024-11-15"},
            {"vaccine": "pentavalent_1", "date": "2025-01-15"},
        ],
        reference_date="2026-05-15",
    )
    overdue_ids = {item["vaccine"] for item in status.overdue}
    assert "mmr_1" in overdue_ids
    assert "pentavalent_2" in overdue_ids


def test_five_year_child_complete_schedule():
    all_ids = [
        "BCG", "hepB_birth", "pentavalent_1", "polio_1", "rotavirus_1", "pcv_1",
        "pentavalent_2", "polio_2", "rotavirus_2", "pcv_2", "pentavalent_3",
        "polio_3", "rotavirus_3", "pcv_3", "mmr_1", "yellow_fever_1",
        "pcv_booster", "pentavalent_booster", "mmr_2",
    ]
    received = [{"vaccine": vaccine, "date": "2021-01-01"} for vaccine in all_ids]
    status = get_vaccination_status("2021-05-15", received, reference_date="2026-05-15")
    assert status.overdue == []
    assert len(status.completed) == len(all_ids)


def test_unknown_vaccine_is_returned_unmatched():
    status = get_vaccination_status(
        "2026-05-15",
        [{"vaccine": "local_card_note", "date": "2026-05-15"}],
        reference_date="2026-05-15",
    )
    assert status.unmatched_received == [{"vaccine": "local_card_note", "date": "2026-05-15"}]
    assert status.source["validation_status"] == "reference_schedule_pending_moh_validation"

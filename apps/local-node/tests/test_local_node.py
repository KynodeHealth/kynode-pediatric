# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from kynode_pediatric_local_node import create_app


STATIC_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "kynode_pediatric_local_node"
    / "static"
)


def sample_assessment_payload() -> dict[str, object]:
    return {
        "local_child_id": "LOCAL-CHILD-024",
        "birth_date": "2024-05-06",
        "sex": "female",
        "zone": "San Cristobal Norte",
        "context": "Recent heavy rains; clinic working offline.",
        "weight_kg": 9.2,
        "vitals": {
            "heart_rate": 138,
            "respiratory_rate": 36,
            "temperature_c": 39.2,
            "spo2": 97,
        },
        "vaccinations_received": [
            {"vaccine": "BCG", "date": "2024-05-06"},
            {"vaccine": "hepB_birth", "date": "2024-05-06"},
            {"vaccine": "pentavalent_1", "date": "2024-07-06"},
        ],
        "syndrome_indicator": "dengue_suspicion",
        "week": "2026-W19",
        "reference_date": "2026-05-06",
    }


def sample_weekly_input() -> dict[str, object]:
    return {
        "zone": "San Cristobal Norte",
        "indicator": "dengue_suspicion",
        "week": "2026-W19",
        "historical_counts": [18, 24, 21, 28, 19, 26],
        "current_count": 38,
        "source": "manual_aggregate_entry",
    }


def sample_climate_context() -> dict[str, object]:
    return {
        "zone": "San Cristobal Norte",
        "week": "2026-W19",
        "rainfall": "heavy",
        "flooding": "reported",
        "heat_alert": "no",
        "water_disruption": "yes",
        "vector_risk": "increased",
        "source": "clinic_observation",
        "confidence": "medium",
        "notes": "Standing water reported near school sector.",
    }


def test_health_endpoint(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    response = client.get("/health")
    runtime = client.get("/api/runtime")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "offline-local-node"}
    assert runtime.status_code == 200
    assert runtime.json()["public_demo"] is False
    assert runtime.json()["synthetic_only"] is False


def test_public_demo_runtime_resets_database_and_reports_limits(tmp_path):
    db_path = tmp_path / "public-demo.sqlite3"
    local_client = TestClient(create_app(db_path))
    assert local_client.post("/api/encounters", json=sample_assessment_payload()).status_code == 200
    assert local_client.get("/api/encounters").json()["items"]

    public_client = TestClient(create_app(db_path, public_demo_mode=True))
    runtime = public_client.get("/api/runtime").json()

    assert runtime["mode"] == "public_demo"
    assert runtime["public_demo"] is True
    assert runtime["synthetic_only"] is True
    assert "Do not enter real patient data" in runtime["warning"]
    assert public_client.get("/api/encounters").json()["items"] == []


def test_public_demo_rejects_manual_write_payloads(tmp_path):
    client = TestClient(create_app(tmp_path / "public.sqlite3", public_demo_mode=True))

    responses = [
        client.post("/api/assessments", json=sample_assessment_payload()),
        client.post("/api/encounters", json={"local_child_id": "REAL-TEST"}),
        client.put("/api/weekly-inputs", json=sample_weekly_input()),
        client.put("/api/climate-context", json=sample_climate_context()),
        client.put(
            "/api/node-settings",
            json={
                "clinic_name": "Real Clinic",
                "node_label": "REAL-NODE",
                "country": "VE",
            },
        ),
    ]

    assert [response.status_code for response in responses] == [403, 403, 403, 403, 403]


def test_public_demo_server_owned_synthetic_flow_excludes_notes(tmp_path):
    client = TestClient(create_app(tmp_path / "public.sqlite3", public_demo_mode=True))

    loaded = client.post("/api/demo/load")
    assessment = client.post("/api/demo/assessment")
    encounter = client.post("/api/demo/encounter")
    climate = client.get(
        "/api/climate-context",
        params={"zone": "San Cristobal Norte", "week": "2026-W19"},
    )
    signal = client.get(
        "/api/signals/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )
    exported = client.get(
        "/api/export/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )
    wrong_scope = client.get(
        "/api/signals/weekly",
        params={
            "zone": "Other Zone",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )

    assert loaded.status_code == 200
    assert assessment.status_code == 200
    assert assessment.json()["child"]["local_child_id"] == "DEMO-CHILD-024"
    assert encounter.status_code == 200
    assert encounter.json()["saved_locally"] is True
    items = client.get("/api/encounters").json()["items"]
    assert len(items) == 1
    assert items[0]["local_child_id"] == "DEMO-CHILD-024"
    assert climate.status_code == 200
    assert "notes" not in climate.json()["item"]
    assert signal.status_code == 200
    assert signal.json()["z_score"] == 4.22
    assert exported.status_code == 200
    assert exported.json()["contains_phi"] is False
    assert exported.json()["signal_source"] == "synthetic_demo"
    assert "signal_uses_synthetic_demo_data" in exported.json()["quality_warnings"]
    assert wrong_scope.status_code == 403


def test_static_sensitive_files_are_blocked(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    for suffix in (".sqlite", ".sqlite3", ".db", ".db-journal", ".sqlite3-wal", ".sqlite3-shm"):
        response = client.get(f"/static/kynode_pediatric_local_node{suffix}")
        assert response.status_code == 404


def test_no_database_files_are_bundled_in_static_directory():
    offenders = [
        path
        for path in STATIC_DIR.iterdir()
        if path.suffix in {".sqlite", ".sqlite3", ".db"}
        or path.name.endswith((".db-journal", ".sqlite3-wal", ".sqlite3-shm"))
    ]
    assert offenders == []


def test_node_settings_get_and_upsert(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    initial = client.get("/api/node-settings")
    updated = client.put(
        "/api/node-settings",
        json={
            "clinic_name": "Barrio Obrero Clinic",
            "node_label": "KYNODE-PED-BO-001",
            "country": "ve",
            "operator_initials": "HF",
        },
    )

    assert initial.status_code == 200
    assert initial.json()["country"] == "VE"
    assert updated.status_code == 200
    assert updated.json()["clinic_name"] == "Barrio Obrero Clinic"
    assert updated.json()["country"] == "VE"
    events = client.get("/api/audit-events").json()["items"]
    assert events[0]["event_type"] == "node_settings_updated"


def test_assessment_runs_real_pediatric_packages_without_aggregate_signal(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    response = client.post("/api/assessments", json=sample_assessment_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["child"]["age_months"] == 24
    assert body["triage"]["flags"]["temperature_c"] == "abnormal_high"
    assert body["growth"]["interpretation"] == "low"
    assert body["vaccinations"]["overdue"]
    assert "signal" not in body
    assert body["privacy"]["contains_patient_level_data"] is True
    assert body["privacy"]["exportable_from_assessment"] is False
    assert "No autonomous diagnosis" in body["clinical_note"]


def test_assessment_rejects_weekly_counts_in_payload(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    payload = sample_assessment_payload() | {
        "historical_counts": [1, 2, 3],
        "current_count": 9,
    }

    response = client.post("/api/assessments", json=payload)

    assert response.status_code == 422


def test_save_and_list_local_encounter_creates_audit_event(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    save_response = client.post("/api/encounters", json=sample_assessment_payload())
    list_response = client.get("/api/encounters")

    assert save_response.status_code == 200
    assert save_response.json()["saved_locally"] is True
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["local_child_id"] == "LOCAL-CHILD-024"
    assert items[0]["zone"] == "San Cristobal Norte"
    assert items[0]["growth_flag"] == "low"
    events = client.get("/api/audit-events").json()["items"]
    assert events[0]["event_type"] == "encounter_saved"


def test_weekly_input_upsert_and_signal_generation(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    saved = client.put("/api/weekly-inputs", json=sample_weekly_input())
    fetched = client.get(
        "/api/weekly-inputs",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )
    signal = client.get(
        "/api/signals/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )

    assert saved.status_code == 200
    assert fetched.json()["item"]["current_count"] == 38
    assert signal.status_code == 200
    body = signal.json()
    assert body["current_count"] == 38
    assert body["z_score"] == 4.22
    assert body["flag"] == "anomaly_high_severity"
    assert body["signal_source"] == "manual_aggregate_entry"
    events = client.get("/api/audit-events").json()["items"]
    assert {event["event_type"] for event in events} >= {
        "weekly_input_saved",
        "weekly_signal_generated",
    }


def test_weekly_input_upsert_last_write_wins_but_audits_every_change(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    first = sample_weekly_input()
    second = sample_weekly_input() | {"current_count": 30}

    assert client.put("/api/weekly-inputs", json=first).status_code == 200
    assert client.put("/api/weekly-inputs", json=second).status_code == 200

    item = client.get(
        "/api/weekly-inputs",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    ).json()["item"]
    assert item["current_count"] == 30
    events = client.get("/api/audit-events?limit=10").json()["items"]
    assert sum(event["event_type"] == "weekly_input_saved" for event in events) == 2


def test_climate_context_upsert_and_invalid_enum_rejection(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    saved = client.put("/api/climate-context", json=sample_climate_context())
    fetched = client.get(
        "/api/climate-context",
        params={"zone": "San Cristobal Norte", "week": "2026-W19"},
    )
    invalid = client.put(
        "/api/climate-context",
        json=sample_climate_context() | {"source": "csv_import"},
    )

    assert saved.status_code == 200
    assert fetched.json()["item"]["rainfall"] == "heavy"
    assert fetched.json()["item"]["confidence"] == "medium"
    assert fetched.json()["item"]["notes"] == "Standing water reported near school sector."
    assert invalid.status_code == 422
    events = client.get("/api/audit-events").json()["items"]
    assert events[0]["event_type"] == "climate_context_saved"


def test_weekly_input_rejects_negative_historical_counts(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    response = client.put(
        "/api/weekly-inputs",
        json=sample_weekly_input() | {"historical_counts": [18, -1, 21]},
    )

    assert response.status_code == 422


def test_export_returns_409_without_weekly_input(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    response = client.get(
        "/api/export/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )

    assert response.status_code == 409


def test_export_includes_climate_context_and_excludes_phi(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    client.put("/api/weekly-inputs", json=sample_weekly_input())
    client.put("/api/climate-context", json=sample_climate_context())

    response = client.get(
        "/api/export/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )

    assert response.status_code == 200
    exported = response.json()
    assert exported["export_type"] == "kynode_pediatric_weekly_aggregate"
    assert exported["schema_version"] == "0.2.0"
    assert exported["contains_phi"] is False
    assert exported["zone"] == "San Cristobal Norte"
    assert exported["indicator"] == "dengue_suspicion"
    assert exported["count"] == 38
    assert exported["z_score"] == 4.22
    assert exported["climate_context"]["rainfall"] == "heavy"
    assert "notes" not in exported["climate_context"]
    assert all(exported["privacy_checklist"].values())
    forbidden_keys = {
        "local_child_id",
        "birth_date",
        "vitals",
        "weight_kg",
        "vaccinations_received",
        "context",
        "operator_initials",
    }
    assert forbidden_keys.isdisjoint(exported)
    assert "prepilot_thresholds_not_field_calibrated" in exported["quality_warnings"]
    events = client.get("/api/audit-events").json()["items"]
    assert events[0]["event_type"] == "weekly_export_prepared"


def test_export_warns_when_climate_context_is_missing(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    client.put("/api/weekly-inputs", json=sample_weekly_input())

    exported = client.get(
        "/api/export/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    ).json()

    assert exported["climate_context"] is None
    assert "no_climate_context_recorded" in exported["quality_warnings"]


def test_synthetic_walkthrough_is_explicit_and_marked(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))

    loaded = client.post("/api/demo/load")
    exported = client.get(
        "/api/export/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )
    cleared = client.post("/api/demo/clear")

    assert loaded.status_code == 200
    assert loaded.json()["mode"] == "synthetic_demo"
    assert exported.status_code == 200
    assert exported.json()["signal_source"] == "synthetic_demo"
    assert "signal_uses_synthetic_demo_data" in exported.json()["quality_warnings"]
    audit_after_load = client.get("/api/audit-events?limit=25").json()["items"]
    climate_audit = [
        event for event in audit_after_load
        if event["event_type"] == "climate_context_saved"
    ]
    assert climate_audit, "synthetic walkthrough must produce a climate audit row"
    assert climate_audit[0]["source"] == "synthetic_demo", (
        "audit row for synthetic-walkthrough climate save must be tagged "
        "synthetic_demo so the UI pill does not falsely read clinic_observation"
    )
    assert cleared.status_code == 200
    missing_after_clear = client.get(
        "/api/export/weekly",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    )
    assert missing_after_clear.status_code == 409


def test_synthetic_walkthrough_does_not_overwrite_manual_weekly_or_climate_data(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    client.put("/api/weekly-inputs", json=sample_weekly_input())
    client.put(
        "/api/climate-context",
        json=sample_climate_context() | {"notes": "Manual clinic note."},
    )

    response = client.post("/api/demo/load")

    assert response.status_code == 409
    assert "overwrite manual" in response.json()["detail"]
    item = client.get(
        "/api/weekly-inputs",
        params={
            "zone": "San Cristobal Norte",
            "indicator": "dengue_suspicion",
            "week": "2026-W19",
        },
    ).json()["item"]
    climate = client.get(
        "/api/climate-context",
        params={"zone": "San Cristobal Norte", "week": "2026-W19"},
    ).json()["item"]
    assert item["source"] == "manual_aggregate_entry"
    assert climate["notes"] == "Manual clinic note."


def test_synthetic_walkthrough_detects_structured_climate_conflict(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    client.put(
        "/api/climate-context",
        json=sample_climate_context() | {"rainfall": "moderate"},
    )

    response = client.post("/api/demo/load")

    assert response.status_code == 409
    climate = client.get(
        "/api/climate-context",
        params={"zone": "San Cristobal Norte", "week": "2026-W19"},
    ).json()["item"]
    assert climate["rainfall"] == "moderate"


def test_incompatible_schema_is_backed_up_and_recreated(tmp_path):
    db_path = tmp_path / "node.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.execute("CREATE TABLE weekly_baselines (id INTEGER PRIMARY KEY)")
    connection.commit()
    connection.close()

    client = TestClient(create_app(db_path))

    assert client.get("/health").status_code == 200
    backups = list(tmp_path.glob("node.sqlite3.bak-*"))
    assert backups, "old incompatible database should be renamed before recreation"
    recreated = sqlite3.connect(db_path)
    try:
        user_version = recreated.execute("PRAGMA user_version").fetchone()[0]
    finally:
        recreated.close()
    assert user_version == 2


def test_favicon_svg_is_served(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    response = client.get("/favicon.svg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert response.content.startswith(b"<svg")


def test_favicon_ico_returns_no_content(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    response = client.get("/favicon.ico")
    assert response.status_code == 204


def test_index_loads_design_system_assets_and_product_panels(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    body = client.get("/").text

    assert "/static/tokens.css" in body
    assert "/static/theme-bootstrap.js" in body
    assert "/static/icons.js" in body
    assert 'viewport-fit=cover' in body
    assert 'data-theme="light"' in body
    assert 'media="(prefers-color-scheme: light)"' in body
    assert 'media="(prefers-color-scheme: dark)"' in body
    for required in (
        'id="home"',
        'id="surveillance"',
        'id="records"',
        'id="configuration"',
        'id="weekly-panel"',
        'id="climate-panel"',
        'id="aggregate-panel"',
        'id="privacy-checklist"',
        'id="audit-panel"',
        'id="synthetic-banner"',
        'id="public-demo-banner"',
        'id="context-bar"',
        'id="context-mobile-child"',
        'class="mobile-boundary-strip"',
        'id="node-setup-panel"',
        'class="config-status-grid"',
        'id="copy-export"',
        'id="download-export"',
        'class="json-preview"',
        'class="mobile-tabbar"',
        'data-view-link="home"',
        'data-view-link="surveillance"',
        'data-view-link="records"',
        'data-view-link="configuration"',
    ):
        assert required in body
    assert "?v=0.2.0-ui12" in body
    assert "PHI exported" not in body
    assert "Prepare weekly aggregate export" in body
    assert "Technical JSON preview" in body
    assert 'name="historical_counts"' in body
    assert 'id="case-form"' in body
    assert body.find('id="aggregate-panel"') < body.find('id="weekly-panel"') < body.find('id="climate-panel"')
    assert body.find('id="weekly-form"') < body.find('name="historical_counts"')
    assert body.find('data-i18n="measurements"') < body.find('class="clinical-context-field"')
    assert body.find('id="case-form"') < body.find('id="node-setup-panel"')
    assert body.find('id="surveillance"') < body.find('id="records"') < body.find('id="configuration"')


def test_static_design_system_assets_are_served(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    for path, content_type, must_contain in [
        ("/static/tokens.css", "text/css", "--bg-primary"),
        ("/static/theme-bootstrap.js", "javascript", "data-theme"),
        ("/static/icons.js", "javascript", "LUCIDE_ICONS"),
        ("/static/fonts/InterVariable.woff2", "font", b"wOF2"),
    ]:
        response = client.get(path)
        assert response.status_code == 200, f"{path} should be 200"
        assert content_type in response.headers["content-type"], (
            f"{path} should be served as {content_type}, got "
            f"{response.headers['content-type']}"
        )
        body = response.content if isinstance(must_contain, bytes) else response.text
        assert must_contain in body, f"{path} should contain {must_contain!r}"


def test_frontend_contracts_match_clinic_mode_product_flow(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    html = client.get("/").text
    js = client.get("/static/local-node.js").text

    for button_id, icon_name in {
        "run-assessment": "play",
        "save-encounter": "save",
        "save-weekly-input": "bar-chart-3",
        "save-climate-context": "cloud-rain",
        "generate-signal": "trending-up",
        "export-json": "download",
        "copy-export": "copy",
        "download-export": "download",
        "load-synthetic": "flask-conical",
        "clear-synthetic": "x",
        "open-config": "settings",
        "open-config-sidebar": "settings",
    }.items():
        assert f'id="{button_id}"' in html
        assert f'data-icon="{icon_name}"' in html

    assert "fillSyntheticCase" not in js
    assert "runAssessment()," not in js
    assert "historical_counts" not in js.split("function collectAssessmentPayload", 1)[1].split("function resolveZoneWeekIndicator", 1)[0]
    for helper in ("function setMobileNav", "function showToast", "function withButtonLoading"):
        assert helper in js
    assert 'status.classList.add("loading")' in js
    for helper in (
        "function loadRuntime",
        "function applyRuntimeMode",
        "function isPublicDemo",
        "function renderSparkline",
        "function renderEmptyAggregate",
        "function updateContextBar",
        "function showView",
        "function viewFromHash",
        "function entityKindLabel",
        "function renderPrivacyChecklist",
        "function copyExportJson",
        "function downloadExportJson",
    ):
        assert helper in js
    for mapping in ("privacyLabels", "qualityWarningLabels", "auditEventLabels", "entityKindLabels", "doseLabels"):
        assert mapping in js
    assert "syntheticClinicalContext" in js
    assert "publicDemoText" in js
    assert "/api/demo/assessment" in js
    assert "/api/demo/encounter" in js
    assert "auditExpanded" in js
    assert "toggle-audit-events" in js
    assert '${escapeHtml(key)}: ${escapeHtml(value)}' not in js


def test_visible_i18n_keys_have_human_fallbacks(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    js = client.get("/static/local-node.js").text

    assert "VISIBLE_I18N_FALLBACKS" in js
    assert "humanizeKey(key)" in js
    translate_function = js.split("function t(key)", 1)[1].split("function mappedLabel", 1)[0]
    assert "|| key;" not in translate_function
    for visible_key in ("assessmentEmptyTitle", "assessmentEmptyText", "countryHint"):
        assert visible_key in js
    for copy in (
        "Evalúa un caso local para ver los cuatro análisis",
        "Triaje, crecimiento OMS, vacunas e indicador sindrómico aparecerán aquí.",
        "Código ISO de 2 letras",
    ):
        assert copy in js
    assert 'entityKey === "synthetic_walkthrough"' in js
    assert "Límites actuales del nodo pre-piloto." in js


def test_mobile_navigation_contracts(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    body = client.get("/").text
    css = client.get("/static/local-node.css").text

    assert 'id="mobile-nav-toggle"' in body
    assert 'aria-controls="sidebar"' in body
    assert 'id="mobile-nav-backdrop"' in body
    assert 'id="sidebar"' in body
    assert 'data-mobile-nav="closed"' in body
    assert 'class="mobile-tabbar"' in body
    for href in ('href="#home"', 'href="#surveillance"', 'href="#records"', 'href="#configuration"'):
        assert href in body
    assert "@media (max-width: 760px)" in css
    assert ".mobile-nav-toggle" in css
    assert ".mobile-tabbar" in css
    assert "position: fixed;" in css
    assert "bottom:" in css


def test_toast_region_is_present(tmp_path):
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    body = client.get("/").text
    assert 'id="toast-region"' in body
    assert 'role="status"' in body
    assert 'aria-live="polite"' in body

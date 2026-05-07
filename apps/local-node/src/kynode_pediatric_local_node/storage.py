# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kynode_pediatric_anomaly_detection import detect_anomaly

from .models import (
    AssessmentRequest,
    AuditEvent,
    ClimateContext,
    ClimateContextRequest,
    EncounterSummary,
    NodeSettings,
    NodeSettingsRequest,
    WeeklySignalInput,
    WeeklySignalInputRequest,
)


SCHEMA_VERSION = 2
DEFAULT_NODE_SETTINGS = {
    "clinic_name": "San Cristobal Norte Clinic",
    "node_label": "KYNODE-PED-SCN-001",
    "country": "VE",
}
QUALITY_WARNINGS = [
    "prepilot_thresholds_not_field_calibrated",
    "vaccination_schedule_pending_moh_validation",
]
SYNTHETIC_WALKTHROUGH = {
    "reference_date": "2026-05-06",
    "week": "2026-W19",
    "child": {
        "local_child_id": "DEMO-CHILD-024",
        "birth_date": "2024-05-06",
        "sex": "female",
        "zone": "San Cristobal Norte",
    },
    "vitals": {
        "heart_rate": 138,
        "respiratory_rate": 36,
        "temperature_c": 39.2,
        "spo2": 97,
    },
    "weight_kg": 9.2,
    "weekly_signal_input": {
        "indicator": "dengue_suspicion",
        "historical_counts": [18, 24, 21, 28, 19, 26],
        "current_count": 38,
        "source": "synthetic_demo",
    },
    "climate_context": {
        "rainfall": "heavy",
        "flooding": "reported",
        "heat_alert": "no",
        "water_disruption": "yes",
        "vector_risk": "increased",
        "source": "clinic_observation",
        "confidence": "medium",
        "notes": "Standing water reported near school sector.",
    },
}
SYNTHETIC_VACCINATIONS_RECEIVED = [
    {"vaccine": "BCG", "date": "2024-05-06"},
    {"vaccine": "hepB_birth", "date": "2024-05-06"},
    {"vaccine": "pentavalent_1", "date": "2024-07-06"},
    {"vaccine": "polio_1", "date": "2024-07-06"},
    {"vaccine": "rotavirus_1", "date": "2024-07-06"},
    {"vaccine": "pcv_1", "date": "2024-07-06"},
    {"vaccine": "pentavalent_2", "date": "2024-09-06"},
]


class MissingWeeklyInputError(ValueError):
    """Raised when a weekly aggregate signal cannot be computed yet."""


class SyntheticWalkthroughConflictError(ValueError):
    """Raised when demo data would overwrite manually entered local data."""


class LocalStore:
    """SQLite storage for the local clinic node."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def session(self):
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        if self.db_path.exists() and not self._schema_is_compatible():
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup_path = self.db_path.with_name(f"{self.db_path.name}.bak-{timestamp}")
            shutil.move(str(self.db_path), backup_path)

        with self.session() as connection:
            connection.executescript(
                """
                PRAGMA user_version = 2;

                CREATE TABLE IF NOT EXISTS node_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    clinic_name TEXT NOT NULL,
                    node_label TEXT NOT NULL,
                    country TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS encounters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    week TEXT NOT NULL,
                    local_child_id TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    indicator TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    assessment_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_encounters_zone_indicator_week
                    ON encounters(zone, indicator, week);

                CREATE TABLE IF NOT EXISTS weekly_signal_inputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone TEXT NOT NULL,
                    indicator TEXT NOT NULL,
                    week TEXT NOT NULL,
                    historical_counts_json TEXT NOT NULL,
                    current_count REAL NOT NULL,
                    source TEXT NOT NULL,
                    operator_initials TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL,
                    UNIQUE(zone, indicator, week)
                );

                CREATE TABLE IF NOT EXISTS weekly_climate_contexts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone TEXT NOT NULL,
                    week TEXT NOT NULL,
                    rainfall TEXT NOT NULL,
                    flooding TEXT NOT NULL,
                    heat_alert TEXT NOT NULL,
                    water_disruption TEXT NOT NULL,
                    vector_risk TEXT NOT NULL,
                    source TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    operator_initials TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL,
                    UNIQUE(zone, week)
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    entity_kind TEXT NOT NULL,
                    entity_key TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    operator_initials TEXT NOT NULL DEFAULT '',
                    source TEXT NOT NULL
                );
                """
            )
            now = _utc_now()
            connection.execute(
                """
                INSERT OR IGNORE INTO node_settings (
                    id, clinic_name, node_label, country, updated_at
                ) VALUES (1, ?, ?, ?, ?)
                """,
                (
                    DEFAULT_NODE_SETTINGS["clinic_name"],
                    DEFAULT_NODE_SETTINGS["node_label"],
                    DEFAULT_NODE_SETTINGS["country"],
                    now,
                ),
            )

    def _schema_is_compatible(self) -> bool:
        connection: sqlite3.Connection | None = None
        try:
            connection = self.connect()
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            tables = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
        except sqlite3.DatabaseError:
            return False
        finally:
            if connection is not None:
                connection.close()

        required_tables = {
            "node_settings",
            "encounters",
            "weekly_signal_inputs",
            "weekly_climate_contexts",
            "audit_events",
        }
        return version == SCHEMA_VERSION and required_tables.issubset(tables)

    def audit(
        self,
        event_type: str,
        entity_kind: str,
        entity_key: str,
        *,
        operator_initials: str = "",
        source: str = "manual_local_entry",
        connection: sqlite3.Connection | None = None,
    ) -> None:
        owns_connection = connection is None
        if connection is None:
            connection = self.connect()
        try:
            connection.execute(
                """
                INSERT INTO audit_events (
                    event_type, entity_kind, entity_key, timestamp, operator_initials, source
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event_type,
                    entity_kind,
                    entity_key,
                    _utc_now(),
                    operator_initials,
                    source,
                ),
            )
            if owns_connection:
                connection.commit()
        finally:
            if owns_connection:
                connection.close()

    def get_node_settings(self) -> NodeSettings:
        with self.session() as connection:
            row = connection.execute(
                """
                SELECT clinic_name, node_label, country, updated_at
                FROM node_settings
                WHERE id = 1
                """
            ).fetchone()
        return NodeSettings(**dict(row))

    def save_node_settings(self, request: NodeSettingsRequest) -> NodeSettings:
        updated_at = _utc_now()
        with self.session() as connection:
            connection.execute(
                """
                UPDATE node_settings
                SET clinic_name = ?, node_label = ?, country = ?, updated_at = ?
                WHERE id = 1
                """,
                (
                    request.clinic_name,
                    request.node_label,
                    request.country.upper(),
                    updated_at,
                ),
            )
            self.audit(
                "node_settings_updated",
                "node",
                "settings",
                operator_initials=request.operator_initials,
                source="manual_local_entry",
                connection=connection,
            )
        return self.get_node_settings()

    def save_encounter(
        self,
        request: AssessmentRequest,
        assessment: dict[str, Any],
        *,
        source: str = "manual_local_entry",
    ) -> dict[str, Any]:
        created_at = _utc_now()
        with self.session() as connection:
            cursor = connection.execute(
                """
                INSERT INTO encounters (
                    created_at,
                    week,
                    local_child_id,
                    zone,
                    indicator,
                    request_json,
                    assessment_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    request.week,
                    request.local_child_id,
                    request.zone,
                    request.syndrome_indicator,
                    request.model_dump_json(),
                    json.dumps(assessment),
                ),
            )
            encounter_id = int(cursor.lastrowid)
            self.audit(
                "encounter_saved",
                "encounter",
                str(encounter_id),
                source=source,
                connection=connection,
            )
        return {
            "id": encounter_id,
            "created_at": created_at,
            "saved_locally": True,
            "assessment": assessment,
        }

    def list_encounters(self, limit: int = 25) -> list[EncounterSummary]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, week, local_child_id, zone, indicator, assessment_json
                FROM encounters
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        summaries: list[EncounterSummary] = []
        for row in rows:
            assessment = json.loads(row["assessment_json"])
            summaries.append(
                EncounterSummary(
                    id=row["id"],
                    created_at=row["created_at"],
                    week=row["week"],
                    local_child_id=row["local_child_id"],
                    zone=row["zone"],
                    indicator=row["indicator"],
                    growth_flag=assessment["growth"]["interpretation"],
                    triage_flags=assessment["triage"]["flags"],
                )
            )
        return summaries

    def synthetic_assessment_request(self) -> AssessmentRequest:
        data = SYNTHETIC_WALKTHROUGH
        child = data["child"]
        weekly = data["weekly_signal_input"]
        return AssessmentRequest(
            local_child_id=child["local_child_id"],
            birth_date=child["birth_date"],
            sex=child["sex"],
            zone=child["zone"],
            context="Synthetic walkthrough case. Recent heavy rains; clinic working offline.",
            weight_kg=data["weight_kg"],
            vitals=data["vitals"],
            vaccinations_received=SYNTHETIC_VACCINATIONS_RECEIVED,
            syndrome_indicator=weekly["indicator"],
            week=data["week"],
            reference_date=data["reference_date"],
        )

    def save_weekly_input(self, request: WeeklySignalInputRequest) -> WeeklySignalInput:
        updated_at = _utc_now()
        entity_key = _signal_key(request.zone, request.week, request.indicator)
        with self.session() as connection:
            connection.execute(
                """
                INSERT INTO weekly_signal_inputs (
                    zone,
                    indicator,
                    week,
                    historical_counts_json,
                    current_count,
                    source,
                    operator_initials,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(zone, indicator, week) DO UPDATE SET
                    historical_counts_json = excluded.historical_counts_json,
                    current_count = excluded.current_count,
                    source = excluded.source,
                    operator_initials = excluded.operator_initials,
                    updated_at = excluded.updated_at
                """,
                (
                    request.zone,
                    request.indicator,
                    request.week,
                    json.dumps(request.historical_counts),
                    request.current_count,
                    request.source,
                    request.operator_initials,
                    updated_at,
                ),
            )
            self.audit(
                "weekly_input_saved",
                "weekly_signal",
                entity_key,
                operator_initials=request.operator_initials,
                source=request.source,
                connection=connection,
            )
        return self.get_weekly_input(request.zone, request.indicator, request.week)

    def get_weekly_input(
        self,
        zone: str,
        indicator: str,
        week: str | None = None,
    ) -> WeeklySignalInput | None:
        with self.session() as connection:
            if week:
                row = connection.execute(
                    """
                    SELECT *
                    FROM weekly_signal_inputs
                    WHERE zone = ? AND indicator = ? AND week = ?
                    """,
                    (zone, indicator, week),
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    SELECT *
                    FROM weekly_signal_inputs
                    WHERE zone = ? AND indicator = ?
                    ORDER BY week DESC
                    LIMIT 1
                    """,
                    (zone, indicator),
                ).fetchone()
        if row is None:
            return None
        return _weekly_input_from_row(row)

    def save_climate_context(
        self,
        request: ClimateContextRequest,
        *,
        audit_source: str | None = None,
    ) -> ClimateContext:
        # `audit_source` decouples the audit trail from `request.source`.
        # The climate.source field follows the WHO observation taxonomy
        # (clinic_observation / community_report / authority_bulletin / other)
        # and must remain semantically truthful even when the entry is
        # triggered by the synthetic walkthrough. The audit row, however,
        # records WHY the change happened — so a synthetic-walkthrough load
        # passes audit_source="synthetic_demo" and the audit pill correctly
        # reads as a demo event, not a real clinic observation.
        updated_at = _utc_now()
        entity_key = _climate_key(request.zone, request.week)
        with self.session() as connection:
            connection.execute(
                """
                INSERT INTO weekly_climate_contexts (
                    zone,
                    week,
                    rainfall,
                    flooding,
                    heat_alert,
                    water_disruption,
                    vector_risk,
                    source,
                    confidence,
                    notes,
                    operator_initials,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(zone, week) DO UPDATE SET
                    rainfall = excluded.rainfall,
                    flooding = excluded.flooding,
                    heat_alert = excluded.heat_alert,
                    water_disruption = excluded.water_disruption,
                    vector_risk = excluded.vector_risk,
                    source = excluded.source,
                    confidence = excluded.confidence,
                    notes = excluded.notes,
                    operator_initials = excluded.operator_initials,
                    updated_at = excluded.updated_at
                """,
                (
                    request.zone,
                    request.week,
                    request.rainfall,
                    request.flooding,
                    request.heat_alert,
                    request.water_disruption,
                    request.vector_risk,
                    request.source,
                    request.confidence,
                    request.notes,
                    request.operator_initials,
                    updated_at,
                ),
            )
            self.audit(
                "climate_context_saved",
                "weekly_climate_context",
                entity_key,
                operator_initials=request.operator_initials,
                source=audit_source or request.source,
                connection=connection,
            )
        context = self.get_climate_context(request.zone, request.week)
        assert context is not None
        return context

    def get_climate_context(self, zone: str, week: str) -> ClimateContext | None:
        with self.session() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM weekly_climate_contexts
                WHERE zone = ? AND week = ?
                """,
                (zone, week),
            ).fetchone()
        if row is None:
            return None
        return ClimateContext(
            zone=row["zone"],
            week=row["week"],
            rainfall=row["rainfall"],
            flooding=row["flooding"],
            heat_alert=row["heat_alert"],
            water_disruption=row["water_disruption"],
            vector_risk=row["vector_risk"],
            source=row["source"],
            confidence=row["confidence"],
            notes=row["notes"],
            updated_at=row["updated_at"],
        )

    def weekly_signal(self, zone: str, indicator: str, week: str | None = None) -> dict[str, Any]:
        signal = self._build_weekly_signal(zone=zone, indicator=indicator, week=week)
        self.audit(
            "weekly_signal_generated",
            "weekly_signal",
            _signal_key(signal["zone"], signal["week"], signal["indicator"]),
            source=signal["signal_source"],
        )
        return signal

    def _build_weekly_signal(self, zone: str, indicator: str, week: str | None = None) -> dict[str, Any]:
        weekly_input = self.get_weekly_input(zone=zone, indicator=indicator, week=week)
        if weekly_input is None:
            raise MissingWeeklyInputError(
                "Weekly aggregate input is required before generating or exporting a signal."
            )
        signal = detect_anomaly(
            historical_counts=weekly_input.historical_counts,
            current_count=weekly_input.current_count,
            threshold_z=2.0,
            minimum_baseline_mean=3.0,
        )
        return {
            "zone": weekly_input.zone,
            "week": weekly_input.week,
            "indicator": weekly_input.indicator,
            "historical_counts": weekly_input.historical_counts,
            "current_count": weekly_input.current_count,
            "baseline_mean": signal.baseline_mean,
            "baseline_std": signal.baseline_std,
            "z_score": signal.z_score,
            "flag": signal.flag,
            "severity": signal.severity,
            "reason": signal.reason,
            "signal_source": weekly_input.source,
        }

    def export_weekly_signal(self, zone: str, indicator: str, week: str | None = None) -> dict[str, Any]:
        signal = self._build_weekly_signal(zone=zone, indicator=indicator, week=week)
        climate_context = self.get_climate_context(signal["zone"], signal["week"])
        warnings = list(QUALITY_WARNINGS)
        if signal["signal_source"] == "synthetic_demo":
            warnings.append("signal_uses_synthetic_demo_data")
        if climate_context is None:
            warnings.append("no_climate_context_recorded")

        payload = {
            "export_type": "kynode_pediatric_weekly_aggregate",
            "schema_version": "0.2.0",
            "node": self.get_node_settings().model_dump(exclude={"updated_at"}),
            "zone": signal["zone"],
            "week": signal["week"],
            "indicator": signal["indicator"],
            "count": signal["current_count"],
            "baseline_mean": signal["baseline_mean"],
            "baseline_std": signal["baseline_std"],
            "z_score": signal["z_score"],
            "flag": signal["flag"],
            "severity": signal["severity"],
            "signal_source": signal["signal_source"],
            "climate_context": _exportable_climate_context(climate_context),
            "quality_warnings": warnings,
            "privacy_checklist": {
                "local_child_id_removed": True,
                "birth_date_removed": True,
                "vitals_removed": True,
                "growth_measurements_removed": True,
                "vaccination_details_removed": True,
                "clinical_notes_removed": True,
                "climate_notes_removed": True,
                "operator_initials_removed": True,
                "aggregate_count_only": True,
            },
            "contains_phi": False,
        }
        self.audit(
            "weekly_export_prepared",
            "weekly_signal",
            _signal_key(signal["zone"], signal["week"], signal["indicator"]),
            source=signal["signal_source"],
        )
        return payload

    def record_brief_event(
        self,
        *,
        zone: str,
        week: str,
        indicator: str,
        generator: str,
        language: str,
    ) -> None:
        """Record an audit row for a generated weekly brief.

        The audit `source` field carries the generator name
        (`deterministic_template` or `llm_brief_v1`) so reviewers can
        tell at a glance whether a brief came from the rule-based
        template or from the optional local LLM. The brief content
        itself never reaches the audit table — only the operational
        metadata, consistent with the rest of the audit schema.
        """
        entity_key = f"{_signal_key(zone, week, indicator)}|{language}"
        self.audit(
            "weekly_brief_generated",
            "weekly_signal",
            entity_key,
            source=generator,
        )

    def list_audit_events(self, limit: int = 25) -> list[AuditEvent]:
        with self.session() as connection:
            rows = connection.execute(
                """
                SELECT id, event_type, entity_kind, entity_key, timestamp, operator_initials, source
                FROM audit_events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [AuditEvent(**dict(row)) for row in rows]

    def load_synthetic_walkthrough(self) -> dict[str, Any]:
        data = json.loads(json.dumps(SYNTHETIC_WALKTHROUGH))
        child = data["child"]
        weekly = data["weekly_signal_input"]
        climate = data["climate_context"]
        existing_weekly = self.get_weekly_input(child["zone"], weekly["indicator"], data["week"])
        if existing_weekly is not None and existing_weekly.source != "synthetic_demo":
            raise SyntheticWalkthroughConflictError(
                "Synthetic walkthrough would overwrite manual weekly input. Clear or use a demo database first."
            )
        existing_climate = self.get_climate_context(child["zone"], data["week"])
        if existing_climate is not None and not _climate_matches_synthetic(existing_climate, climate):
            raise SyntheticWalkthroughConflictError(
                "Synthetic walkthrough would overwrite manual climate context. Clear or use a demo database first."
            )
        weekly_record = self.save_weekly_input(
            WeeklySignalInputRequest(
                zone=child["zone"],
                indicator=weekly["indicator"],
                week=data["week"],
                historical_counts=weekly["historical_counts"],
                current_count=weekly["current_count"],
                source=weekly["source"],
            )
        )
        climate_record = self.save_climate_context(
            ClimateContextRequest(
                zone=child["zone"],
                week=data["week"],
                rainfall=climate["rainfall"],
                flooding=climate["flooding"],
                heat_alert=climate["heat_alert"],
                water_disruption=climate["water_disruption"],
                vector_risk=climate["vector_risk"],
                source=climate["source"],
                confidence=climate["confidence"],
                notes=climate["notes"],
            ),
            audit_source="synthetic_demo",
        )
        self.audit(
            "synthetic_walkthrough_loaded",
            "demo",
            "synthetic_walkthrough",
            source="synthetic_demo",
        )
        data["weekly_signal_input"] = weekly_record.model_dump()
        data["climate_context"] = climate_record.model_dump()
        data["mode"] = "synthetic_demo"
        return data

    def clear_synthetic_walkthrough(self) -> dict[str, Any]:
        child = SYNTHETIC_WALKTHROUGH["child"]
        week = SYNTHETIC_WALKTHROUGH["week"]
        indicator = SYNTHETIC_WALKTHROUGH["weekly_signal_input"]["indicator"]
        with self.session() as connection:
            connection.execute(
                """
                DELETE FROM weekly_signal_inputs
                WHERE zone = ? AND indicator = ? AND week = ? AND source = 'synthetic_demo'
                """,
                (child["zone"], indicator, week),
            )
            connection.execute(
                """
                DELETE FROM weekly_climate_contexts
                WHERE zone = ?
                  AND week = ?
                  AND rainfall = ?
                  AND flooding = ?
                  AND heat_alert = ?
                  AND water_disruption = ?
                  AND vector_risk = ?
                  AND source = ?
                  AND confidence = ?
                  AND notes = ?
                """,
                (
                    child["zone"],
                    week,
                    SYNTHETIC_WALKTHROUGH["climate_context"]["rainfall"],
                    SYNTHETIC_WALKTHROUGH["climate_context"]["flooding"],
                    SYNTHETIC_WALKTHROUGH["climate_context"]["heat_alert"],
                    SYNTHETIC_WALKTHROUGH["climate_context"]["water_disruption"],
                    SYNTHETIC_WALKTHROUGH["climate_context"]["vector_risk"],
                    SYNTHETIC_WALKTHROUGH["climate_context"]["source"],
                    SYNTHETIC_WALKTHROUGH["climate_context"]["confidence"],
                    SYNTHETIC_WALKTHROUGH["climate_context"]["notes"],
                ),
            )
            self.audit(
                "synthetic_walkthrough_cleared",
                "demo",
                "synthetic_walkthrough",
                source="manual_local_entry",
                connection=connection,
            )
        return {"mode": "clinic", "cleared": True}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _signal_key(zone: str, week: str, indicator: str) -> str:
    return f"{zone}|{week}|{indicator}"


def _climate_key(zone: str, week: str) -> str:
    return f"{zone}|{week}"


def _weekly_input_from_row(row: sqlite3.Row) -> WeeklySignalInput:
    return WeeklySignalInput(
        zone=row["zone"],
        indicator=row["indicator"],
        week=row["week"],
        historical_counts=json.loads(row["historical_counts_json"]),
        current_count=row["current_count"],
        source=row["source"],
        updated_at=row["updated_at"],
    )


def _exportable_climate_context(context: ClimateContext | None) -> dict[str, str] | None:
    if context is None:
        return None
    return {
        "rainfall": context.rainfall,
        "flooding": context.flooding,
        "heat_alert": context.heat_alert,
        "water_disruption": context.water_disruption,
        "vector_risk": context.vector_risk,
        "source": context.source,
        "confidence": context.confidence,
    }


def _climate_matches_synthetic(context: ClimateContext, synthetic: dict[str, str]) -> bool:
    return all(
        getattr(context, key) == synthetic[key]
        for key in (
            "rainfall",
            "flooding",
            "heat_alert",
            "water_disruption",
            "vector_risk",
            "source",
            "confidence",
            "notes",
        )
    )

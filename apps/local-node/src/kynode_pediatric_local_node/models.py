# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


Indicator = Literal[
    "dengue_suspicion",
    "malaria_suspicion",
    "diarrheal_disease",
    "heat_related_illness",
    "respiratory_outbreak",
    "malnutrition_signal",
]

SignalSource = Literal["manual_aggregate_entry", "synthetic_demo"]

Rainfall = Literal["none", "light", "moderate", "heavy", "unknown"]
Flooding = Literal["no", "reported", "unknown"]
BinaryUnknown = Literal["no", "yes", "unknown"]
VectorRisk = Literal["normal", "increased", "unknown"]
ClimateSource = Literal[
    "clinic_observation",
    "community_report",
    "authority_bulletin",
    "other",
]
Confidence = Literal["low", "medium", "high"]
NonNegativeCount = Annotated[float, Field(ge=0)]


class VitalsInput(BaseModel):
    heart_rate: float | None = Field(default=None, ge=0)
    respiratory_rate: float | None = Field(default=None, ge=0)
    temperature_c: float | None = Field(default=None, ge=25, le=45)
    spo2: float | None = Field(default=None, ge=0, le=100)


class VaccineRecord(BaseModel):
    vaccine: str = Field(min_length=1, max_length=80)
    date: date


class AssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    local_child_id: str = Field(min_length=1, max_length=80)
    birth_date: date
    sex: Literal["male", "female"]
    zone: str = Field(min_length=1, max_length=120)
    context: str = Field(default="", max_length=240)
    weight_kg: float = Field(gt=0, le=80)
    vitals: VitalsInput
    vaccinations_received: list[VaccineRecord] = Field(default_factory=list)
    syndrome_indicator: Indicator
    week: str = Field(pattern=r"^\d{4}-W\d{2}$")
    reference_date: date = Field(default_factory=date.today)


class EncounterSummary(BaseModel):
    id: int
    created_at: str
    week: str
    local_child_id: str
    zone: str
    indicator: str
    growth_flag: str
    triage_flags: dict[str, str]


class NodeSettingsRequest(BaseModel):
    clinic_name: str = Field(min_length=1, max_length=160)
    node_label: str = Field(min_length=1, max_length=80)
    country: str = Field(min_length=2, max_length=2)
    operator_initials: str = Field(default="", max_length=20)


class NodeSettings(BaseModel):
    clinic_name: str
    node_label: str
    country: str
    updated_at: str


class WeeklySignalInputRequest(BaseModel):
    zone: str = Field(min_length=1, max_length=120)
    indicator: Indicator
    week: str = Field(pattern=r"^\d{4}-W\d{2}$")
    historical_counts: list[NonNegativeCount] = Field(min_length=2)
    current_count: float = Field(ge=0)
    source: SignalSource = "manual_aggregate_entry"
    operator_initials: str = Field(default="", max_length=20)


class WeeklySignalInput(BaseModel):
    zone: str
    indicator: Indicator
    week: str
    historical_counts: list[float]
    current_count: float
    source: SignalSource
    updated_at: str


class ClimateContextRequest(BaseModel):
    zone: str = Field(min_length=1, max_length=120)
    week: str = Field(pattern=r"^\d{4}-W\d{2}$")
    rainfall: Rainfall = "unknown"
    flooding: Flooding = "unknown"
    heat_alert: BinaryUnknown = "unknown"
    water_disruption: BinaryUnknown = "unknown"
    vector_risk: VectorRisk = "unknown"
    source: ClimateSource = "clinic_observation"
    confidence: Confidence = "low"
    notes: str = Field(default="", max_length=500)
    operator_initials: str = Field(default="", max_length=20)


class ClimateContext(BaseModel):
    zone: str
    week: str
    rainfall: Rainfall
    flooding: Flooding
    heat_alert: BinaryUnknown
    water_disruption: BinaryUnknown
    vector_risk: VectorRisk
    source: ClimateSource
    confidence: Confidence
    notes: str
    updated_at: str


class AuditEvent(BaseModel):
    id: int
    event_type: str
    entity_kind: str
    entity_key: str
    timestamp: str
    operator_initials: str
    source: str

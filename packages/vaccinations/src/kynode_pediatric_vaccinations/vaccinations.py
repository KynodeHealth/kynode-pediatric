# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import calendar
import json
from dataclasses import dataclass
from datetime import date, datetime
from importlib import resources
from typing import Any, Mapping, Sequence


CLINICAL_NOTE = (
    "Vaccination schedule status only. This output is not an instruction to "
    "administer a vaccine and does not replace local clinical policy."
)


@dataclass(frozen=True)
class VaccinationStatus:
    completed: list[dict[str, Any]]
    due: list[dict[str, Any]]
    overdue: list[dict[str, Any]]
    upcoming: list[dict[str, Any]]
    unmatched_received: list[dict[str, Any]]
    source: dict[str, Any]
    clinical_note: str = CLINICAL_NOTE


def _parse_date(value: str | date | None, *, field_name: str) -> date:
    if value is None:
        return date.today()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from exc


def _parse_required_date(value: str | date | None, *, field_name: str) -> date:
    if value is None:
        raise ValueError(f"{field_name} is required")
    return _parse_date(value, field_name=field_name)


def _add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _load_schedules() -> Mapping[str, Any]:
    data_path = resources.files("kynode_pediatric_vaccinations").joinpath("data/schedules.json")
    return json.loads(data_path.read_text(encoding="utf-8"))


def _dose_view(dose: Mapping[str, Any], target_date: date, received_date: date | None = None) -> dict[str, Any]:
    item = {
        "vaccine": dose["id"],
        "label": dose["label"],
        "target_date": target_date.isoformat(),
    }
    if received_date:
        item["date"] = received_date.isoformat()
    return item


def get_vaccination_status(
    birth_date: str | date,
    vaccinations_received: Sequence[Mapping[str, str]],
    country: str = "VE",
    reference_date: str | date | None = None,
    due_window_days: int = 7,
) -> VaccinationStatus:
    """Return completed, due, overdue and upcoming doses for a child.

    Vaccine matching is by dose identifier. Unknown received records are
    returned in ``unmatched_received`` so implementers can reconcile local
    names without losing source data.
    """
    if due_window_days < 0:
        raise ValueError("due_window_days cannot be negative")

    schedules = _load_schedules()
    country_key = country.upper()
    if country_key not in schedules:
        raise ValueError(f"unsupported country schedule: {country}")

    born_on = _parse_required_date(birth_date, field_name="birth_date")
    ref_date = _parse_date(reference_date, field_name="reference_date")
    if ref_date < born_on:
        raise ValueError("reference_date cannot be before birth_date")

    schedule = schedules[country_key]
    schedule_ids = {dose["id"] for dose in schedule["doses"]}
    received_by_id: dict[str, date] = {}
    unmatched: list[dict[str, Any]] = []
    for record in vaccinations_received:
        vaccine = record.get("vaccine")
        record_date = _parse_required_date(record.get("date"), field_name="vaccinations_received.date")
        if record_date < born_on:
            raise ValueError("vaccinations_received.date cannot be before birth_date")
        if vaccine in schedule_ids:
            received_by_id[vaccine] = record_date
        else:
            unmatched.append({"vaccine": vaccine, "date": record_date.isoformat()})

    completed: list[dict[str, Any]] = []
    due: list[dict[str, Any]] = []
    overdue: list[dict[str, Any]] = []
    upcoming: list[dict[str, Any]] = []

    for dose in schedule["doses"]:
        target_date = _add_months(born_on, int(dose["target_month"]))
        received_date = received_by_id.get(dose["id"])
        if received_date:
            completed.append(_dose_view(dose, target_date, received_date))
            continue

        days_from_target = (ref_date - target_date).days
        if -due_window_days <= days_from_target <= due_window_days:
            due.append(_dose_view(dose, target_date))
        elif days_from_target > due_window_days:
            overdue.append(_dose_view(dose, target_date))
        elif len(upcoming) < 3:
            upcoming.append(_dose_view(dose, target_date))

    source = {
        "country": schedule["country"],
        "schedule_name": schedule["schedule_name"],
        "source_name": schedule["source_name"],
        "source_url": schedule["source_url"],
        "source_date": schedule["source_date"],
        "validation_status": schedule["validation_status"],
        "notes": schedule["notes"],
    }
    return VaccinationStatus(
        completed=completed,
        due=due,
        overdue=overdue,
        upcoming=upcoming,
        unmatched_received=unmatched,
        source=source,
    )

# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ValidationError
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware

from .models import (
    AssessmentRequest,
    ClimateContextRequest,
    NodeSettingsRequest,
    WeeklySignalInputRequest,
)
from .brief import generate_brief
from .service import build_assessment
from .storage import (
    LocalStore,
    MissingWeeklyInputError,
    SyntheticWalkthroughConflictError,
    SYNTHETIC_WALKTHROUGH,
)


class CachedStaticFiles(StaticFiles):
    """StaticFiles subclass that emits long-lived Cache-Control headers.

    Why: production deployments behind nginx / a CDN already handle this, but
    when a UNICEF reviewer (or the local clinic itself) runs the bundled
    uvicorn directly, the default StaticFiles response has no Cache-Control
    at all. Lighthouse marks that as "Use efficient cache lifetimes" and the
    next page load re-fetches every asset. We mark `/static/*` as immutable
    because the local-node ships its assets as a frozen bundle inside the
    package — they only change on a new release.
    """

    SENSITIVE_SUFFIXES = (
        ".sqlite",
        ".sqlite3",
        ".db",
        ".db-journal",
        ".sqlite3-wal",
        ".sqlite3-shm",
    )

    async def get_response(self, path, scope):
        if path.lower().endswith(self.SENSITIVE_SUFFIXES):
            return Response(status_code=404)
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            # 30 days · public · immutable. The font is the biggest single
            # asset (110 KB) so caching it makes the second-and-later visits
            # essentially instant.
            response.headers["Cache-Control"] = "public, max-age=2592000, immutable"
        return response


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"

# Bundled favicon. We vendor a copy from `demo/favicon.svg` into the package
# `static/` so the local-node app stays self-contained — no path lookups
# outside its own package, no surprises when installed via pip.
FAVICON_SVG = STATIC_DIR / "favicon.svg"

# Tiny 1x1 transparent ICO. Some browsers (and some legacy bots) request
# /favicon.ico unconditionally even when an <link rel="icon"> points to SVG.
# Returning an empty 204 is cleaner than a 404 in the access logs.
_NO_CONTENT_FAVICON = Response(status_code=204)
PUBLIC_DEMO_ENV = "KYNODE_PUBLIC_DEMO_MODE"
PUBLIC_DEMO_DB_NAME = "kynode_pediatric_public_demo.sqlite3"
PUBLIC_DEMO_FORBIDDEN = (
    "Public demo accepts synthetic data only. Run the Local Node locally "
    "for real clinic data."
)


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _reset_sqlite_files(db_path: Path) -> None:
    for candidate in (
        db_path,
        db_path.with_name(f"{db_path.name}-wal"),
        db_path.with_name(f"{db_path.name}-shm"),
        db_path.with_name(f"{db_path.name}-journal"),
    ):
        if candidate.exists():
            candidate.unlink()


def _validate_payload(model: type[BaseModel], payload: dict[str, object]) -> BaseModel:
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


def _public_demo_scope_matches(zone: str, indicator: str, week: str | None) -> bool:
    synthetic = SYNTHETIC_WALKTHROUGH
    child = synthetic["child"]
    weekly = synthetic["weekly_signal_input"]
    return (
        zone == child["zone"]
        and indicator == weekly["indicator"]
        and week == synthetic["week"]
    )


def _require_public_demo_scope(zone: str, indicator: str, week: str | None) -> None:
    if not _public_demo_scope_matches(zone, indicator, week):
        raise HTTPException(status_code=403, detail=PUBLIC_DEMO_FORBIDDEN)


def create_app(
    db_path: str | Path | None = None,
    public_demo_mode: bool | None = None,
) -> FastAPI:
    """Create the local-node FastAPI app."""
    public_demo = _env_flag(PUBLIC_DEMO_ENV) if public_demo_mode is None else public_demo_mode
    if public_demo:
        resolved_db_path = Path(db_path) if db_path else Path(tempfile.gettempdir()) / PUBLIC_DEMO_DB_NAME
        _reset_sqlite_files(resolved_db_path)
    else:
        resolved_db_path = db_path or os.environ.get("KYNODE_LOCAL_NODE_DB")
        if not resolved_db_path:
            resolved_db_path = Path.cwd() / "kynode_pediatric_local_node.sqlite3"
    store = LocalStore(resolved_db_path)

    app = FastAPI(
        title="KYNODE Pediatric Local Node",
        version="0.2.0-prepilot-local-node",
        docs_url=None,
        redoc_url=None,
    )
    # Compress responses larger than 500 bytes. CSS/JS shrink ~60-70%, JSON
    # API responses ~50%. The Mini PCs we deploy on can encode a few MB/s
    # of gzip on a single core — the saved bandwidth is worth it on the
    # field-grade WiFi the clinics actually have. minimum_size=500 also
    # skips the 204 favicon and tiny health responses where gzip would add
    # net overhead.
    app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=6)
    app.state.store = store
    app.state.public_demo_mode = public_demo
    app.mount("/static", CachedStaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/favicon.svg")
    def favicon_svg() -> Response:
        # Served at the root path (not /static/) so the standard
        # <link rel="icon" href="/favicon.svg"> resolves with no rewriting.
        if FAVICON_SVG.exists():
            return FileResponse(FAVICON_SVG, media_type="image/svg+xml")
        return _NO_CONTENT_FAVICON

    @app.get("/favicon.ico")
    def favicon_ico() -> Response:
        # Legacy browsers / bots ask for /favicon.ico. Return 204 so the
        # access log stays clean (404 noise on every page load otherwise).
        return _NO_CONTENT_FAVICON

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "offline-local-node"}

    @app.get("/api/runtime")
    def runtime() -> dict[str, object]:
        if app.state.public_demo_mode:
            return {
                "mode": "public_demo",
                "public_demo": True,
                "synthetic_only": True,
                "warning": "Public demo accepts synthetic data only. Do not enter real patient data.",
            }
        return {
            "mode": "local_clinic",
            "public_demo": False,
            "synthetic_only": False,
            "warning": "",
        }

    @app.get("/api/node-settings")
    def get_node_settings() -> dict[str, object]:
        return app.state.store.get_node_settings().model_dump()

    @app.put("/api/node-settings")
    def put_node_settings(payload: dict[str, object]) -> dict[str, object]:
        if app.state.public_demo_mode:
            raise HTTPException(status_code=403, detail=PUBLIC_DEMO_FORBIDDEN)
        request = _validate_payload(NodeSettingsRequest, payload)
        return app.state.store.save_node_settings(request).model_dump()

    @app.post("/api/assessments")
    def assess(payload: dict[str, object]) -> dict[str, object]:
        if app.state.public_demo_mode:
            raise HTTPException(status_code=403, detail=PUBLIC_DEMO_FORBIDDEN)
        request = _validate_payload(AssessmentRequest, payload)
        try:
            return build_assessment(request)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/encounters")
    def save_encounter(payload: dict[str, object]) -> dict[str, object]:
        if app.state.public_demo_mode:
            raise HTTPException(status_code=403, detail=PUBLIC_DEMO_FORBIDDEN)
        request = _validate_payload(AssessmentRequest, payload)
        try:
            assessment = build_assessment(request)
            return app.state.store.save_encounter(request, assessment)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/encounters")
    def list_encounters() -> dict[str, object]:
        return {
            "items": [
                item.model_dump()
                for item in app.state.store.list_encounters()
            ]
        }

    @app.get("/api/weekly-inputs")
    def get_weekly_input(
        zone: str = Query(min_length=1),
        indicator: str = Query(min_length=1),
        week: str | None = Query(default=None, pattern=r"^\d{4}-W\d{2}$"),
    ) -> dict[str, object]:
        item = app.state.store.get_weekly_input(zone=zone, indicator=indicator, week=week)
        return {"item": item.model_dump() if item else None}

    @app.put("/api/weekly-inputs")
    def put_weekly_input(payload: dict[str, object]) -> dict[str, object]:
        if app.state.public_demo_mode:
            raise HTTPException(status_code=403, detail=PUBLIC_DEMO_FORBIDDEN)
        request = _validate_payload(WeeklySignalInputRequest, payload)
        return app.state.store.save_weekly_input(request).model_dump()

    @app.get("/api/climate-context")
    def get_climate_context(
        zone: str = Query(min_length=1),
        week: str = Query(pattern=r"^\d{4}-W\d{2}$"),
    ) -> dict[str, object]:
        item = app.state.store.get_climate_context(zone=zone, week=week)
        if item is None:
            return {"item": None}
        if app.state.public_demo_mode:
            return {"item": item.model_dump(exclude={"notes"})}
        return {"item": item.model_dump()}

    @app.put("/api/climate-context")
    def put_climate_context(payload: dict[str, object]) -> dict[str, object]:
        if app.state.public_demo_mode:
            raise HTTPException(status_code=403, detail=PUBLIC_DEMO_FORBIDDEN)
        request = _validate_payload(ClimateContextRequest, payload)
        return app.state.store.save_climate_context(request).model_dump()

    @app.get("/api/audit-events")
    def audit_events(limit: int = Query(default=25, ge=1, le=100)) -> dict[str, object]:
        return {
            "items": [
                item.model_dump()
                for item in app.state.store.list_audit_events(limit=limit)
            ]
        }

    @app.post("/api/demo/load")
    def load_demo() -> dict[str, object]:
        try:
            return app.state.store.load_synthetic_walkthrough()
        except SyntheticWalkthroughConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/api/demo/clear")
    def clear_demo() -> dict[str, object]:
        return app.state.store.clear_synthetic_walkthrough()

    @app.post("/api/demo/assessment")
    def demo_assessment() -> dict[str, object]:
        if not app.state.public_demo_mode:
            raise HTTPException(status_code=404, detail="Not found")
        return build_assessment(app.state.store.synthetic_assessment_request())

    @app.post("/api/demo/encounter")
    def demo_encounter() -> dict[str, object]:
        if not app.state.public_demo_mode:
            raise HTTPException(status_code=404, detail="Not found")
        request = app.state.store.synthetic_assessment_request()
        assessment = build_assessment(request)
        return app.state.store.save_encounter(request, assessment, source="synthetic_demo")

    @app.get("/api/signals/weekly")
    def weekly_signal(
        zone: str = Query(min_length=1),
        indicator: str = Query(min_length=1),
        week: str | None = Query(default=None, pattern=r"^\d{4}-W\d{2}$"),
    ) -> dict[str, object]:
        if app.state.public_demo_mode:
            _require_public_demo_scope(zone, indicator, week)
        try:
            return app.state.store.weekly_signal(zone=zone, indicator=indicator, week=week)
        except MissingWeeklyInputError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/api/export/weekly")
    def export_weekly_signal(
        zone: str = Query(min_length=1),
        indicator: str = Query(min_length=1),
        week: str | None = Query(default=None, pattern=r"^\d{4}-W\d{2}$"),
    ) -> dict[str, object]:
        if app.state.public_demo_mode:
            _require_public_demo_scope(zone, indicator, week)
        try:
            return app.state.store.export_weekly_signal(zone=zone, indicator=indicator, week=week)
        except MissingWeeklyInputError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/api/brief/generate")
    def brief_generate(
        zone: str = Query(min_length=1),
        indicator: str = Query(min_length=1),
        week: str | None = Query(default=None, pattern=r"^\d{4}-W\d{2}$"),
        lang: str = Query(default="en", pattern=r"^(en|es)$"),
    ) -> dict[str, object]:
        # The brief sits AFTER the privacy boundary: it consumes the
        # weekly export envelope (PHI-free) and adds an interpretation
        # layer for public-health supervisors. We re-fetch the export
        # rather than trusting a client-supplied JSON to keep the
        # privacy contract auditable from a single chokepoint.
        if app.state.public_demo_mode:
            _require_public_demo_scope(zone, indicator, week)
        try:
            export = app.state.store.export_weekly_signal(
                zone=zone, indicator=indicator, week=week
            )
        except MissingWeeklyInputError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        brief = generate_brief(export, lang=lang)
        # Operational audit row: which brief generator ran, for which
        # signal, in which language. The audit schema records the
        # generator name (e.g. "deterministic_template" / "llm_brief_v1")
        # in `source` so reviewers can trace whether a given brief came
        # from the rule-based template or from the local LLM.
        app.state.store.record_brief_event(
            zone=export["zone"],
            week=export["week"],
            indicator=export["indicator"],
            generator=brief.generator,
            language=brief.language,
        )
        return {"brief": brief.model_dump(), "export": export}

    return app

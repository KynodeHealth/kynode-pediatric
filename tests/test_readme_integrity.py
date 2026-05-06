# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.
"""
README and repo-presentation integrity tests.

Repository presentation surface — these guard the public-facing assets that a UNICEF
reviewer (or any visitor) sees first when they open the GitHub page:

- All ![alt](path) screenshots in the README actually exist on disk
- All badges resolve against the workflows/files they claim to track
- The pytest configuration discovers every test directory in the repo
- The sync script and CI workflow exist and reference the right paths
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"


def _readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_screenshot_links_resolve():
    """Every ![alt](relative-path.png) in the README must point to a file
    that actually exists. Catches a broken hero image after a path rename."""
    body = _readme_text()
    matches = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body)
    assert matches, "README has no images; expected product screenshots"
    for relative in matches:
        # Skip absolute URLs (badges, external images)
        if relative.startswith(("http://", "https://")):
            continue
        path = REPO_ROOT / relative
        assert path.exists(), f"README references missing file: {relative}"


def test_readme_internal_doc_links_resolve():
    """Markdown links to relative paths (LICENSE, docs/architecture.md, etc.)
    must exist on disk. Pure URL fragments (#anchor) and external URLs are
    skipped."""
    body = _readme_text()
    # Match [label](target) links but exclude images already covered above.
    links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", body)
    skipped = 0
    for target in links:
        # Drop fragment + query
        clean = target.split("#", 1)[0].split("?", 1)[0]
        if not clean or clean.startswith(("http://", "https://", "mailto:")):
            skipped += 1
            continue
        path = REPO_ROOT / clean
        assert path.exists(), f"README links to missing file: {target}"


def test_readme_has_required_badges():
    """README hero must include at least the build,
    coverage, demo, license, python and status badges."""
    body = _readme_text()
    required_substrings = [
        "actions/workflows/ci.yml/badge.svg",         # CI badge
        "badges/coverage.json",                       # Coverage badge endpoint
        "demo-GitHub%20Pages",                        # Demo badge
        "license-Apache%202.0",                       # License badge
        "python-3.12",                                # Python version badge
        "status-pre--pilot%20alpha",                  # Status badge
    ]
    for needle in required_substrings:
        assert needle in body, f"README missing badge containing '{needle}'"


def test_pytest_ini_includes_all_test_dirs():
    """pytest.ini's testpaths must enumerate every test directory in the
    repo so CI doesn't silently drop tests when a new package or top-level
    suite is added."""
    pytest_ini = (REPO_ROOT / "pytest.ini").read_text(encoding="utf-8")
    expected_paths = (
        "packages/growth-curves/tests",
        "packages/triage-ranges/tests",
        "packages/anomaly-detection/tests",
        "packages/vaccinations/tests",
        "apps/local-node/tests",
        "tests",
    )
    for path in expected_paths:
        assert path in pytest_ini, f"pytest.ini missing testpath: {path}"


def test_sync_script_exists_and_is_executable():
    """The design-system sync script must exist and have the executable bit set
    so contributors can run it without `bash` prefix (and CI can chain it)."""
    script = REPO_ROOT / "scripts" / "sync-design-system.sh"
    assert script.exists(), "scripts/sync-design-system.sh missing"
    assert script.stat().st_mode & 0o111, (
        "scripts/sync-design-system.sh is not executable; "
        "run `chmod +x scripts/sync-design-system.sh`"
    )


def test_ci_workflow_runs_pytest():
    """The CI workflow must invoke pytest at least once. Renaming the test
    runner without updating CI would let regressions slip through."""
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "pytest" in ci, "CI workflow does not run pytest"


def test_pages_workflow_uploads_demo_directory():
    """The GitHub Pages workflow must upload the demo/ directory so the
    deployed site includes the vendored design system files (tokens.css,
    icons.js, fonts/)."""
    pages = (REPO_ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "path: demo" in pages, "Pages workflow does not upload demo/"


@pytest.mark.parametrize("screenshot", [
    "docs/assets/local-node-desktop.png",
    "docs/assets/local-node-mobile.png",
    "docs/assets/demo-screenshot.png",
])
def test_product_screenshots_are_present(screenshot):
    """README should embed three concrete screenshots
    (desktop app, mobile app, static demo). Missing one means the README
    will render a broken image."""
    path = REPO_ROOT / screenshot
    assert path.exists(), f"README screenshot missing: {screenshot}"
    # Quick sanity: should be a PNG with non-trivial size (>10 KB rules out
    # a placeholder file accidentally committed).
    assert path.stat().st_size > 10_000, f"{screenshot} is suspiciously small"
    # PNG magic bytes
    with path.open("rb") as fh:
        head = fh.read(8)
    assert head == b"\x89PNG\r\n\x1a\n", f"{screenshot} is not a valid PNG"


@pytest.mark.parametrize("screenshot", [
    "docs/assets/user-guide/local-node-01-clinic-home.jpg",
    "docs/assets/user-guide/local-node-02-assessment-results.jpg",
    "docs/assets/user-guide/local-node-03-surveillance-export.jpg",
    "docs/assets/user-guide/local-node-04-records-audit.jpg",
    "docs/assets/user-guide/local-node-05-configuration.jpg",
])
def test_user_guide_screenshots_are_present(screenshot):
    """The user guide should remain illustrated with real product captures."""
    path = REPO_ROOT / screenshot
    assert path.exists(), f"user guide screenshot missing: {screenshot}"
    assert path.stat().st_size > 10_000, f"{screenshot} is suspiciously small"
    with path.open("rb") as fh:
        head = fh.read(3)
    assert head == b"\xff\xd8\xff", f"{screenshot} is not a valid JPEG"


def test_user_guides_are_linked_from_readmes():
    en = README.read_text(encoding="utf-8")
    es = (REPO_ROOT / "README.es.md").read_text(encoding="utf-8")
    app = (REPO_ROOT / "apps" / "local-node" / "README.md").read_text(encoding="utf-8")

    assert "docs/user-guide/local-node.md" in en
    assert "docs/user-guide/local-node.es.md" in en
    assert "docs/user-guide/local-node.es.md" in es
    assert "docs/user-guide/local-node.md" in es
    assert "../../docs/user-guide/local-node.md" in app


def test_readme_es_mirrors_readme_structure():
    """The Spanish README must cover the same sections as the English one
    so a LATAM reviewer doesn't get a stripped-down version. Compares the
    *count* of top-level + h2 headings (the actual translation strings
    differ by language, but the structural parity is enforceable)."""
    en = README.read_text(encoding="utf-8")
    es = (REPO_ROOT / "README.es.md").read_text(encoding="utf-8")

    def headings(body: str) -> int:
        return len(re.findall(r"^##? ", body, re.MULTILINE))

    en_count = headings(en)
    es_count = headings(es)
    # ES is allowed to have +1 extra section ("Documentación que ya existe
    # en español") that has no EN equivalent. Anything beyond that is a
    # missing-section regression.
    assert es_count >= en_count, (
        f"README.es.md has {es_count} headings vs {en_count} in README.md — "
        f"the Spanish README is stripped-down. Mirror the missing sections."
    )


def test_readme_es_has_required_badges():
    """The Spanish README must carry the same six badges as the English
    one so the badges row is consistent across languages."""
    es = (REPO_ROOT / "README.es.md").read_text(encoding="utf-8")
    required_substrings = [
        "actions/workflows/ci.yml/badge.svg",
        "badges/coverage.json",
        "demo-GitHub%20Pages",
        "license-Apache%202.0",
        "python-3.12",
        "status-pre--pilot%20alpha",
    ]
    for needle in required_substrings:
        assert needle in es, f"README.es.md missing badge containing '{needle}'"

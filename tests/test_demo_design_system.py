# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.
"""
Static-demo design-system regression tests.

The demo lives outside the FastAPI app and is just an HTML/CSS/JS bundle the
reviewer opens from `python3 -m http.server -d demo`. These tests guard the
sync contract with the local-node design system: same tokens, same fonts,
same theme-bootstrap script, same icon library, same storage key.

A future refactor that breaks the cross-surface coherence (renaming a token,
forgetting to re-run scripts/sync-design-system.sh, leaking a hardcoded color
into the demo CSS) will surface a failing test here.
"""
from __future__ import annotations

import filecmp
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_NODE_STATIC = (
    REPO_ROOT
    / "apps"
    / "local-node"
    / "src"
    / "kynode_pediatric_local_node"
    / "static"
)
DEMO_STATIC = REPO_ROOT / "demo" / "static"
DEMO_INDEX = REPO_ROOT / "demo" / "index.html"
DEMO_CSS = DEMO_STATIC / "kynode-pediatric.css"

VENDORED_FILES = (
    "tokens.css",
    "theme-bootstrap.js",
    "icons.js",
    "fonts/InterVariable.woff2",
)


@pytest.mark.parametrize("relative_path", VENDORED_FILES)
def test_vendored_design_system_files_match_local_node(relative_path):
    """Vendored design-system files in demo/static must be byte-identical
    to their source in apps/local-node. Drift means scripts/sync-design-system.sh
    needs to be re-run before commit."""
    src = LOCAL_NODE_STATIC / relative_path
    dst = DEMO_STATIC / relative_path
    assert src.exists(), f"missing source file: {src}"
    assert dst.exists(), f"missing vendored copy: {dst}"
    assert filecmp.cmp(src, dst, shallow=False), (
        f"{relative_path} drifted from the local-node source. Run "
        f"`bash scripts/sync-design-system.sh` to re-sync."
    )


def test_demo_index_loads_design_system_assets():
    """The demo HTML must wire up the shared design system in the right
    order: theme-bootstrap.js inline in head (anti-FOUC), tokens.css before
    the component CSS, icons.js before demo.js."""
    body = DEMO_INDEX.read_text(encoding="utf-8")
    assert 'src="static/theme-bootstrap.js' in body
    assert 'href="static/tokens.css' in body
    assert 'href="static/kynode-pediatric.css' in body
    assert 'src="static/icons.js' in body
    assert 'src="static/demo.js' in body

    # Order: tokens.css BEFORE kynode-pediatric.css (component layer overrides)
    tokens_pos = body.find('href="static/tokens.css')
    component_pos = body.find('href="static/kynode-pediatric.css')
    assert tokens_pos < component_pos, (
        "tokens.css must load before kynode-pediatric.css so component rules "
        "can reference and override the design tokens"
    )

    # icons.js BEFORE demo.js (demo.js calls KynodeIcons.hydrateIcons())
    icons_pos = body.find('src="static/icons.js')
    demo_pos = body.find('src="static/demo.js')
    assert icons_pos < demo_pos, "icons.js must load before demo.js"


def test_demo_index_has_required_meta_tags():
    """Mobile / iOS PWA contract — viewport-fit=cover for safe-area, dual
    theme-color metas for OS chrome blending."""
    body = DEMO_INDEX.read_text(encoding="utf-8")
    assert "viewport-fit=cover" in body
    assert 'media="(prefers-color-scheme: light)"' in body
    assert 'media="(prefers-color-scheme: dark)"' in body
    assert 'data-theme="light"' in body
    assert 'rel="apple-touch-icon"' in body


def test_demo_css_uses_zero_hardcoded_colors():
    """All colors in the demo component CSS must come from tokens.css.
    Catches accidental color literals re-introduced by future tweaks."""
    body = DEMO_CSS.read_text(encoding="utf-8")
    # Strip comments before counting so a comment that mentions a hex
    # doesn't count as a violation.
    no_comments = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
    hex_matches = re.findall(r"#[0-9a-fA-F]{3,6}\b", no_comments)
    rgba_matches = re.findall(r"rgba?\(\s*\d", no_comments)
    leaks = hex_matches + rgba_matches
    assert not leaks, (
        f"demo CSS contains {len(leaks)} hardcoded color(s) that should be "
        f"design tokens: {leaks[:5]}"
    )


def test_demo_css_does_not_redefine_design_tokens():
    """The demo's component CSS must not declare its own :root token block
    (those live in tokens.css). A local block here would shadow the shared
    tokens and break the cross-surface theme contract."""
    body = DEMO_CSS.read_text(encoding="utf-8")
    # A `:root { --foo: ... }` block declares custom properties globally.
    matches = re.findall(r":root\s*\{[^}]*--[a-z]", body)
    assert not matches, (
        "demo/static/kynode-pediatric.css defines its own :root tokens. "
        "Tokens live in tokens.css; component CSS may only reference them."
    )


def test_demo_uses_shared_theme_storage_key():
    """The demo's theme toggle must read/write the same localStorage key as
    the bootstrap script, otherwise the user's preference doesn't survive
    a page reload."""
    bootstrap = (DEMO_STATIC / "theme-bootstrap.js").read_text(encoding="utf-8")
    demo_js = (DEMO_STATIC / "demo.js").read_text(encoding="utf-8")
    bootstrap_key = re.search(r'STORAGE_KEY\s*=\s*"([^"]+)"', bootstrap)
    demo_key = re.search(r'(?:DEMO_)?THEME_KEY\s*=\s*"([^"]+)"', demo_js)
    assert bootstrap_key, "could not find STORAGE_KEY in theme-bootstrap.js"
    assert demo_key, "could not find theme storage key in demo.js"
    assert bootstrap_key.group(1) == demo_key.group(1), (
        f"theme key mismatch: bootstrap reads {bootstrap_key.group(1)!r} "
        f"but demo writes {demo_key.group(1)!r}. The demo's preference "
        f"will be ignored on reload."
    )


def test_demo_index_has_theme_toggle_with_lucide_icons():
    """The theme toggle must declare both sun and moon icon spans so the
    CSS [data-theme] selectors can show/hide the right one per theme."""
    body = DEMO_INDEX.read_text(encoding="utf-8")
    assert 'id="theme-toggle"' in body
    assert 'data-icon="sun"' in body
    assert 'data-icon="moon"' in body


def test_all_declared_data_icons_are_available():
    """Every rendered data-icon must exist in the vendored icon registry."""
    icon_js = (LOCAL_NODE_STATIC / "icons.js").read_text(encoding="utf-8")
    html_files = [
        LOCAL_NODE_STATIC / "index.html",
        DEMO_INDEX,
    ]
    declared = set()
    for html_file in html_files:
        declared.update(re.findall(r'data-icon="([^"]+)"', html_file.read_text(encoding="utf-8")))

    missing = [
        name
        for name in sorted(declared)
        if f'{name}:' not in icon_js and f'"{name}":' not in icon_js
    ]
    assert missing == []

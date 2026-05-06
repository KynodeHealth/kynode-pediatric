# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.
"""
Performance and offline-readiness contracts.

These tests don't *measure* Lighthouse scores (running Lighthouse in CI is
slow and flaky). They guard the architectural invariants that produce the
scores documented in `docs/qa/phase5-lighthouse-audit.md`:

- Inter Variable font subset stays under the original 350 KB
- Both index.html files preload the font with the right attributes
- Every non-bootstrap script tag has `defer`
- Local-node serves gzipped responses + immutable Cache-Control on /static/
- No HTML/CSS/JS in the bundle reaches an external origin (offline-readiness)
- `font-display: optional` is set on the @font-face rule so cold-load LCP
  isn't gated on font swap

Re-run Lighthouse manually when these change; see the audit doc for the
recipe.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kynode_pediatric_local_node import create_app


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_NODE_STATIC = (
    REPO_ROOT
    / "apps"
    / "local-node"
    / "src"
    / "kynode_pediatric_local_node"
    / "static"
)
LOCAL_NODE_INDEX = LOCAL_NODE_STATIC / "index.html"
LOCAL_NODE_TOKENS = LOCAL_NODE_STATIC / "tokens.css"
LOCAL_NODE_FONT = LOCAL_NODE_STATIC / "fonts" / "InterVariable.woff2"
DEMO_INDEX = REPO_ROOT / "demo" / "index.html"
DEMO_STATIC = REPO_ROOT / "demo" / "static"


def test_inter_font_is_subsetted_below_120kb():
    """The full Inter Variable file weighs ~344 KB. We shipped a Latin-only
    subset; the file must stay under 120 KB or the LCP gains regress."""
    size = LOCAL_NODE_FONT.stat().st_size
    assert size < 120_000, (
        f"InterVariable.woff2 is {size:,} bytes — looks like the full font "
        f"sneaked back in. Re-run pyftsubset (see audit doc)."
    )
    # Sanity: still a valid woff2 with the right magic bytes
    head = LOCAL_NODE_FONT.read_bytes()[:4]
    assert head == b"wOF2", "InterVariable.woff2 lost its woff2 magic bytes"


def test_font_face_uses_font_display_optional():
    """`font-display: optional` is what keeps cold-load LCP unaffected by
    font swap. `swap` triggers a second LCP event. `block` delays FCP.
    Anything else and the perf budget breaks."""
    css = LOCAL_NODE_TOKENS.read_text(encoding="utf-8")
    match = re.search(r"@font-face\s*\{[^}]*font-display:\s*(\w+)", css, re.DOTALL)
    assert match, "no font-display declaration in @font-face block"
    value = match.group(1).strip()
    assert value == "optional", (
        f"font-display is {value!r}; expected 'optional' to "
        f"protect LCP. See docs/qa/phase5-lighthouse-audit.md for why."
    )


@pytest.mark.parametrize("path,base", [
    (LOCAL_NODE_INDEX, "/static/fonts/InterVariable.woff2"),
    (DEMO_INDEX, "static/fonts/InterVariable.woff2"),
])
def test_index_preloads_inter_font(path, base):
    """Both surfaces must <link rel=preload> the font with crossorigin so
    the browser starts the fetch in parallel with the CSS chain. Drop this
    and LCP regresses by ~500-1000 ms on cold load."""
    body = path.read_text(encoding="utf-8")
    pattern = (
        r'<link\s+rel="preload"\s+as="font"\s+type="font/woff2"\s+'
        r'crossorigin="anonymous"\s+href="' + re.escape(base) + r'(?:\?v=[^"]+)?"'
    )
    assert re.search(pattern, body), (
        f"{path.name} missing the Inter font preload link with the exact "
        f"href {base!r}. The browser will defer the font fetch and LCP "
        f"will regress."
    )


@pytest.mark.parametrize("index_path,bootstrap_basename", [
    (LOCAL_NODE_INDEX, "theme-bootstrap.js"),
    (DEMO_INDEX, "theme-bootstrap.js"),
])
def test_non_bootstrap_scripts_use_defer(index_path, bootstrap_basename):
    """Every <script> outside the head must have `defer`. The
    theme-bootstrap script is the documented exception (it must run
    before first paint to set the theme attribute)."""
    body = index_path.read_text(encoding="utf-8")
    scripts = re.findall(r'<script\s+src="([^"]+)"([^>]*)>', body)
    assert scripts, "no <script src=...> tags in the document"
    for src, attrs in scripts:
        if bootstrap_basename in src:
            # Bootstrap script must NOT defer — it runs synchronously to
            # set data-theme before paint.
            assert "defer" not in attrs, (
                f"{src} should not defer (it must run before first paint)"
            )
        else:
            assert "defer" in attrs, (
                f"<script src={src!r}> is missing `defer`. Without it the "
                f"parser blocks on the script and FCP/LCP regress."
            )


def test_local_node_serves_gzip_for_static_assets(tmp_path):
    """The GZipMiddleware must wrap responses big enough to compress.
    The component CSS (~29 KB raw) should drop to ~6-7 KB on the wire."""
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    response = client.get(
        "/static/local-node.css",
        headers={"Accept-Encoding": "gzip"},
    )
    assert response.status_code == 200
    encoding = response.headers.get("content-encoding", "")
    assert "gzip" in encoding, (
        f"CSS response not gzipped (content-encoding={encoding!r}). "
        f"Check that GZipMiddleware is registered before the static mount."
    )


def test_local_node_sets_immutable_cache_on_static(tmp_path):
    """`/static/*` must declare a long-lived immutable Cache-Control so
    repeat visits don't re-fetch the design-system bundle."""
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    for path in ("/static/local-node.css", "/static/local-node.js", "/static/tokens.css"):
        response = client.get(path)
        assert response.status_code == 200, f"{path} did not respond 200"
        cc = response.headers.get("cache-control", "")
        assert "immutable" in cc, (
            f"{path} Cache-Control={cc!r} missing 'immutable'. "
            f"Repeat visits will re-fetch the asset."
        )
        assert "max-age=" in cc, (
            f"{path} Cache-Control missing max-age — set explicit lifetime"
        )


def test_local_node_does_not_compress_tiny_responses(tmp_path):
    """The 204 No-Content favicon.ico response must not be gzipped (no body
    to compress, header-only). Sanity check that GZipMiddleware honours
    the minimum_size threshold."""
    client = TestClient(create_app(tmp_path / "node.sqlite3"))
    response = client.get("/favicon.ico", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 204
    assert "content-encoding" not in {k.lower() for k in response.headers}


@pytest.mark.parametrize("file_path", [
    LOCAL_NODE_STATIC / "index.html",
    LOCAL_NODE_STATIC / "local-node.js",
    LOCAL_NODE_STATIC / "local-node.css",
    LOCAL_NODE_STATIC / "tokens.css",
    LOCAL_NODE_STATIC / "icons.js",
    LOCAL_NODE_STATIC / "theme-bootstrap.js",
    DEMO_INDEX,
    DEMO_STATIC / "kynode-pediatric.css",
    DEMO_STATIC / "demo.js",
    DEMO_STATIC / "i18n.js",
])
def test_no_external_network_dependencies(file_path):
    """Offline-readiness contract: no served file may reference an external
    HTTP/HTTPS origin. Brand links to kynode.io and the LICENSE/spec links
    to apache.org / unicef.org are allowed (they're documentation, not
    runtime dependencies)."""
    text = file_path.read_text(encoding="utf-8")
    # Strip CSS/JS/HTML comments so a comment that mentions an external URL
    # doesn't count as a runtime dependency.
    no_comments = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    no_comments = re.sub(r"//.*$", "", no_comments, flags=re.MULTILINE)
    no_comments = re.sub(r"<!--.*?-->", "", no_comments, flags=re.DOTALL)

    # Any http(s) URL that's NOT in this allowlist is a violation.
    allowlist = (
        "kynode.io",                        # brand link, anchor only
        "kynodehealth.github.io",           # GitHub Pages demo, link only
        "github.com/KynodeHealth",          # repo link
        "www.unicef.org",                   # grant page link in docs
        "www.w3.org",                       # XML namespace declaration in SVGs
        "svpediatria.org",                  # vaccination schedule attribution (data file, not fetched)
        "apache.org/licenses",              # LICENSE pointer
    )
    urls = re.findall(r"https?://[a-zA-Z0-9.-]+", no_comments)
    violations = [
        u for u in urls
        if not any(needle in u for needle in allowlist)
    ]
    assert not violations, (
        f"{file_path.name} references external origins outside the allowlist: "
        f"{set(violations)}. Offline-readiness contract violated."
    )

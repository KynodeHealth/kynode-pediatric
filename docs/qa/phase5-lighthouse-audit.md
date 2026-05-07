# Lighthouse + Offline QA Audit

Date: 2026-05-06
Tool: Lighthouse 12.8.2 (npx)
Browser: Headless Chrome 148, desktop form factor, no throttling
Pages tested: local-node app (`/`) and static demo (`/`)

## Scope: which Lighthouse categories matter for KYNODE Pediatric

| Category | Relevant? | Why |
|---|:-:|---|
| **Performance** | ✅ | Real users on poor networks; fast first paint matters in the field. |
| **Accessibility** | ✅ | Clinical tool — must work for all clinicians; WCAG AA target. |
| **Best Practices** | ✅ | Security, modern code, no console errors, proper meta. |
| **SEO** | ❌ | Local-node lives on `127.0.0.1` inside a clinic, never indexed. The static demo on GitHub Pages is reached via a direct link (the README, the application form), not via search. We don't optimise for Google rank for either surface. |

We only track the three relevant categories below. Any "SEO" checks that are
also useful (meta description, `lang`, viewport) are already enforced by
Accessibility / Best Practices.

## Scores (final, post-optimisations)

Two measurement contexts; both matter for different reasons.

### Throttled · Lighthouse default (Slow 4G + 4× CPU slowdown)

This is the worst-case mobile scenario — useful for the static demo over the
public internet.

| Surface | Performance | Accessibility | Best Practices |
|---|:-:|:-:|:-:|
| **Local Node app** | 90 🟡 | **100** ✅ | **100** ✅ |
| **Static demo** | 90 🟡 | **100** ✅ | **100** ✅ |

### Unthrottled · realistic deployment

This is the real condition for the local-node, which runs on the same Mini PC
as the clinician. Loopback network + native CPU. Also realistic for the demo
when reviewers access it from a stable broadband connection.

| Surface | Performance | Accessibility | Best Practices |
|---|:-:|:-:|:-:|
| **Local Node app** | **100** ✅ | **100** ✅ | **100** ✅ |
| **Static demo** | **100** ✅ | **100** ✅ | **100** ✅ |

The throttled context exists to flag opportunities for low-bandwidth users.
The unthrottled context is what the typical user actually experiences.

## Web Vitals

### Throttled (Slow 4G + 4× CPU)

| Surface | FCP | LCP | SI | CLS | TBT |
|---|:-:|:-:|:-:|:-:|:-:|
| Local Node app | 0.9 s | 2.0 s | 0.9 s | 0 | 0 ms |
| Static demo | 0.9 s | 2.0 s | 0.9 s | 0 | 0 ms |

### Unthrottled (real localhost / cached)

| Surface | FCP | LCP | SI | CLS | TBT |
|---|:-:|:-:|:-:|:-:|:-:|
| Local Node app | 0.1 s | 0.1 s | 0.1 s | 0 | 0 ms |
| Static demo | 0.1 s | 0.1 s | 0.0 s | 0 | 0 ms |

`CLS = 0` and `TBT = 0` are perfect — no layout shift, no main-thread blocking.

## Score evolution (throttled context)

| Iteration | Local-node Perf | Demo Perf | Demo a11y |
|---|:-:|:-:|:-:|
| Baseline | 63 🔴 | 65 🔴 | 96 (1 contrast fail) |
| + Inter font preload + script defer | 74 | 81 🟡 | 96 |
| + Contrast token fix (`--primary-darker`) | 74 | 81 🟡 | **100** ✅ |
| + Inter Variable Latin subset (344 KB → 110 KB) | 89 | 90 ✅ | 100 |
| + GZipMiddleware (29 KB CSS → 6.6 KB on the wire) | 89 | 90 | 100 |
| + 30-day immutable Cache-Control on `/static/*` | 89 | 90 | 100 |
| + `font-display: optional` (no FOUT/FOIT, accept fallback on slow first load) | **90** ✅ | **90** ✅ | 100 |

In unthrottled context all three categories sit at **100/100/100**.

Performance gains came from, in order of impact:

- **Latin font subset**: `pyftsubset` cut the Inter Variable file from 344 KB
  to 110 KB by stripping non-Latin glyphs we don't ship. The
  `--unicodes` ranges are exactly the ones declared in the `@font-face`
  rule, so Spanish accents, smart quotes and the symbol set we use all
  survived. (The full file ships in the proprietary KYNODE platform
  where multi-script support is on the roadmap — for the OSS module
  this trade-off is right.)
- **GZip middleware**: starlette's `GZipMiddleware` compresses everything
  above 500 bytes. On the wire the 29 KB component CSS becomes 6.6 KB.
  ~75 % bandwidth savings on every page load.
- **Cache-Control immutable**: a custom `CachedStaticFiles` subclass marks
  `/static/*` as `public, max-age=2592000, immutable`. The font, CSS, JS
  and icon library all become free on the second-and-later visit. This
  is what production CDNs do automatically; we add it explicitly for
  the bundled uvicorn case.
- **Font preload**: `<link rel="preload" as="font" type="font/woff2"
  crossorigin>` so the browser starts the font fetch in parallel with
  the CSS chain instead of after.
- **Script defer**: `defer` on every `<script>` outside the head
  (`icons.js`, `local-node.js`, `i18n.js`, `demo.js`). The
  theme-bootstrap stays non-deferred because it must run before first
  paint to avoid the dark-mode flash.
- **`font-display: optional`**: keeps Largest Contentful Paint fast on
  the first cold visit by accepting the fallback if Inter doesn't arrive
  in ~100 ms. On every visit after the first, the font is in disk cache
  and Inter renders within the budget. Trade-off: a very-slow first
  visit shows system fonts; a swap-style FOUT was triggering a second
  LCP ~1 s in.

## Performance Trade-offs

The bundled app keeps all browser assets local: no Google Fonts CDN, no runtime
fetch for icons and no external analytics. That offline-first contract adds some
bundle weight, so the work focused on the parts that matter in a clinic:

| Choice | Why it stays |
|---|---|
| Latin-only Inter subset | Keeps the KYNODE visual system while cutting the font from 344 KB to 110 KB. Spanish accents and symbols used by the UI remain covered. |
| `font-display: optional` | Protects first paint and LCP on very slow first loads. The first visit may use system font briefly; later visits use cached Inter. |
| Immutable static cache | Repeat visits inside the clinic should not re-fetch unchanged CSS, JS, icons or fonts. |
| Gzip middleware | Keeps the bundled CSS/JS practical over low-bandwidth clinic LANs. |

The throttled Lighthouse score is 90/100; the realistic loopback/cached score is
100/100. Re-run Lighthouse after any meaningful bundle, typography or caching
change.

## Accessibility deep-dive

Both surfaces hit **100/100**. The accessibility fix in this pass:

- **Demo `signal-strip`**: white text on `--primary-dark` (`#059669` emerald-600)
  failed WCAG AA at 3.76:1 (needs 4.5:1 for normal text). Added a new
  `--primary-darker` token (`#065f46` emerald-800) which yields 6.05:1 against
  white. Same brand colour, just one shade darker.

The rest passed first time:
- Every `<button>` has an accessible name (text or `aria-label`)
- Every interactive element has a focus indicator
- Mobile navigation controls expose correct labels and active states
- Heading hierarchy is sequential
- Form fields have associated labels
- `lang` attribute on `<html>` (and toggled by the i18n switcher)
- Colour is never the only meaningful indicator (icons accompany every status)

## Best-practices

Both surfaces hit **100/100**:

- HTTPS-ready (no mixed content, no `http://` references in code)
- No browser console errors at load
- Proper `<title>`, `<meta description>`, `<meta viewport>`
- `lang` attribute set (and switched by the i18n toggle)
- Sensible `theme-color` for OS chrome (light + dark variants)

## Offline-readiness

Verified by static analysis: zero external HTTP/HTTPS URLs in any of the
served files. The pages can run inside a clinic with the Wi-Fi unplugged
once the bundle has been served once.

```
$ grep -rE 'https?://[^/" )]+' apps/local-node/.../static demo/index.html demo/static/
[no external resource fetches]

$ grep -E "fetch\(['\"]http|XMLHttpRequest" *.js
[no external XHR or fetch]
```

The only outbound network from the local-node app is to its own backend
(`/api/assessments`, `/api/encounters`, etc.), and the demo doesn't talk to a
backend at all (it consumes the pre-generated `data/demo-output.json`).

## Reproducing the audit

```bash
# Terminal 1: start the local-node app
source .venv/bin/activate
uvicorn kynode_pediatric_local_node.app:create_app --factory --port 8080

# Terminal 2: run Lighthouse against it
npx lighthouse@12 http://127.0.0.1:8080/ \
  --chrome-flags="--headless=new" \
  --only-categories=performance,accessibility,best-practices \
  --form-factor=desktop --screen-emulation.disabled \
  --view
```

Same recipe with `python3 -m http.server 8080 -d demo` for the static demo.

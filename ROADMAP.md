# Roadmap

## Where we are: May 2026

This module exists as spec. The first three components are being developed in May 2026 ahead of the [UNICEF Climate & Health 2026](https://www.unicef.org/innovation/call-for-application-climate-and-health-2026) application.

## Components

| Package | What it does | State | Target |
|---|---|---|---|
| `growth-curves` | WHO 2006/2007 z-score percentile calculator | In development | Working state by 2026-05-15 |
| `vaccinations` | Per-country vaccination schedule + reminder logic | In development | Working state by 2026-05-15 |
| `anomaly-detection` | Weekly aggregation + z-score on rolling baseline per zone, for climate-sensitive pediatric indicators | In development | Working state by 2026-05-15 |
| `triage` | Pediatric vital sign ranges by age | Spec stage | After grant decision |
| `imci-rules` | WHO IMCI deterministic danger sign rules | Spec stage | After grant decision |

Each component has its own folder under `docs/components/` with a more detailed spec.

## If UNICEF funding lands

- **Months 1–3** — Finish all five components. Internal testing on the existing Táchira node.
- **Months 4–6** — First field deployments in five medical centers in Venezuela. Onboard community health workers, capture UX feedback, iterate.
- **Months 7–9** — Scale to twelve to fifteen more centers. Public release of v1.0 on this repo, plus CHW training materials in Spanish and English.
- **Months 10–12** — Reach at least twenty active centers in Venezuela. Begin first cross-border deployment in Norte de Santander, Colombia, leveraging the natural Andean continuity with the Táchira region.

## If UNICEF funding does not land

We still build the module. It just takes longer because we juggle it with paying work. Estimated extension: roughly 12 to 18 months for the same scope, depending on what other grants come through.

## What we will not do

- We will not turn this module into a diagnostic engine. It flags. The clinician decides. That line stays.
- We will not embed cloud dependencies in the local components. They must run in a clinic with no internet for weeks. That is the whole point of the design.
- We will not break the public API after v1.0 without a migration path. NGOs and ministries will write integrations against this; stability matters more here than novelty.

## How decisions get made

For now, by the small team that started this. As contributors come in, we'll move toward a lightweight RFC process documented in [CONTRIBUTING.md](CONTRIBUTING.md). For anything that touches clinical logic — triage thresholds, IMCI rules, vaccination schedules — we want at least one clinical reviewer on the PR before it ships.

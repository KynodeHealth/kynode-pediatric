# KYNODE Pediatric

[English](README.md) · [Español](README.es.md)

Open-source pediatric climate-health surveillance, built from the point of care.

This is not another clinic app. KYNODE Pediatric runs on a small computer inside the clinic, no internet required, and turns the workflows that nurses and community health workers already do every day — triage, growth measurement, vaccination, recognition of danger signs — into a real-time signal for climate-sensitive child health: dengue after heavy rains, diarrheal disease after flooding, heat-related illness during heat waves, respiratory outbreaks when air quality drops.

The module sits on top of [KYNODE](https://kynode.io), a proprietary edge health information system that already runs in rural and semi-urban Venezuela. We are releasing the pediatric layer under Apache 2.0 because the population it serves — children under five in disconnected, climate-vulnerable settings — has a stronger case for free access than for revenue capture.

## How it works

Five components, none of which are diagnoses. The module organizes what the clinician already knows how to do, and uses the resulting structured data to feed a surveillance signal upstream.

1. **Pediatric triage.** Vital sign ranges by age. A 2-year-old gets thresholds for a 2-year-old, not the same thresholds we use for an adult. Captures structured data at the front desk — input layer for everything else.
2. **WHO growth curves.** Weight, height and BMI percentiles, calculated locally from the WHO 2006/2007 z-score tables. The tables ship with the package, so it works with no internet. Feeds malnutrition surveillance — acute, chronic, and the climate-amplified kind.
3. **Vaccination schedule.** Configurable per country. Ships with the Venezuelan PAI calendar; PRs welcome for other countries. Feeds coverage and equity-gap surveillance per zone.
4. **IMCI danger sign alerts.** Deterministic rules from the WHO Integrated Management of Childhood Illness protocol. The module flags. The clinician decides. There is no auto-diagnosis here, and there will not be one. First-line outbreak signal at the patient level.
5. **Anomaly detection.** Weekly comparison of aggregated, anonymized indicators per zone against rolling baseline. Flags climate-sensitive disease clusters — dengue, malaria, diarrheal disease, heat-related illness, respiratory outbreaks — before they reach reportable thresholds in the slow monthly system. Statistical, not ML. Fully auditable.

Identifiers are stripped at the node before anything reaches the cloud. Patient PHI never leaves the clinic. Only the surveillance signal travels.

## What's already built

The packages in this repo are not greenfield work. They extract pediatric clinical logic that has been running inside the proprietary KYNODE edge platform for months:

- **WHO Z-Score calculator** with LMS tables — in production in KYNODE since March 2026, used by the clinical calculation flow.
- **Age-banded pediatric vital sign reference ranges** — in production in the KYNODE consultation flow since March 2026.
- **Epidemiological trends radar with weekly aggregation** — in production in our cloud dashboard since March 2026.

What is happening in this repo through May 2026: extracting those three components into standalone, Apache 2.0 packages (`growth-curves`, `triage-ranges`, `anomaly-detection`), writing one new package (`vaccinations`) on top of the Venezuelan PAI calendar, and shipping a small demo web that consumes the four packages end-to-end. A fifth package (`imci-rules`) is fully specified and ships after the grant decision.

We chose to open-source the pediatric layer specifically because the population it serves has the strongest case for free access. The rest of the KYNODE platform (cloud, sync, AI inference pipeline, hardware integration) remains proprietary.

## How this fits with DHIS2, OpenMRS and other existing tools

We are not trying to replace DHIS2, OpenMRS, CommCare or CHT. Those tools are excellent and widely used.

KYNODE Pediatric is for the case those tools handle worst: clinics that go weeks without internet, with no central server within reach, where the data has to live and be useful entirely on a small computer inside the clinic itself, and where the surveillance signal still has to make it upstream when the clinic eventually reconnects.

In practice, KYNODE Pediatric and these tools can coexist. The aggregated weekly signal that the anomaly-detection package produces can be exported to a DHIS2 instance, sent to an OpenMRS dashboard, or pushed to whatever the local health authority already uses. We see ourselves as the offline-first input layer to whatever system is consuming the signal upstream.

## Status

Early development. As of May 2026, this repo contains the spec for all five components, plus the first four (`growth-curves`, `triage-ranges`, `anomaly-detection` and `vaccinations`) in active development with working code and tests. The fifth (`imci-rules`) is in design.

If you found this looking for production-ready software, come back in a few months.

## License

Apache 2.0. See [LICENSE](LICENSE).

## Quick start

This will get you somewhere once the first packages have shipped (target: 2026-05-15):

```bash
git clone https://github.com/<org>/kynode-pediatric
cd kynode-pediatric

# Python components
cd packages/growth-curves
pip install -e .
pytest
```

For now, the more useful entry points are the docs:

- [Architecture](docs/architecture.md) — how the module fits together and where it sits inside KYNODE.
- [Roadmap](ROADMAP.md) — what's built, what's being built, what's planned.
- [Pediatric triage spec](docs/components/01-pediatric-triage.md) — first component spec, gives you a feel for how each one is documented.

## Why open source

Children's health doesn't compete on closed code. It competes on whether the tool actually reaches the clinic. We monetize the rest of KYNODE; this module we give back.

## Who's behind this

A small team based in Caracas and Táchira, Venezuela. We're building KYNODE because in most of the country there isn't a working alternative to a notebook and a pen, and we don't see anyone else solving it from the inside.

## Contact

opensource@kynode.io · [kynode.io](https://kynode.io)

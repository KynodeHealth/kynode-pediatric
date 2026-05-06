# KYNODE Pediatric

[English](README.md) · [Español](README.es.md)

Open-source pediatric climate-health surveillance, built from the point of care.

This is not another clinic app. KYNODE Pediatric runs on a small computer inside the clinic, no internet required, and turns the workflows that nurses and community health workers already do every day — triage, growth measurement, vaccination, recognition of danger signs — into a real-time signal for climate-sensitive child health: dengue after heavy rains, diarrheal disease after flooding, heat-related illness during heat waves, respiratory outbreaks when air quality drops.

The module sits on top of [KYNODE](https://kynode.io), a proprietary edge health information system that already runs in rural and semi-urban Venezuela. We are releasing the pediatric layer under Apache 2.0 because the population it serves — children under five in disconnected, climate-vulnerable settings — has a stronger case for free access than for revenue capture.

## How it works

Five components, none of which are diagnoses. The module organizes what the clinician already knows how to do, and uses the resulting structured data to feed a surveillance signal upstream.

1. **Pediatric triage.** Vital sign ranges by age. A 2-year-old gets thresholds for a 2-year-old, not the same thresholds we use for an adult. Captures structured data at the front desk — input layer for everything else.
2. **WHO growth curves.** Weight, height and BMI percentiles for 0-60 months, calculated locally from a bundled WHO LMS reference table. The alpha ships with compact offline tables and interpolation, so it works with no internet. Feeds growth-status and nutrition surveillance; formal acute malnutrition assessment requires weight-for-height/length or MUAC and is not claimed in this alpha.
3. **Vaccination schedule.** Configurable per country. The alpha ships with a Venezuela reference schedule based on SVPP 2025, pending ministerial validation before field deployment. Feeds coverage and equity-gap surveillance per zone.
4. **IMCI danger sign alerts.** Deterministic rules from the WHO Integrated Management of Childhood Illness protocol. The module flags. The clinician decides. There is no auto-diagnosis here, and there will not be one. First-line outbreak signal at the patient level.
5. **Anomaly detection.** Weekly comparison of aggregated, anonymized indicators per zone against rolling baseline. Flags climate-sensitive disease clusters — dengue, malaria, diarrheal disease, heat-related illness, respiratory outbreaks — before they reach reportable thresholds in the slow monthly system. Statistical, not ML. Fully auditable.

Identifiers are stripped at the node before anything reaches the cloud. Patient PHI never leaves the clinic. Only the surveillance signal travels.

## What's already built

The packages in this repo are not greenfield work. They extract pediatric clinical logic that has been running inside the proprietary KYNODE edge platform for months:

- **WHO Z-Score calculator** with LMS tables — in production in KYNODE since March 2026, used by the clinical calculation flow.
- **Age-banded pediatric vital sign reference ranges** — in production in the KYNODE consultation flow since March 2026.
- **Epidemiological trends radar with weekly aggregation** — in production in our cloud dashboard since March 2026.

What is happening in this repo through May 2026: extracting those three components into standalone, Apache 2.0 packages (`growth-curves`, `triage-ranges`, `anomaly-detection`), writing one new package (`vaccinations`) on top of a public Venezuela immunization reference, and shipping a small demo web that consumes the four packages end-to-end. A fifth package (`imci-rules`) is specified and ships after the grant decision.

We chose to open-source the pediatric layer specifically because the population it serves has the strongest case for free access. The rest of the KYNODE platform (cloud, sync, AI inference pipeline, hardware integration) remains proprietary.

## How this fits with DHIS2, OpenMRS and other existing tools

We are not trying to replace DHIS2, OpenMRS, CommCare or CHT. Those tools are excellent and widely used.

KYNODE Pediatric is for the case those tools handle worst: clinics that go weeks without internet, with no central server within reach, where the data has to live and be useful entirely on a small computer inside the clinic itself, and where the surveillance signal still has to make it upstream when the clinic eventually reconnects.

In practice, KYNODE Pediatric and these tools can coexist. The aggregated weekly signal that the anomaly-detection package produces can be exported to a DHIS2 instance, sent to an OpenMRS dashboard, or pushed to whatever the local health authority already uses. We see ourselves as the offline-first input layer to whatever system is consuming the signal upstream.

## Status

Pre-pilot alpha. As of May 2026, this repo contains four installable offline-ready pediatric packages (`growth-curves`, `triage-ranges`, `anomaly-detection` and `vaccinations`), a bilingual demo that consumes their generated JSON output, and documentation for the architecture and roadmap.

This is a working open-source prototype for review, grant evaluation and technical collaboration. It is not validated clinical field software, not the full WHO IMCI scope and not an end-to-end deployment bundle.

## License

Apache 2.0. See [LICENSE](LICENSE).

## Quick start

Run the alpha locally:

```bash
git clone https://github.com/<org>/kynode-pediatric
cd kynode-pediatric

pip install -e packages/growth-curves
pip install -e packages/triage-ranges
pip install -e packages/anomaly-detection
pip install -e packages/vaccinations

pytest packages/growth-curves/tests
pytest packages/triage-ranges/tests
pytest packages/anomaly-detection/tests
pytest packages/vaccinations/tests

python demo/generate_demo_data.py
python -m http.server 8080 -d demo
```

Then open `http://localhost:8080`.

Useful entry points:

- [Architecture](docs/architecture.md) — how the module fits together and where it sits inside KYNODE.
- [Roadmap](ROADMAP.md) — what's built, what's being built, what's planned.
- [Demo README](demo/README.md) — how to regenerate and serve the bilingual demo.

## Why open source

Children's health doesn't compete on closed code. It competes on whether the tool actually reaches the clinic. We monetize the rest of KYNODE; this module we give back.

## Who's behind this

A small team based in Caracas and Táchira, Venezuela. We're building KYNODE because in most of the country there isn't a working alternative to a notebook and a pen, and we don't see anyone else solving it from the inside.

## Contact

opensource@kynode.io · [kynode.io](https://kynode.io)

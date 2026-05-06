# Architecture

## Where this module sits

KYNODE Pediatric is one module inside the larger KYNODE platform.

KYNODE itself is a proprietary edge health information system built for clinics in fragile-infrastructure settings — the kind of clinic that runs on intermittent power, drops internet for days at a time, and where most consultations are still recorded on paper. The pediatric module is the part of that platform that handles children's care, and it is open source under Apache 2.0.

The reason for this split: we monetize the rest of KYNODE through licensing, support and aggregated data services. The pediatric module we give back to the commons because the population it serves — children under five in low-resource settings — has a stronger case for free access than for revenue capture.

## How the module is organized

Each of the five components lives in its own package. This is on purpose: a pediatric system somewhere else can pull only the parts they need without inheriting the rest.

```
packages/
  growth-curves/         WHO z-score tables + percentile calculator (Python)
  triage-ranges/         Pediatric vital sign reference ranges by age band (Python)
  anomaly-detection/     Weekly aggregation + z-score on rolling baseline per zone (Python)
  vaccinations/          Configurable national schedule + reminder logic (Python)
  imci-rules/            WHO IMCI deterministic alert rules (Python)
```

The Python packages have no shared internal dependency between them. You can pull `growth-curves` into a completely different system and it will work without any other piece of this repo.

## What runs where

| Concern | Where it runs | Why |
|---|---|---|
| Growth curve calculation | Local edge node | Tables are static; calculation is fast; no need for a network round-trip |
| Vaccination reminders | Local edge node | Schedule and patient history both live locally |
| IMCI alerts | Local edge node | Deterministic rules; no AI inference needed |
| Anomaly detection on aggregated indicators | Local node, then cloud | Aggregation and z-score happen at the node; only the surveillance signal travels upstream, with identifiers already stripped |

Patient PHI never leaves the node. The cloud only ever sees aggregated, anonymized counts.

## Why we use AI elsewhere in KYNODE but not in the alerts

KYNODE uses AI for two things in the parent platform: Whisper for Spanish speech-to-text (so a clinician can dictate observations instead of typing them), and Google's MedGemma 4B for clinical note structuring. Both run on the local node. Neither makes diagnostic calls.

For the pediatric danger sign alerts in this module, we deliberately chose **not** to use AI. The reasons:

1. The IMCI protocol is already a well-defined deterministic decision tree. There is no advantage to introducing model uncertainty into a process that has a deterministic correct answer.
2. Auditability matters. A clinician should be able to read why a child got flagged. With deterministic rules they can. With a model they cannot.
3. Children deserve the most conservative engineering choices we can make, and rule-based logic is more conservative than any generative model.

This is not anti-AI. It's about putting the right tool in the right place.

## Cross-platform expectations

The module is designed to run on the same hardware KYNODE already runs on: a small fanless mini-PC (typically AMD Ryzen with 16 GB RAM and SSD storage) inside the clinic. We do not target browsers without a backend, mobile-only deployments, or cloud-native architectures, because none of those work in the connectivity profile we built KYNODE for.

The packages themselves are portable enough that someone could pull `growth-curves` into a Django app or a Flask service or even a CLI tool. We just don't ship those wrappers ourselves.

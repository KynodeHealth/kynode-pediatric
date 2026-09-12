# Usability sessions with primary-care nurses — August 2026

Structured, consent-based usability sessions of the Local Node with three
nurses of a type-III primary-care center in Táriba, Táchira (Venezuela),
run on 6–7 August 2026. Synthetic data only; no patient data was entered.

## Method

- Format: moderated think-aloud walkthrough of the pre-pilot Local Node
  (v0.2.1), one participant at a time, on the clinic's own network.
- Tasks: register a pediatric encounter, read the local assessment, enter
  the weekly surveillance input and climate context, prepare the aggregate
  export.
- Scoring: 5-point scale for perceived usefulness, willingness to use daily
  and ease of use, collected at the end of each session.
- Participants: a nursing-auxiliary coordinator (38 years of experience), a
  professional nurse (21) and a nursing auxiliary (24). Participants are
  not identified in this repository.

## Results

| Measure | Mean (n = 3) |
| --- | --- |
| Perceived usefulness | 4.7 / 5 |
| Willingness to use daily | 4.0 / 5 |
| Ease of use | 3.3 / 5 |

## Barriers observed

The ease-of-use gap came from three recurring barriers, each tracked as a
public issue:

1. **Save confirmations were easy to miss.** The only feedback after saving
   the weekly input or the climate context was a toast that disappeared
   after ~3 seconds; participants re-saved to make sure. → persistent
   "saved at" line under every save button (#11).
2. **Technical terminology** in the Spanish clinical UI (z-score, IMCI,
   aggregate signal) slowed first-time reading. → plain-language glosses
   (#12, extends #2).
3. **Sequence guidance**: the weekly routine (weekly input → climate
   context → export → brief) was not obvious without a moderator. →
   step-sequence guidance (#13, extends #3).

## Limits

Three participants from a single center, synthetic data, moderated
sessions. This is formative usability evidence for the pre-pilot; it is
not a clinical validation and does not measure outcomes.

# Contributing

This is a small project still finding its shape. Contributions are welcome, especially from clinicians, public health professionals, and engineers who have actually worked in low-resource health settings.

## Before you contribute

The clinical logic is the part you have to be careful with. If you're touching:

- **Growth curves** — make sure your numbers match the WHO 2006/2007 z-score tables. Add a test that compares against a known reference value from the WHO documentation.
- **Vaccination schedules** — country calendars are live documents. Cite the source (Ministry of Health publication, version, date) in the PR description and in the schedule file itself.
- **IMCI rules** — work from the WHO IMCI manual, not from memory or general medical knowledge. Reference the manual section in the rule's docstring.
- **Triage thresholds** — pediatric vital sign reference ranges have small variations across published sources. Be explicit about which source you're using.

## What we look for in a PR

- Tests. Every PR that adds or changes logic needs at least one test covering the new behavior. Clinical PRs need at least one test against a published reference value.
- Plain-language docs. The audience downstream of this code includes community health workers, not just engineers. Avoid jargon where you can; when you can't, define it inline.
- Spanish and English both work for issues and PRs. Reviewers are bilingual. If your English is rough, say so in the PR description and we'll help with the wording — what matters is the substance.

## What we don't want

- **Diagnostic features.** The module flags. The clinician decides. PRs that add anything resembling auto-diagnosis will be closed.
- **Cloud-dependent code in the local components.** They must run offline. Anything that needs internet to function belongs in `packages/reports` or outside this repo entirely.
- **Black-box AI inside the alert logic.** Triage and IMCI alerts are deterministic by design. We use AI elsewhere in KYNODE; we keep it out of the alert path because clinicians need to be able to read why a child got flagged.

## Local development

Each package has its own README with setup instructions. Most of them are pure Python and work with a standard `pip install -e .` followed by `pytest`. The triage UI components are in TypeScript and use `npm`.

## Code of Conduct

Be decent to other people. We'll write a longer version when there are more than four of us in here.

## License

By contributing, you agree your contributions will be licensed under Apache 2.0.

## Contact

opensource@kynode.io if you want to talk before opening a PR — useful for anything that touches clinical logic.

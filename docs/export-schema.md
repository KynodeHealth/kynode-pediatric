# Public synthetic export API

KYNODE Pediatric exposes one fixed synthetic weekly aggregate through the public
Local Node demo. The endpoint makes the export contract inspectable without
accepting or exposing real patient data.

This is a **synthetic demonstration surface**. It is not current clinical
activity, an outbreak declaration, field-validation evidence or a feed of real
health records.

## Live synthetic aggregate export

```text
GET https://pediatric.kynode.io/api/export/weekly
```

The public demo accepts only this synthetic scope:

| Query parameter | Required value |
|---|---|
| `zone` | `San Cristobal Norte` |
| `indicator` | `dengue_suspicion` |
| `week` | `2026-W19` |

Open the [prepared JSON response](https://pediatric.kynode.io/api/export/weekly?zone=San%20Cristobal%20Norte&indicator=dengue_suspicion&week=2026-W19)
or inspect it from a terminal:

```bash
curl --fail --silent --show-error \
  'https://pediatric.kynode.io/api/export/weekly?zone=San%20Cristobal%20Norte&indicator=dengue_suspicion&week=2026-W19'
```

Any other zone, indicator or week returns `403` in public demo mode. The runtime
boundary is independently inspectable at
[`GET /api/runtime`](https://pediatric.kynode.io/api/runtime), which reports
`public_demo: true` and `synthetic_only: true`.

## Top-level fields

The current export contract is `schema_version: "0.2.0"`.

| Field | Type | Meaning |
|---|---|---|
| `export_type` | string | Stable contract identifier: `kynode_pediatric_weekly_aggregate`. |
| `schema_version` | string | Version of this aggregate JSON contract. |
| `node` | object | Non-patient node metadata included in the aggregate export. |
| `zone` | string | Aggregate reporting zone. The public value is synthetic. |
| `week` | string | ISO week in `YYYY-Www` format. |
| `indicator` | string | Aggregate surveillance indicator key. |
| `count` | number | Current aggregate count supplied for the zone and week. |
| `baseline_mean` | number | Mean of the historical aggregate counts. |
| `baseline_std` | number | Population standard deviation of the historical counts. |
| `z_score` | number | Standardized difference between the current count and baseline. |
| `flag` | string | `normal`, `insufficient_baseline`, `anomaly` or `anomaly_high_severity`. |
| `severity` | string | Review severity: `low`, `medium` or `high`. |
| `signal_source` | string | Origin of the aggregate input. Public responses use `synthetic_demo`. |
| `climate_context` | object or null | Structured zone/week context; never patient-level weather exposure. |
| `quality_warnings` | array of strings | Explicit limits attached to the pre-pilot signal. |
| `privacy_checklist` | object | Machine-readable confirmation of fields removed before export. |
| `contains_phi` | boolean | Must be `false` for every weekly aggregate export. |

## Node object

| Field | Type | Meaning |
|---|---|---|
| `clinic_name` | string | Local node display name. The public value is synthetic. |
| `node_label` | string | Operational node label, not a patient identifier. |
| `country` | string | Two-letter country code. |

## Climate context object

Climate context is recorded once per zone/week. The system does not infer
causality and does not predict weather.

| Field | Allowed values |
|---|---|
| `rainfall` | `none`, `light`, `moderate`, `heavy`, `unknown` |
| `flooding` | `no`, `reported`, `unknown` |
| `heat_alert` | `no`, `yes`, `unknown` |
| `water_disruption` | `no`, `yes`, `unknown` |
| `vector_risk` | `normal`, `increased`, `unknown` |
| `source` | `clinic_observation`, `community_report`, `authority_bulletin`, `other` |
| `confidence` | `low`, `medium`, `high` |

Free-text climate notes and operator initials remain local and are never present
in this object.

## Privacy checklist

Every key below must be `true`:

| Field | Export guarantee |
|---|---|
| `local_child_id_removed` | Local child identifier is absent. |
| `birth_date_removed` | Date of birth is absent. |
| `vitals_removed` | Patient vital signs are absent. |
| `growth_measurements_removed` | Weight and growth measurements are absent. |
| `vaccination_details_removed` | Individual vaccination records are absent. |
| `clinical_notes_removed` | Clinical free text is absent. |
| `climate_notes_removed` | Climate free text is absent. |
| `operator_initials_removed` | Operator initials are absent. |
| `aggregate_count_only` | The signal contains an aggregate count, not encounter rows. |

Automated tests assert the export boundary, including `contains_phi: false`, the
absence of PHI-like top-level fields and removal of climate notes. See
[`test_export_includes_climate_context_and_excludes_phi`](../apps/local-node/tests/test_local_node.py).

## Intended use

The endpoint demonstrates the publicly accessible mechanism and JSON shape used
by the pre-pilot. A future field deployment may publish periodically synchronized
aggregate signals through the same privacy boundary. Production synchronization,
institutional adapters, threshold calibration and field validation remain out of
scope for this release.

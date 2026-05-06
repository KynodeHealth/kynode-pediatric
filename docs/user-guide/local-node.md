# KYNODE Pediatric Local Node User Guide

English guide. For Spanish, see [local-node.es.md](local-node.es.md).

This guide covers the pre-pilot Local Node workflow:

1. Capture a pediatric encounter locally.
2. Run offline assessment support.
3. Save the encounter in local SQLite.
4. Register weekly aggregate surveillance input.
5. Add weekly climate context.
6. Prepare an aggregate JSON export without PHI.

The Local Node is pre-pilot software. It is not field validated and does not provide autonomous diagnosis.

> Screenshots show the mobile-width layout. The desktop layout uses the same four views: Home, Surveillance, Records and Configuration.

## Start The Node

From the repository root:

```bash
python3 -m pip install -e packages/growth-curves
python3 -m pip install -e packages/triage-ranges
python3 -m pip install -e packages/anomaly-detection
python3 -m pip install -e packages/vaccinations
python3 -m pip install -e apps/local-node

python3 -m kynode_pediatric_local_node
```

Open:

```text
http://localhost:8080
```

The app starts in **Clinic mode**. It does not load synthetic data unless the user explicitly chooses the walkthrough.

![Clinic mode home screen](../assets/user-guide/local-node-01-clinic-home.jpg)

## Home: Capture A Pediatric Encounter

Use **Home** to enter patient-level information that stays on the local device:

- local child ID;
- birth date;
- sex;
- zone;
- week;
- syndrome indicator preview;
- weight and vital signs;
- vaccines received;
- clinical context notes.

Then select **Run local assessment**. The Local Node calculates:

- pediatric vital-sign flags;
- WHO growth status flag;
- vaccination schedule status;
- a syndrome indicator preview.

These outputs are statistical support only. They are not a diagnosis and do not recommend treatment.

![Assessment results after loading a synthetic case](../assets/user-guide/local-node-02-assessment-results.jpg)

Select **Save local encounter** when the encounter should be kept in the local SQLite database.

## Synthetic Walkthrough

Use **Load synthetic walkthrough** only for demos, onboarding or QA.

The walkthrough:

- fills the encounter form with synthetic pediatric data;
- registers a synthetic weekly surveillance input;
- registers synthetic weekly climate context;
- marks the mode and all aggregate signal/export output as synthetic.

Use **Clear synthetic walkthrough** before returning to normal clinic entry.

Clinic mode never loads synthetic data silently.

## Surveillance: Weekly Aggregate Signal

Use **Surveillance** to prepare the zone-level weekly signal.

The weekly surveillance input is aggregate, not per-child:

- zone;
- epidemiological week;
- indicator;
- current aggregate count;
- baseline weekly counts.

Climate context is a structured local observation for the same zone/week:

- rainfall;
- flooding;
- heat alert;
- water disruption;
- vector risk;
- source;
- confidence;
- local-only notes.

The pre-pilot does not call a weather API, does not predict weather and does not claim causal attribution between climate context and cases.

After the weekly input exists, select **Prepare weekly aggregate export**. The Local Node generates the signal, shows the trend and prepares the privacy-safe aggregate JSON.

![Weekly aggregate signal and export readiness](../assets/user-guide/local-node-03-surveillance-export.jpg)

## Export Privacy Boundary

The export is designed for zone-level signal sharing. It must not contain:

- child ID;
- birth date;
- individual vitals;
- weight or per-child growth measurements;
- vaccination details;
- clinical notes;
- climate notes;
- operator initials.

The UI shows a privacy checklist before the aggregate export is shared.

Allowed export content includes:

- node identity;
- zone;
- week;
- indicator;
- aggregate count;
- baseline statistics;
- signal flag and severity;
- structured climate context without notes;
- quality warnings;
- privacy checklist.

## Records: Local History And Audit Trail

Use **Records** to review saved local encounters and operational events.

The audit trail stores operational metadata only. It records events such as node setup changes, encounter saves, weekly input saves, climate context saves and aggregate export preparation.

![Local records and audit trail](../assets/user-guide/local-node-04-records-audit.jpg)

## Configuration

Use **Configuration** for node identity and local preferences.

Node identity fields are used in aggregate exports:

- clinic name;
- node label;
- country;
- operator initials.

The page also shows the current pre-pilot operating limits:

- local SQLite storage only;
- no cloud sync configured;
- v0.2.0-prepilot-local-node;
- backup-and-recreate schema policy during pre-pilot.

![Configuration and operational status](../assets/user-guide/local-node-05-configuration.jpg)

## Current Limits

This pre-pilot Local Node intentionally does not include:

- login or role management;
- cloud sync;
- weather API integration;
- CSV import;
- DHIS2/OpenMRS adapters;
- full WHO IMCI rule engine;
- field-calibrated thresholds.

Those are grant-funded productization items.

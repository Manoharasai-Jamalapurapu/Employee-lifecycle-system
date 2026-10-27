# Employee Lifecycle Operations System

A synthetic-data demonstration for HR onboarding/offboarding coordination across HR, IT, facilities and managers. It demonstrates relational data modeling, dependency-aware tasks, access approvals and revocation, asset tracking, labelled exception scenarios, audit events, SLA metrics, and deterministic dataset generation.

> **Safety and scope:** All names, emails, IDs, and records are synthetic. This project is a demonstration only; it does not connect to real HR, IT, identity, or facilities systems. It does not execute real access changes.

## Features

- Deterministic generator (default seed `20261022`) with parameterized scale.
- 8 departments, 12 roles, 50 managers, 500 employees and onboarding cases, 4,000 task instances, 600 assets, and 300 access requests by default.
- CSV and JSON exports, separate `evaluation/ground_truth.csv`, checksums and generation summary.
- Task dependency field and rule checks, overdue/SLA calculations, manager-missing detection, asset-conflict detection, terminated-user access risk detection.
- Streamlit dashboard with KPIs, charts, exception filters, searchable employee/task data and CSV exception export.
- SQL schema, data dictionary, validation script and tests.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python -m generator.generate
python -m validation.validate_data
pytest -q
streamlit run app.py
```

Open the local URL shown by Streamlit.

## Regenerate data

```bash
python -m generator.generate --seed 20261022
python -m generator.generate --seed 20261022 --employees 50 --cases 50 --tasks 400 --assets 60 --access-requests 30
```

The default full dataset produces the requested scale. The starter example reduces the volume but uses the same generation code. To test reproducibility, run generation twice using the same seed and compare `reports/checksums.json`. The generator writes deterministic synthetic data; timestamps and generated CSV contents are stable for a fixed configuration.

## Data model

- `Department` 1:N `Employee`, `Manager`, and `Role` (role default department).
- `Role` 1:N `Employee`.
- `Manager` 1:N `Employee` and task assignments; employee manager is optional to allow a labelled exception.
- `Employee` 1:N `OnboardingCase`, `TaskInstance`, `Asset` assignment history concept, `AccessRequest`, and `OffboardingCase`.
- `OnboardingCase` 1:N `TaskInstance`.
- `TaskTemplate` 1:N `TaskInstance`.
- `TaskInstance` may depend on another task instance; dependency graph should be acyclic.
- `AccessRequest` 1:N `Approval`.
- `AuditEvent` stores append-only state/event history. For a production system, add explicit bridge tables for multi-system roles/assets and time-versioned employee department assignments.

The schema file documents the core SQL constraints. CSVs are convenient exports, while the SQL schema is the relational model reference.

## Important business rules

1. A task that has a prerequisite cannot be considered compliant until the prerequisite is complete.
2. Provision access only after the required approvals; do not treat a pending request as approved.
3. For terminated employees, any provisioned access not marked revoked is a critical exception.
4. Calculate overdue days from due date and a supplied evaluation date; do not generate SLA labels independently.
5. Preserve historical changes as events rather than erasing previous values.
6. Ground-truth anomaly labels are stored separately from feature data.

## Anomaly scenarios included

- Task completed before prerequisite.
- Employee with missing manager.
- Asset assignment conflict.
- Employee starts before background check is complete.
- Terminated employee with active, unrevoked access.
- Overdue task / SLA breach.
- Department change during process (recorded as an audit event).

`evaluation/ground_truth.csv` documents expected decisions. Ground truth must not be fed into a detection rule or model as an input feature.

## Validation

Run:

```bash
python -m validation.validate_data
pytest -q
```

The validation summary is written to `reports/validation_summary.json`. It checks primary-key uniqueness and the implemented foreign-key references. Expand validation before submission to cover every enum, lifecycle transition, dependency cycle, access-before-approval case, date ordering and arithmetic reconciliation.

## Evaluation metrics

Recommended metrics for your final report:
- Referential integrity pass rate.
- Dependency violation count.
- Access requests provisioned before approval (target: 0).
- Terminated users with active access.
- SLA breach count and overdue days.
- Anomaly precision, recall and F1 compared with `evaluation/ground_truth.csv`.
- Reproducibility: row counts and SHA-256 checksums from two identical runs.

Do not claim metrics are perfect unless validation actually demonstrates it. This is a starter implementation and should be reviewed and tested before submission.

## Lawful provenance

No external dataset is used. All records are generated locally from synthetic rules. No real personal or confidential data is included.

## GitHub upload

1. Create a new **public or private** GitHub repository.
2. Extract this project ZIP.
3. Upload the project folder contents (ensure `README.md` is at repository root), or use Git:

```bash
git init
git add .
git commit -m "Build employee lifecycle operations system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL. Never upload credentials, tokens, real employee data, or private company information.

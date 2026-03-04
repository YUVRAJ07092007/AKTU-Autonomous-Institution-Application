# Testing Report — AKTU Autonomy Portal

*Copy this template, fill in the sections below, and save as e.g. `docs/reports/TESTING_REPORT_YYYY-MM-DD.md`. See [TESTING_GUIDE.md](TESTING_GUIDE.md) for scenario details.*

---

## Process report

**Build / version:** Record once here; do not duplicate BASE_URL or auth elsewhere in the report.

| Field | Value |
|-------|--------|
| **Report date** | *(YYYY-MM-DD)* |
| **Tester name** | |
| **Git branch** | *(e.g. `main`)* |
| **Git commit hash** | *(e.g. output of `git rev-parse HEAD`)* |
| **Release tag (if any)** | |
| **BASE_URL tested** | *(e.g. `http://127.0.0.1:8000` or ngrok URL — single source for this run)* |
| **Environment — OS** | |
| **Environment — Python version** | |
| **Environment — Node version** | |
| **Environment — DB path** | *(e.g. path to SQLite file, or "in-memory" for pytest)* |
| **Seed data used?** | *(Yes / No)* |
| **Seed command** | *(if used: e.g. `PYTHONPATH=backend python backend/scripts/seed_synthetic_data.py`)* |
| **Seed script output summary / version tag** | *(if used: one-line summary from script printout or version tag)* |
| **Test execution** | *(Manual / Automated / Both)* |
| **Automated command(s)** | *(e.g. `pytest`, script name, or N/A)* |
| **Manual reference** | *(e.g. TESTING_GUIDE sections 5–7)* |
| **Duration** | |
| **Notes** | |

---

## Product report

**Test scope:** *(e.g. "API with synthetic data", "pytest suite", "frontend build", "manual Swagger smoke")*

### Test scenarios / cases

| Scenario ID | Description | Expected result | Actual result | Pass/Fail |
|-------------|-------------|-----------------|---------------|-----------|
| 1 | *(e.g. Login as Institution, list applications)* | *(e.g. 200, list of apps)* | | |
| 2 | | | | |
| *(add rows as needed)* | | | | |

**On failure:** For any failed scenario, record **step number**, **HTTP status code**, and **response body or error message** below and in the Summary.

### Failures / deviations (if any)

| Failure ID | Scenario ID | Step # | Endpoint / action | Expected | Actual | HTTP | Evidence (log/screenshot path) |
|------------|-------------|--------|-------------------|----------|--------|------|-------------------------------|
| F-001 | *(e.g. SCN-03)* | *(e.g. 4)* | *(e.g. `POST /api/applications/{id}/decision`)* | *(e.g. 409 invalid transition)* | *(e.g. 200 OK)* | *(e.g. 200)* | *(e.g. `logs/backend.log` or screenshot)* |
| *(add rows as needed)* | | | | | | | |

### Summary

| | Count |
|---|-------|
| **Passed** | |
| **Failed** | |
| **Skipped** | |

*(Optional: coverage or area summary)*

### Defects / observations

| ID | Description | Severity |
|----|-------------|----------|
| | | *(High / Medium / Low)* |
| *(add rows as needed)* | | |

### Evidence links / attachments

*(So every report is debuggable.)*

| Item | Value |
|------|--------|
| **BASE_URL tested** | *(same as Process report; do not duplicate)* |
| **OpenAPI snapshot** | *(e.g. `/openapi.json` saved as `artifacts/openapi-YYYY-MM-DD.json` or N/A)* |
| **Seed output log** | *(path or paste one-line summary)* |
| **Backend log path** | *(if captured)* |
| **Frontend console log** | *(if captured)* |

---

*End of report.*

# Testing Report — AKTU Autonomy Portal

*Copy this template, fill in the sections below, and save as e.g. `docs/reports/TESTING_REPORT_YYYY-MM-DD.md`. See [TESTING_GUIDE.md](TESTING_GUIDE.md) for scenario details.*

---

## Process report

| Field | Value |
|-------|--------|
| **Report date** | *(YYYY-MM-DD)* |
| **Tester name** | |
| **Environment — OS** | |
| **Environment — Python version** | |
| **Environment — Node version** | |
| **Environment — DB path** | *(e.g. path to SQLite file, or "in-memory" for pytest)* |
| **Seed data used?** | *(Yes / No)* |
| **Seed command** | *(if used: e.g. `PYTHONPATH=backend python backend/scripts/seed_synthetic_data.py`)* |
| **Seed script output summary** | *(if used: one-line summary from script printout)* |
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

**On failure:** For any failed scenario, record **step number**, **HTTP status code**, and **response body or error message** in the Notes or in a separate "Failures" table below.

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

---

*End of report.*

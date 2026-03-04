# AKTU Autonomy Portal — Testing Guide

This guide explains how to run the app, load synthetic data, perform manual testing, and run automated tests. For the full testing and validation plan (scenarios, report, known issues), see [TESTING_AND_VALIDATION_PLAN.md](TESTING_AND_VALIDATION_PLAN.md).

---

## 1. Overview

For **developers and testers**. Two ways to test:

- **Manual:** Swagger API and optional frontend, optionally with synthetic data.
- **Automated:** Backend pytest, frontend lint/build, optional Playwright e2e; CI runs on push/PR.

---

## 2. Prerequisites

- **Backend:** Python 3.10+, `backend/.env` (or env vars). Required: `JWT_SECRET`. Optional: `AKTU_DB_PATH`, `UPLOAD_DIR`. SQLite.
- **Frontend:** Node 18+, `frontend/.env.local` with `NEXT_PUBLIC_API_BASE_URL` pointing to the backend.
- **Colab:** GitHub PAT (repo scope), ngrok authtoken (free account). See [README](../README.md) and `.env.example` for setup.

---

## 3. Running the application

- **Backend in Colab:** Open [colab/AKTU-Autonomous-Institution-Application_run_backend_colab.ipynb](../colab/AKTU-Autonomous-Institution-Application_run_backend_colab.ipynb) (or use **Open in Colab** from the README). Run cells: optional delete DB → mount Drive + clone/pull + migrations → Uvicorn + ngrok. Use the printed public URL as base URL.
- **Backend locally:** From repo root: `cd backend`, create venv, `pip install -r requirements.txt`, set `JWT_SECRET` and optional `AKTU_DB_PATH`, `alembic upgrade head`, `uvicorn app.main:app --host 0.0.0.0 --port 8000`. Base URL: `http://127.0.0.1:8000`.
- **Frontend (optional):** `cd frontend`, `npm install`, set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` to backend URL, `npm run dev`. Open http://localhost:3000.
- **Where data lives:** Colab with Drive → `My Drive/aktu_autonomy/` (DB + uploads). Local → `AKTU_DB_PATH` and `UPLOAD_DIR` from env.

---

## 4. Synthetic data for manual testing

When the seed script is available (`backend/scripts/seed_synthetic_data.py`), run it **after** `alembic upgrade head` to load:

- **2 institutions** (e.g. Synthetic College A/B).
- **6 users** — one per role (INSTITUTION x2, DEALING_HAND, REGISTRAR, COMMITTEE, AUTHORITY, ACCOUNTS) with a shared password (e.g. `Test@123`).
- **2–3 applications** in different workflow statuses (e.g. DRAFT, SUBMITTED_ONLINE, HARDCOPY_RECEIVED).

**How to run the seed (when available):** From repo root, set `ENV=dev` (or unset), set `JWT_SECRET`, optionally `AKTU_DB_PATH`. Then:

```bash
PYTHONPATH=backend python backend/scripts/seed_synthetic_data.py
```

The script prints a **table of seeded users** (email, role, password) and a short summary (e.g. "Institutions: 2, Users: 6, Applications: 3"). Use that table to log in as Authority, Registrar, etc.

**Application–institution mapping:** Each INSTITUTION user sees only their institution’s applications. The seed output or this guide will state which user sees which application(s) (e.g. College A user sees apps X, Y; College B sees app Z).

**Verifying seed data:** The seed script runs a self-check and exits with code 1 if counts or role/status coverage are wrong. A successful run prints the summary and status list. Optional: after starting the backend, log in via Swagger with a seeded user and call `GET /api/applications/` to confirm 2–3 applications appear.

**Known issues:** Run seed once on an empty DB (or reset by deleting the DB file and running `alembic upgrade head`). Never use seed or shared password in production. The shared password is weak by design for dev only. After model/migration changes, update the seed script if needed. Document-upload scenarios may require manual upload if no document seed. For clean state: remove DB file, run migrations, run seed again. Colab: DB path on Drive; local: `AKTU_DB_PATH`.

**Note:** Pytest uses an in-memory DB and creates its own data; the seed is not used in CI.

---

## 5. Manual testing — API (Swagger)

1. Open `{BASE_URL}/docs` (e.g. ngrok URL or http://127.0.0.1:8000/docs).
2. **Register (optional):** `POST /api/auth/register` with email, password, name, role (e.g. INSTITUTION). Or use a seeded user.
3. **Login:** `POST /api/auth/login` with email/password; copy `access_token`.
4. **Authorize:** In Swagger, click **Authorize**, enter `Bearer <access_token>`.
5. **Smoke checks:** `GET /api/health`, `GET /api/health/live`, `GET /api/applications/`, `POST /api/applications/` (create draft).

---

## 6. Manual testing — Frontend

With the backend running and `NEXT_PUBLIC_API_BASE_URL` set: open the app, log in (seeded user or registered), open dashboard, create or view applications, check status timeline. For full workflow (committee, MoM, decision), use Swagger or frontend and follow role-based flows.

---

## 7. Testing the software with synthetic data (suitably)

Use the seeded users and applications to run a structured procedure. **On failure,** record: step number, HTTP status code, response body or error message (see [TESTING_REPORT_TEMPLATE.md](TESTING_REPORT_TEMPLATE.md)).

### By role

| Role | Example scenarios |
|------|-------------------|
| **Institution** | Log in; list my applications; create draft; submit online (DRAFT → SUBMITTED_ONLINE). |
| **Dealing Hand** | Log in; list applications; transition HARDCOPY_RECEIVED → UNDER_SCRUTINY (or SCRUTINY_CLEARED). |
| **Registrar** | Log in; constitute committee for an application in SCRUTINY_CLEARED. |
| **Committee** | Log in; add meeting; generate MoM draft for an application in MEETING_SCHEDULED. |
| **Authority** | Log in; issue decision for an application in MOM_FINALIZED. |
| **Accounts** | Log in; list applications / role-specific actions per product scope. |

### By feature

- **Health:** `GET /api/health`, `GET /api/health/live`.
- **Auth:** Login/register with seeded credentials.
- **Applications CRUD:** List, create, get by id (use seeded application ids; institution users see only their institution’s apps).
- **Workflow transitions:** Use seeded applications and their statuses; only valid transitions (e.g. HARDCOPY_RECEIVED → UNDER_SCRUTINY by Dealing Hand). See workflow rules in the codebase.
- **Documents:** Upload/list; seeded apps may have no documents—manual upload or optional metadata seed.
- **Committee / Meeting / MoM / Decision:** If in scope; use applications in COMMITTEE_CONSTITUTED, MEETING_SCHEDULED, MOM_FINALIZED as appropriate.

### Negative scenarios

- Institution user cannot transition another institution’s application (expect 403 or 404).
- Authority cannot move DRAFT → DECISION_ISSUED (invalid transition; expect 4xx).
- Wrong role for a transition returns 403.

---

## 8. Automated tests

**Backend (from `backend/`):**

```bash
export ENV=test
export JWT_SECRET=test-secret
pytest
```

Optional: `ruff check app tests`, `black --check app tests`.

**Test modules:** test_auth_rbac, test_application_workflow, test_document_uploads, test_committee_office_order, test_meeting_notice, test_mom, test_decision, test_health, test_config, test_security, test_db_basic, test_workflow_transitions.

**Frontend (from `frontend/`):** `npm run lint`, `npm run build`. Optional: `npx playwright install`, then `npm run test:e2e`.

**CI:** [.github/workflows/ci.yml](../.github/workflows/ci.yml) runs backend (ruff, black, pytest) and frontend (lint, build) on push/PR; optional Playwright job.

---

## 9. Quick test checklist

- [ ] Backend live (`GET /api/health/live`).
- [ ] (Optional) Seed data loaded; login as seeded user.
- [ ] Register + Login + Authorize in Swagger; list applications; create application if desired.
- [ ] Run `pytest` in `backend/` for full backend coverage.
- [ ] Run `npm run build` in `frontend/` for frontend build.

---

*See [TESTING_AND_VALIDATION_PLAN.md](TESTING_AND_VALIDATION_PLAN.md) for the full plan and [TESTING_REPORT_TEMPLATE.md](TESTING_REPORT_TEMPLATE.md) for the report template.*

# AKTU Academic Autonomy Portal — Cursor Prompt Pack
**Target:** Professional web app (Frontend + Backend) for AKTU autonomy applications  
**Environment:** Google Colab-first (no Docker required for MVP)  
**Repo:** Private GitHub monorepo `aktu-autonomy-portal/`  
**Date:** 2026-03-03

## Non‑negotiables (apply to every task)
- Write code that runs in **Google Colab** (Linux), and locally on Windows if possible.
- Use **FastAPI** backend; **SQLite** for MVP (DB file stored in Google Drive mount).
- File uploads stored under a configurable directory (default: Drive mount path).
- Strict **RBAC** and **audit logs** for all actions.
- No secrets committed. Use `.env` locally and `os.environ` in Colab.
- Add **validation** (Pydantic) and **tests** (pytest) for each module.
- Prefer **pure Python** libs; avoid system dependencies where possible.
- Provide concise run steps in `README.md` and in `colab/run_backend_colab.ipynb`.

## Coding standards
- Python 3.10+
- Type hints everywhere.
- Black + Ruff formatting/lint.
- HTTP errors must be meaningful (status + message).
- Every endpoint must enforce authorization and log audit events.

---

## Task
Create database schema (SQLite) and ORM models.

### Tech
- SQLAlchemy 2.0 style + Alembic migrations (works in Colab).

### Entities (minimum)
1. `User`
   - id, email, name, hashed_password, role
   - role enum: INSTITUTION, DEALING_HAND, REGISTRAR, COMMITTEE, AUTHORITY, ACCOUNTS (optional)
2. `Institution`
   - id, name, code, address, district, contact_email, contact_phone
3. `Application`
   - id (UUID), institution_id, status, created_at, updated_at
   - core fields: requested_from_year, programmes_json, ugc_policy_mode (A/B)
4. `DispatchTracking`
   - id, application_id, speedpost_no, akt_diary_no, received_date, remarks
5. `Document`
   - id, application_id, doc_type enum (CoverLetter, ApplicationForm, AnnexureIA, AnnexureII, AnnexureIII, AnnexureIV, AnnexureV, AnnexureVII, FeeProof, OfficeOrder, MoM, DecisionLetter, UGCApproval)
   - filename, storage_path, uploaded_by, uploaded_at, version, sha256
6. `AuditLog`
   - id, actor_user_id, action, entity_type, entity_id, timestamp, ip, details_json

### Deliverables
- SQLAlchemy models + Alembic init + first migration
- DB session dependency injection for FastAPI

### Tests
- Create an in-memory sqlite test; create tables; insert minimal records.

### Acceptance
- `alembic upgrade head` works in Colab.
- Basic CRUD works via tests.

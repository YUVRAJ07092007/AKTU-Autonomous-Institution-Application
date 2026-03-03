# AKTU Academic Autonomy Portal — Cursor Prompt Pack
**Target:** Professional web app (Frontend + Backend) for AKTU autonomy applications  
**Environment:** Google Colab-first (no Docker required for MVP)  
**Repo:** https://github.com/YUVRAJ07092007/AKTU-Autonomous-Institution-Application  
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
Implement the Application lifecycle with strict status transitions and server-side enforcement.

### Status Enum
- DRAFT
- SUBMITTED_ONLINE
- HARDCOPY_DISPATCHED (optional intermediate)
- HARDCOPY_RECEIVED
- UNDER_SCRUTINY
- DEFICIENCY_RAISED
- SCRUTINY_CLEARED
- COMMITTEE_CONSTITUTED
- MEETING_SCHEDULED
- MOM_DRAFT_GENERATED
- MOM_FINALIZED
- DECISION_ISSUED
- CLOSED

### Deliverables
- Transition guard function `can_transition(from, to, role)`
- API endpoints:
  - `POST /api/applications` create draft (institution)
  - `PATCH /api/applications/{id}` update draft fields
  - `POST /api/applications/{id}/submit` -> SUBMITTED_ONLINE
  - `POST /api/applications/{id}/dispatch` -> record speedpost
  - `POST /api/applications/{id}/receive` -> record diary no and received date (dealing hand)
  - `POST /api/applications/{id}/deficiency` -> raise deficiency (dealing hand)
  - `POST /api/applications/{id}/scrutiny-clear` -> SCRUTINY_CLEARED (dealing hand)
- Always write `AuditLog` on status changes with details.

### Validation
- Cannot skip mandatory annexures before submit.
- Cannot issue decision unless MoM finalized.

### Tests
- Transition tests for allowed/forbidden paths.

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
Implement meeting notice creation + notifications for online/offline/hybrid.

### Deliverables
- DB: `Meeting` (application_id, mode, date_time, venue, online_link, agenda, created_by)
- Endpoint:
  - `POST /api/applications/{id}/meetings` create notice (registrar)
  - `GET /api/applications/{id}/meetings` list
- Auto-notify committee members (email stub ok).
- Store meeting notice as a generated DOCX/PDF document (Document type = MeetingNotice).

### Tests
- Only registrar can schedule meeting.
- Meeting visible to committee members; institution visibility configurable (default OFF).

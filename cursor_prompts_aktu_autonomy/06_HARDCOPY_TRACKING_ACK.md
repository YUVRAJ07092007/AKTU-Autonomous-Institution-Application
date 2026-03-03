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
Implement hardcopy dispatch + AKTU inward acknowledgement flow.

### Deliverables
- Fields on Application or separate model `DispatchTracking`:
  - speedpost_no, dispatch_date
  - akt_diary_no, received_date, received_by_user_id
- API endpoints:
  - Institution: `POST /api/applications/{id}/dispatch` (speedpost)
  - AKTU: `POST /api/applications/{id}/ack-received` (diary + date)
- Auto-generate an Acknowledgement PDF/DOCX (optional MVP) containing:
  - Application ID, institution name, received date, diary no.
  - Store as Document type = ACK

### Tests
- Institution can set speedpost only before hardcopy received.
- Only dealing hand can ack received.

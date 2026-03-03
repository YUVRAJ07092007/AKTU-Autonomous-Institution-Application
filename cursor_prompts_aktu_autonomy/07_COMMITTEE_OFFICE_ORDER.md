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
Implement committee formation workflow and Office Order generation.

### Deliverables
- DB: `Committee` table linked to Application with members list (many-to-many `CommitteeMember`)
- Endpoint for Registrar/Authority:
  - `POST /api/applications/{id}/committee` create committee draft (members, roles: chair/convener/member)
  - `POST /api/applications/{id}/committee/approve` (authority) -> COMMITTEE_CONSTITUTED
- Office Order generator:
  - DOCX template with placeholders: OfficeOrderNo, Date, InstitutionName, ApplicationID, Members list
  - Generate DOCX + PDF (optional) and store as Document type = OfficeOrder

### Notification
- Email notifications to members (stub SMTP for MVP; log-only ok).

### Tests
- Authority required for approval.
- Document created and saved.

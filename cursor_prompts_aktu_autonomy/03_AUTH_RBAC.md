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
Implement authentication + role-based access control.

### Deliverables
- Auth endpoints:
  - `POST /api/auth/register` (admin-only or bootstrap script)
  - `POST /api/auth/login` -> JWT access token
  - `GET /api/auth/me`
- Dependency helpers:
  - `get_current_user`
  - `require_roles([...])`

### RBAC rules (MVP)
- INSTITUTION: can create/submit/view ONLY its own applications and upload its own docs until “Hardcopy Received”.
- DEALING_HAND: can view all, set diary number, mark received, raise deficiency, move status to scrutiny cleared.
- REGISTRAR: can schedule meeting, forward to authority, manage committee workflow.
- AUTHORITY: can approve committee formation + issue final decision.
- COMMITTEE: can view docs for assigned cases and edit MoM drafts.
- ACCOUNTS (optional): can verify fee/payment fields.

### Security requirements
- Password hashing.
- JWT expiry.
- Audit log for login and role-restricted access attempts.

### Tests
- Auth flow tests (register/login/me)
- RBAC tests: forbidden access returns 403.

### Acceptance
- A user with INSTITUTION cannot access another institution's application.

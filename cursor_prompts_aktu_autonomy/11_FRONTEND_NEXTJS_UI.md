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
Implement Next.js frontend with role-based dashboards and forms.

### Deliverables
- Auth pages: login
- Institution dashboard:
  - create application, fill AKTU fields, upload docs, submit, enter speedpost, track status
- AKTU dashboard (dealing hand):
  - receive hardcopy (diary no), scrutiny checklist, raise deficiency, clear scrutiny
- Registrar dashboard:
  - form committee draft, schedule meetings, start MoM draft
- Committee workspace:
  - view documents, edit MoM sections, finalize
- Authority dashboard:
  - approve committee, issue decision

### UI requirements
- Use a component library (e.g., MUI) for speed and consistency.
- Show application status timeline.
- File upload component supports doc_type selection and version.
- API base URL configurable via env (supports ngrok).

### Frontend tests
- Basic unit tests (Jest) or Playwright smoke test (optional MVP).

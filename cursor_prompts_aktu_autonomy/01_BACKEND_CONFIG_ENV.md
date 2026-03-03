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
Implement robust backend configuration for Colab and local dev.

### Deliverables
- `backend/app/core/config.py` using Pydantic Settings:
  - `ENV` (dev/prod)
  - `DATABASE_URL` (default sqlite path)
  - `UPLOAD_DIR` (default `/content/drive/MyDrive/AKTU_Autonomy_Uploads` in Colab, else `./data/uploads`)
  - `BASE_URL` (used for links)
  - `JWT_SECRET` (required; read from env)
  - `NGROK_PUBLIC_URL` (optional)
- `backend/app/core/logging.py` structured logging (JSON preferred)
- `backend/app/core/security.py` JWT helpers (HS256), password hashing (passlib bcrypt)

### Validation
- Fail fast if `JWT_SECRET` missing in non-test environments.
- Ensure directories are created on startup.

### Tests
- Unit tests for config loading (test env defaults).
- Unit tests for JWT encode/decode.

### Acceptance
- Running `uvicorn app.main:app` in Colab starts without errors and creates upload directory.

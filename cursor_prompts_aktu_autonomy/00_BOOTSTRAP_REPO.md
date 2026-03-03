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
Create a production-grade monorepo skeleton for the AKTU Academic Autonomy Portal.

### Deliverables
1. Repo structure:
   - `backend/` (FastAPI)
   - `frontend/` (Next.js)
   - `colab/` (notebooks/scripts to run backend)
   - `docs/` (workflow + API contract)
2. Tooling:
   - `backend/pyproject.toml` with dependencies + dev tools (pytest, ruff, black, mypy optional)
   - `backend/requirements.txt` (generated or maintained)
   - `frontend/package.json` with scripts
   - `.env.example` at repo root
   - `.gitignore` (Python + Node + Colab + secrets)
3. Minimal working backend:
   - `GET /api/health` returns `{status:"ok", service:"aktu-autonomy-portal"}`
4. Minimal working frontend:
   - Home page with “API base URL” read from env and a health-check button.
5. Colab runner:
   - `colab/run_backend_colab.ipynb` that clones repo, installs deps, mounts Drive, runs FastAPI, starts ngrok, prints public URL.

### Constraints
- No Docker required for MVP; optional Dockerfile later.
- All commands must work in Colab.

### Acceptance tests
- `pytest` passes (at least 1 test for health endpoint).
- `ruff` passes (or documented baseline).
- From Colab, user can open ngrok URL + `/api/health` works.

### Notes
- Keep code minimal but clean.

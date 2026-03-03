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
Make the entire project runnable in Google Colab (backend + minimal frontend preview).

### Deliverables
- `colab/run_backend_colab.ipynb`
  - Drive mount
  - Clone/pull private GitHub repo (token from input)
  - Install deps
  - Run alembic migrations
  - Start uvicorn
  - Start ngrok and print URL
- `colab/run_frontend_preview_colab.ipynb` (optional)
  - Install node
  - Start Next.js dev server
  - Use ngrok to expose frontend
- Documentation in README: exact cells/commands.

### Ngrok in Colab (apply in all future Colab runbooks)
- **Ngrok requires a verified account and authtoken.** Do not assume unauthenticated ngrok; it will fail with `ERR_NGROK_4018`.
- In any notebook cell that calls `ngrok.connect()`:
  - **Prompt for the authtoken** if not set (e.g. `os.environ.get("NGROK_AUTHTOKEN")` or `getpass.getpass(...)`), then call `ngrok.set_auth_token(token)` before `ngrok.connect()`.
  - Add a **markdown cell immediately before** that code cell titled e.g. **"Where to paste your ngrok authtoken"** explaining: when you run the next cell, an input box appears in the **output area below the cell**; paste your authtoken there and press Enter. Link to https://dashboard.ngrok.com/get-started/your-authtoken.
  - Use a **clear prompt string** in `getpass.getpass(...)` e.g. "Ngrok authtoken — paste in the box below and press Enter:" so users know exactly where to paste.
- In README/instructions, mention that users need a free ngrok account and must paste the authtoken when the notebook asks for it.

### Acceptance
- A user can run backend fully from Colab without manual Linux setup.

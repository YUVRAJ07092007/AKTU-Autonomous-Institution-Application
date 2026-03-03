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
Implement document upload/download system with strong validation and metadata.

### Deliverables
- Endpoint: `POST /api/applications/{id}/documents` multipart upload
  - fields: doc_type, version (optional), notes
- Endpoint: `GET /api/documents/{doc_id}` download (RBAC)
- Store file to `UPLOAD_DIR/{application_id}/{doc_type}/...`
- Compute sha256, save metadata in DB.
- Validate:
  - allowed extensions: pdf, docx, xlsx (if needed), png/jpg for scans
  - file size limit (configurable)
  - required docs list at submission time (AKTU core)
- Optional: basic PDF page size check (A4) if feasible, else log warning.

### Tests
- Upload/download happy path
- Unauthorized download blocked
- Required-doc validation blocks submission if missing

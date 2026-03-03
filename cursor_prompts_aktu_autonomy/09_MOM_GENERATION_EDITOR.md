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
Implement Minutes of Meeting (MoM) auto-draft generation + collaborative editing.

### Deliverables
- MoM template aligned to AKTU Clause 6.29(a) / 6.29(d) style (DOCX placeholders).
- Endpoint:
  - `POST /api/applications/{id}/mom/draft` -> generates draft DOCX, status MOM_DRAFT_GENERATED
  - `PUT /api/applications/{id}/mom/content` -> save structured MoM sections (JSON) with versioning
  - `POST /api/applications/{id}/mom/finalize` -> render final DOCX/PDF, status MOM_FINALIZED
- Provide a web UI editor:
  - section-by-section editing (6.29(a)(i)-(iii))
  - comments + change log (simplified MVP)
- Must include the **UGC Policy Toggle**:
  - Mode A (Strict): block Decision “Granted” until UGC approval recorded
  - Mode B (Parallel): allow AKTU decision labeled “Subject to UGC” + auto-generate UGC recommendation packet

### Tests
- Draft generation creates document.
- Only committee roles can edit/finalize.
- Status rules enforced.

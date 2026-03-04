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
- Provide concise run steps in `README.md` and in `colab/AKTU-Autonomous-Institution-Application_run_backend_colab.ipynb`.

## Coding standards
- Python 3.10+
- Type hints everywhere.
- Black + Ruff formatting/lint.
- HTTP errors must be meaningful (status + message).
- Every endpoint must enforce authorization and log audit events.

---

## Task
Implement final decision workflow and institution notification.

### Deliverables
- Decision fields:
  - decision_type: GRANTED / GRANTED_WITH_CONDITIONS / DEFERRED / REJECTED / RETURNED_WITHOUT_PROCESSING / CLOSED_NON_COMPLIANCE
  - tenure_years, valid_from, valid_to
  - reasons, conditions
  - ugc_subject_to_flag (auto in Mode B if UGC not approved)
- Endpoint:
  - `POST /api/applications/{id}/decision` (authority) -> generate Decision Letter DOCX/PDF and status DECISION_ISSUED/CLOSED
- Email notification to institution (stub ok) with download link.
- Store decision letter as Document type = DecisionLetter.

### Tests
- Authority-only.
- Mode A blocks GRANTED without UGC approval doc recorded.

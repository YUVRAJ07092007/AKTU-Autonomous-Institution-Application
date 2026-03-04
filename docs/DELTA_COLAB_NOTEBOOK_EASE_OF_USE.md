# Delta Suggestions (Ease of Use) — AKTU_Autonomous_Institution_Application_run_backend_colab.ipynb

Date: 2026-03-04

This document is **delta-only**: it lists **only the suggested changes** to make the notebook easier to use for a **non‑coder** (no full rewrite).

---

## A) 8 High‑priority Ease‑of‑Use Changes

### 1) Remove duplicate / malformed title cell
- **Delete Cell 1** (duplicate title) because it contains literal escaped newlines like `\n\n` and confuses users.
- Keep only one clean title markdown cell.

---

### 2) Add a single “SETTINGS (Edit only this)” cell at the very top
**Add a new Code cell** at the top with simple toggles/values so you never edit deeper code cells.

Suggested variables:
```python
# SETTINGS (Edit only this)
USE_DRIVE = True            # True: store DB + uploads in Google Drive
RESET_DB = False            # True: wipe DB for a fresh run
RUN_SEED = True             # True: create demo users + sample applications
RUN_TESTS = False           # True: run pytest after setup
PORT = 8000

REPO_URL = "https://github.com/<org>/<repo>.git"
REPO_DIR = "/content/aktu_autonomy_repo"

# Optional: for private repos
GH_PAT_ENV = "AKTU_GH_PAT"  # if set in env, use it; else prompt
```

---

### 3) Make “fresh start” one click (integrate DB delete into setup)
- Merge the separate “DB delete” cell into the main setup cell.
- Control it with `RESET_DB`.

Implementation idea:
- compute DB path once (same logic used everywhere)
- if `RESET_DB=True`: delete DB file + uploads folder
- print: “Fresh start enabled: DB cleared ✅”

---

### 4) GitHub PAT handling — fewer prompts, safer token behavior
- If repo is public: **remove PAT prompt**.
- If repo is private:
  - Use `os.getenv(GH_PAT_ENV)` if present, otherwise prompt once.
  - After clone/pull, **remove PAT from git remote** to avoid token staying in `.git/config`:

```bash
git -C "$REPO_DIR" remote set-url origin "$REPO_URL"
```

---

### 5) ngrok cell must be safe to re‑run (avoid multi‑tunnel issues)
At the start of the “run server” cell:
- Kill/disconnect any existing ngrok tunnels before creating a new one.

Example approach:
```python
try:
    ngrok.kill()
except Exception:
    pass
```

---

### 6) Add an automatic backend health‑check wait (fail fast)
After starting uvicorn thread:
- Poll `http://127.0.0.1:{PORT}/api/health` for ~10 seconds.
- If not healthy: print “Server failed to start” and show quick hints (missing deps, port conflict, import error).

---

### 7) Fix Seed cell message + show outputs clearly
Current wording implies there is a “user table above” even when not shown.
- Update the message to: “Seed completed — see THIS cell output for created users.”
- Better: print users in a small readable list/table (username, role, institution).

---

### 8) Print “What to do next” in plain language after server starts
After ngrok URL is created, print a simple checklist:
- Swagger: `{public_url}/docs`
- Health: `{public_url}/api/health`
- Steps: open Swagger → Authorize (if needed) → try Health endpoint

This removes the “now what?” gap for non‑coders.

---

## B) 10 Nice‑to‑Have UX Improvements

### 9) Rename section headers and cells to be self‑explanatory
Use consistent headings:
- **A. SETTINGS (Edit only this)**
- **B. SETUP (mount → clone → install → DB setup)**
- **C. RUN SERVER (backend + ngrok)**
- **D. SEED DEMO DATA (optional)**
- **E. RUN TESTS (optional)**
- **F. REPORT METADATA (optional)**

---

### 10) Replace technical jargon in markdown (“migrations”) with plain language
Instead of “Run migrations”, say:
- “Database setup (automatic)”
- “Apply database updates”

---

### 11) Add a single “Run Order” markdown card at the top
A short, non‑coder sequence:
1. Run SETTINGS
2. Run SETUP
3. Run RUN SERVER
4. (Optional) Run SEED
5. (Optional) Run TESTS

---

### 12) Show clear success/failure badges in prints
Print very explicit markers:
- `✅ Setup complete`
- `✅ Server healthy`
- `❌ Server failed to start (see error above)`

---

### 13) Auto-detect and print where DB and uploads are stored
After setup, print:
- DB path in use
- Upload directory in use
- Whether it is Drive or local runtime storage

---

### 14) Add “Stop server / cleanup” helper cell
Add a small cell:
- kill ngrok
- stop uvicorn thread (if supported) or at least explain runtime restart

---

### 15) Make pytest output concise and readable
If `RUN_TESTS=True`:
- run `pytest -q -ra`
- print Python version and key package versions (optional) to help debugging

---

### 16) Put all URLs in one clearly labelled output block
After server start, print:
- Public base URL
- Swagger URL
- Health URL
- OpenAPI JSON URL

---

### 17) Add a “Common problems” mini‑FAQ
In markdown:
- “If /docs doesn’t open…”
- “If you see 401…”
- “If you see 403…”
- “If ngrok fails…”

---

### 18) Reduce repeated prompts and require input only once
- PAT prompt (only if needed)
- ngrok authtoken prompt (only once)
- avoid prompting in multiple cells

---

## C) Minimal Implementation Notes (non‑intrusive)
- These changes can be made without changing your backend logic.
- They primarily reorganize cells, add toggles, and add guardrails for re‑runs.

---

## D) Review and recommendations

| # | Suggestion | Recommendation | Notes |
|---|------------|----------------|-------|
| **1** | Remove duplicate title cell (Cell 1) | **Apply** | Cell 1 has literal `\n` and is redundant; keep one clean title. |
| **2** | Single “SETTINGS (Edit only this)” cell at top | **Apply with care** | Use a **code** cell that defines `USE_DRIVE`, `RESET_DB`, `RUN_SEED`, `RUN_TESTS`, `PORT`, `REPO_URL`, `REPO_DIR`. Later cells must **read** these (same kernel); avoid changing repo path to `/content/aktu_autonomy_repo` if README/CI reference current path—keep `REPO_DIR = "/content/aktu-autonomy-portal"` as default. |
| **3** | Merge DB delete into setup; control with `RESET_DB` | **Apply** | Single setup flow: if `RESET_DB` then delete DB (+ optional uploads), then mount/clone/install/migrate. Removes one cell and one “run order” decision. |
| **4** | GitHub PAT: skip for public repo; for private, use env then clear remote | **Apply** | If `REPO_URL` is public (no PAT in URL), clone without prompt. If private: use `os.getenv(GH_PAT_ENV)` or prompt once; after clone/pull run `git remote set-url origin <original REPO_URL>` so token is not stored in `.git/config`. |
| **5** | ngrok: kill existing tunnels before new one | **Apply** | At start of server cell: `try: ngrok.kill(); except Exception: pass` then `ngrok.connect(...)`. Makes re-run safe and avoids “Address already in use” / multiple tunnels. |
| **6** | Health-check wait after starting uvicorn (~10 s, fail fast) | **Apply** | Poll `http://127.0.0.1:{PORT}/api/health`; on success print “✅ Server healthy”; on timeout print “❌ Server failed to start” + short hints (port, deps, import). |
| **7** | Seed cell: fix message; show users in this cell | **Apply** | Message: “Seed completed — see this cell’s output for created users.” Seed script already prints user table to stdout; subprocess run captures it. Either (a) don’t capture stdout so table appears in notebook, or (b) print the captured stdout in the cell. Prefer (a): run without capturing so “user table above” is accurate. |
| **8** | “What to do next” after server starts | **Apply** | Print Swagger URL, Health URL, OpenAPI URL, and 2–3 bullet steps (Open Swagger → Authorize → try Health). |
| **9** | Rename sections (A. SETTINGS, B. SETUP, …) | **Optional** | Improves scanability; align with “Run order” card. |
| **10** | Plain language for “migrations” | **Optional** | Use “Database setup (automatic)” or “Apply database updates” in markdown/code comments. |
| **11** | “Run order” markdown card at top | **Optional** | Short numbered list (1. SETTINGS 2. SETUP 3. RUN SERVER 4–6 optional). Fits well with section renames. |
| **12** | Success/failure badges (✅/❌) in prints | **Apply** | Already partially suggested in #6; use consistently for setup complete, server healthy, seed/tests result. |
| **13** | Auto-print DB path, upload dir, Drive vs local | **Apply** | After setup (or in inspect cell), print “DB: …”, “Uploads: …”, “Storage: Google Drive” or “Storage: local (session only)”. |
| **14** | “Stop server / cleanup” cell | **Optional** | ngrok.kill() is doable; stopping the uvicorn thread from another cell is not straightforward (daemon thread). Document “Restart runtime to stop server” and add a cell that only runs `ngrok.kill()`. |
| **15** | Pytest: `-q -ra`, optional version print | **Apply** | Use `pytest -q -ra` when running from notebook; optionally print Python version. |
| **16** | All URLs in one labelled block | **Apply** | Covered by #8; one block: Base URL, Swagger, Health, OpenAPI. |
| **17** | “Common problems” mini-FAQ | **Optional** | Markdown: /docs doesn’t open, 401, 403, ngrok fails. Helpful for non-coders; keep it short. |
| **18** | Reduce repeated prompts (PAT once, ngrok once) | **Apply** | Already aligned with #4 (PAT) and single server cell (ngrok once). Ensure no other cell prompts for the same token. |

**Summary**
- **High priority (1–8):** All recommended to apply. #2 and #3 need care so `REPO_DIR` and run order stay consistent with README/Colab links.
- **Nice-to-have (9–18):** Apply 12, 13, 15, 16, 18; optionally 9, 10, 11, 14, 17.
- **Risks:** Changing default `REPO_DIR` could break existing Colab copies; keep default `/content/aktu-autonomy-portal`. PAT clearing after clone is important for security when repo is private.

---

## E) Implementation status (applied)

The following were applied to the Colab notebook:

- **1** Removed duplicate title; single title cell with **Run order** card.
- **2** Added **A. SETTINGS** cell at top: `USE_DRIVE`, `RESET_DB`, `RUN_SEED`, `RUN_TESTS`, `PORT`, `REPO_URL`, `REPO_DIR`, `USE_GH_PAT`, `GH_PAT_ENV`.
- **3** **B. SETUP** merges DB delete (when `RESET_DB`), mount, clone/pull, database setup, optional seed and pytest; prints DB path, uploads, storage, ✅ Setup complete.
- **4** PAT: public repo clones without prompt; when `USE_GH_PAT` or `AKTU_GH_PAT` set, prompt once then `git remote set-url origin` to clear token.
- **5** **C. RUN SERVER** calls `ngrok.kill()` before creating tunnel so re-run is safe.
- **6** Health-check wait (~10 s) after uvicorn start; prints ✅ Server healthy or ❌ Server failed to start.
- **7** Seed: message says “see this cell’s output”; seed in SETUP runs without capturing stdout so user table appears.
- **8** After server: one block with Base URL, Swagger, Health, OpenAPI + “What to do next”.
- **9–11** Section headers (A/B/C/D/E/F) and Run order in title cell.
- **12** ✅/❌ used for setup complete and server health.
- **13** After setup: print DB path, uploads, “Storage: Google Drive” or “local (session only)”.
- **14** Optional “Stop tunnel” cell: `ngrok.kill()` + note to restart runtime to stop server.
- **15** Pytest cell uses `pytest -q -ra`.
- **16** All URLs in one labelled block (in RUN SERVER).
- **17** “Common problems” mini-FAQ in testing docs cell (/docs, 401, 403, ngrok).
- **18** PAT and ngrok prompted once; no duplicate prompts.

Plain-language “database setup” used in comments. Default `REPO_DIR` kept as `/content/aktu-autonomy-portal`.

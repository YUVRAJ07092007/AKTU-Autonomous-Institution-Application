## AKTU Academic Autonomy Portal

**Repository:** [https://github.com/YUVRAJ07092007/AKTU-Autonomous-Institution-Application](https://github.com/YUVRAJ07092007/AKTU-Autonomous-Institution-Application)

Monorepo for the AKTU Academic Autonomy Portal: FastAPI backend, Next.js frontend, Colab runbooks, and CI.

### Structure

- `backend/`: FastAPI backend (`GET /api/health`).
- `frontend/`: Next.js frontend with a health-check button.
- `colab/`: Notebooks to run the backend in Google Colab.
- `docs/`: Workflow and API documentation.

### Backend (FastAPI + SQLite)

Create `backend/.env` from `.env.example` (or set `JWT_SECRET` and optionally `AKTU_DB_PATH`, `UPLOAD_DIR`). Then from the repo root:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux / Colab
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- **Health (no auth):** `http://127.0.0.1:8000/api/health/live`
- **Health (with auth):** `http://127.0.0.1:8000/api/health` (Bearer token required)

CORS is enabled so the Next.js frontend can call the API from another origin. For production, set `allow_origins` in `app.main` to your frontend origin(s).

### Frontend (Next.js)

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

Copy `.env.example` to `frontend/.env.local` and set `NEXT_PUBLIC_API_BASE_URL` to your backend URL (e.g. `http://127.0.0.1:8000` or your ngrok URL).

### Testing and CI

**Backend (pytest, ruff, black)**

From `backend/`:

```bash
pip install -r requirements.txt
export ENV=test
ruff check app tests
black --check app tests
pytest
```

**Frontend (lint, build, optional E2E)**

From `frontend/`:

```bash
npm install
npm run lint
npm run build
# Optional: smoke test with Playwright (install browsers: npx playwright install)
npm run test:e2e
```

**GitHub Actions**

On push/PR to `main` (or `master`), the workflow in `.github/workflows/ci.yml` runs:

- **Backend:** ruff, black check, pytest (with `ENV=test`).
- **Frontend:** lint and build.

An optional **Playwright** job runs on push to `main` (or via manual workflow_dispatch) to execute the smoke test. Pre-commit hooks for ruff/black are optional (add to your local repo if desired).

### Colab runner

**Backend (FastAPI)**

1. Open `colab/run_backend_colab.ipynb` in Google Colab (via **File → Open notebook → GitHub**, then enter `https://github.com/YUVRAJ07092007/AKTU-Autonomous-Institution-Application` and open **colab/run_backend_colab.ipynb**).
2. Run the first code cell:
   - Mounts Google Drive (or uses local storage if mount fails)
   - Clones or pulls the repo into `/content/aktu-autonomy-portal` (you will be prompted for a GitHub PAT)
   - Installs backend dependencies from `backend/requirements.txt`
   - Runs `alembic upgrade head` against a SQLite DB on Drive
3. Run the second code cell:
   - Starts Uvicorn for `app.main:app` on port `8000`
   - Starts an ngrok tunnel and prints a public URL and `/api/health` link
4. Keep the notebook running and call the API using the printed public URL.

**Frontend preview (optional)**

If you want to preview the Next.js UI from Colab:

1. Ensure the repo is already cloned at `/content/aktu-autonomy-portal` (via the backend notebook).
2. When available, open `colab/run_frontend_preview_colab.ipynb` from [AKTU-Autonomous-Institution-Application](https://github.com/YUVRAJ07092007/AKTU-Autonomous-Institution-Application).
3. Run all cells to install Node dependencies, start `npm run dev` on port `3000`, and expose it via ngrok.


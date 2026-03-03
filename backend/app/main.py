from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.deps import get_current_user
from app.core.config import get_runtime_config
from app.core.logging import setup_logging
from app.core.debug_log import write_debug_log
from app.api.routes import auth as auth_routes
from app.api.routes import applications as applications_routes
from app.api.routes import documents as documents_routes


setup_logging()
runtime = get_runtime_config()
logger = logging.getLogger("aktu-autonomy-portal")

app = FastAPI(title="AKTU Academic Autonomy Portal API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(applications_routes.router)
app.include_router(documents_routes.router)


@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    """Very thin audit log stub for all actions."""
    response = await call_next(request)
    logger.info(
        "audit_event",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    return response


@app.get("/")
async def root() -> JSONResponse:
    """Root: point users to the API."""
    return JSONResponse({
        "service": "AKTU Academic Autonomy Portal API",
        "docs": "/docs",
        "health": "/api/health/live",
        "health_auth": "/api/health",
    })


@app.get("/api/health/live")
async def health_live() -> JSONResponse:
    """Unauthenticated liveness probe for load balancers and k8s."""
    return JSONResponse({"status": "ok", "service": "aktu-autonomy-portal"})


@app.get("/api/health")
async def health(_user=Depends(get_current_user)) -> JSONResponse:
    """Health with auth (readiness-style); use /api/health/live for unauthenticated probes."""
    write_debug_log(
        hypothesis_id="H3",
        location="backend/app/main.py:health",
        message="Health endpoint called",
        data={"env": runtime.settings.env},
    )
    return JSONResponse({"status": "ok", "service": "aktu-autonomy-portal"})


def get_db_path() -> str:
    """Returns SQLite DB path from config."""
    return runtime.settings.database_url


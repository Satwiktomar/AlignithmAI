from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from routes import similarity, ats, taxonomy
from embedding_engine import warmup_model, get_cache_stats
import os
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ml-service")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

ML_INTERNAL_KEY = os.getenv("ML_INTERNAL_KEY", "")

_PUBLIC_PATHS = {"/", "/health", "/cache-stats", "/docs", "/openapi.json"}


class InternalAuthMiddleware(BaseHTTPMiddleware):
    """Verify X-Internal-Key header on non-public endpoints."""
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)
        if ML_INTERNAL_KEY:
            provided = request.headers.get("X-Internal-Key", "")
            if provided != ML_INTERNAL_KEY:
                return JSONResponse(status_code=403, content={"detail": "Invalid or missing internal key"})
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000)
        if not request.url.path.startswith("/health"):
            logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)")
        return response


app = FastAPI(
    title="RoleFit AI — ML Service",
    description="Embedding-based semantic similarity, ATS scoring, and skill taxonomy normalization",
    version="2.0.0"
)

app.add_middleware(InternalAuthMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Internal-Key"],
)

app.include_router(similarity.router)
app.include_router(ats.router)
app.include_router(taxonomy.router)


# ── Model pre-warming at startup ────────────────────────────────────────

_model_status = {"status": "loading"}


@app.on_event("startup")
async def startup_event():
    global _model_status
    logger.info("Pre-warming embedding model...")
    try:
        _model_status = warmup_model()
        logger.info(f"Model ready: {_model_status}")
    except Exception as e:
        _model_status = {"status": "error", "error": str(e)}
        logger.error(f"Model warmup failed: {e}")


# ── Endpoints ───────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "RoleFit ML Service running", "version": "2.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": _model_status,
        "cache": get_cache_stats(),
    }


@app.get("/cache-stats")
def cache_stats():
    return get_cache_stats()


# ── Error handlers ──────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": True, "detail": "Internal server error"},
    )

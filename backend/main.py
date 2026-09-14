"""M4 Backend Entrypoint.

Provides the REST/voice API boundary, CORS for the M3 browser client,
and lightweight request logging/health endpoints.
"""

from __future__ import annotations

import logging
import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.router import router
from backend.api.voice_router import router as voice_router


logging.basicConfig(
    level=os.getenv("ORCA_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("orca.m4")


app = FastAPI(
    title="ORCA-LIVING M4 Integration API",
    version="1.0.0",
)


# Browser clients need CORS when M3 and M4 run on different ports/hosts.
# Set ORCA_ALLOWED_ORIGINS to a comma-separated allow-list for deployment.
# The default is intentionally permissive for the local SIH demo and does
# not enable credential sharing.
_allowed_origins = [
    origin.strip()
    for origin in os.getenv("ORCA_ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_trace_middleware(request: Request, call_next):
    """Attach a trace id and log API duration without logging request data."""
    trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "request_failed method=%s path=%s trace_id=%s duration_ms=%.1f",
            request.method,
            request.url.path,
            trace_id,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = trace_id
    logger.info(
        "request_complete method=%s path=%s status=%s trace_id=%s duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        trace_id,
        elapsed_ms,
    )
    return response


@app.get("/health")
async def health_check():
    """Liveness endpoint; does not fabricate upstream availability."""
    return {
        "status": "healthy",
        "service": "m4",
        "version": app.version,
    }


@app.get("/ready")
async def readiness_check():
    """M4 process readiness endpoint.

    Upstream M2/M1 calls are validated when a decision is requested; this
    endpoint only confirms that the M4 application has initialized.
    """
    return {
        "status": "ready",
        "service": "m4",
        "version": app.version,
    }


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return a stable error envelope without exposing a fake recommendation."""
    trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    logger.exception(
        "unhandled_exception method=%s path=%s trace_id=%s",
        request.method,
        request.url.path,
        trace_id,
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "SERVICE_UNAVAILABLE",
            "error": "M4 service encountered an unexpected error",
            "requestId": trace_id,
        },
        headers={"X-Request-ID": trace_id},
    )


app.include_router(router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

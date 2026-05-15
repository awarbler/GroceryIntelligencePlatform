# =============================================================================
# File: routes.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Registers backend API routers for the FastAPI application.
# Security Note: Registers the global rate-limit exception handler.
# SRS Traceability: Supports SRS v5.0 SE-008 and SE-009.
# SDD Traceability: Supports SDD v5.0 API endpoint design.
# =============================================================================

from __future__ import annotations  # Enables modern type annotation behavior.

from fastapi import FastAPI  # Imports FastAPI so routers can be registered on the app.
from slowapi import _rate_limit_exceeded_handler  # Imports the default SlowAPI 429 handler.
from slowapi.errors import RateLimitExceeded  # Imports the SlowAPI rate-limit exception.

from backend.api.auth import router as auth_router  # Imports the authentication router.
from backend.api.rate_limit import limiter  # Imports the shared application limiter.


def register_routes(app: FastAPI) -> None:  # Registers all API routers on the FastAPI app.
    app.state.limiter = limiter  # Stores the limiter on app state for SlowAPI.
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # Registers the rate-limit error handler.
    app.include_router(auth_router, prefix="/api/v1")  # Mounts auth routes under /api/v1/auth.
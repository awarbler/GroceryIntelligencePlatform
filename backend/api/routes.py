# =============================================================================  # File header separator.
# File: api/routes.py  # Identifies this route registration file.
# Project: Grocery Intelligence Platform  # Identifies the project.
# Author: Anita Woodford  # Identifies the project author.
# Description: Registers backend API routers for the FastAPI application.  # Explains the file purpose.
# Security Note: Registers the global rate-limit exception handler.  # States security concern.
# SRS Traceability: Supports SRS v5.0 SE-008, SE-009, ET-001 through ET-005, and HC-001 through HC-009.  # Maps to SRS.
# SDD Traceability: Supports SDD v5.0 API endpoint design.  # Maps to SDD.
# =============================================================================  # File header separator.

from __future__ import annotations  # Enables modern type annotation behavior.

from fastapi import FastAPI  # Imports FastAPI so routers can be registered on the app.
from slowapi import _rate_limit_exceeded_handler  # Imports the default SlowAPI 429 handler.
from slowapi.errors import RateLimitExceeded  # Imports the SlowAPI rate-limit exception.

from backend.api.auth import router as auth_router  # Imports the authentication router.
from backend.api.etl import router as etl_router  # Imports the ETL and correction router.
from backend.api.rate_limit import limiter  # Imports the shared application limiter.
from backend.api.purchases import router as purchases_router  # Imports purchase CRUD routes.

from backend.api.my_items import router as my_items_router  # Imports My Items CRUD routes.
from backend.api.ad_etl import router as ad_etl_router  # Imports H-E-B weekly ad ETL routes.
from backend.api.ads import router as ads_router  # Imports H-E-B weekly ad retrieval routes.

def register_routes(app: FastAPI) -> None:  # Registers all API routers on the FastAPI app.
    app.state.limiter = limiter  # Stores the limiter on app state for SlowAPI.
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # Registers the rate-limit error handler.
    app.include_router(auth_router, prefix="/api/v1")  # Mounts auth routes under /api/v1/auth.
    app.include_router(etl_router, prefix="/api/v1")  # Mounts ETL and correction routes under /api/v1.
    app.include_router(ads_router, prefix="/api/v1")  # Mounts ad retrieval routes under /api/v1/ads.
    app.include_router(ad_etl_router, prefix="/api/v1")  # Mounts ad ETL routes under /api/v1/ad-etl.
    app.include_router(purchases_router, prefix="/api/v1")  # Mounts purchase CRUD routes under /api/v1/purchases.
    app.include_router(my_items_router, prefix="/api/v1")  # Mounts My Items CRUD routes under /api/v1/my-items.
# =============================================================================
# File: backend/api/ads.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Defines H-E-B weekly ad retrieval endpoints.
# Security Note: Routes call service layer only and do not access MongoDB directly.
# SRS Traceability: Supports SRS v5.0 Section 7 AD-001 through AD-010.
# SDD Traceability: Supports SDD v5.0 Section 8 API Endpoint Design.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations.

from datetime import date  # Supports query date parsing.
from typing import Any  # Supports generic response dictionaries.

from fastapi import APIRouter  # Provides API router.
from fastapi import Depends  # Provides dependency injection.
from fastapi import Query  # Provides query validation.
from motor.motor_asyncio import AsyncIOMotorDatabase  # Provides database type annotation.

from backend.data_access.ads import AdsDataAccess  # Imports ads DAL.
from backend.database import get_db  # Imports DB dependency.
from backend.services import ad_service  # Imports ad service layer.


router: APIRouter = APIRouter(prefix="/ads", tags=["ads"])  # Defines ads routes under /api/v1/ads.


def get_ads_dal(db: AsyncIOMotorDatabase = Depends(get_db)) -> AdsDataAccess:  # Builds DAL dependency.
    return AdsDataAccess(db)  # Returns ads DAL.


@router.get("")  # Handles GET /api/v1/ads.
async def get_ads(
    as_of_date: date | None = Query(default=None),  # Optional valid-date filter.
    store_ref: str | None = Query(default=None),  # Optional store reference filter.
    skip: int = Query(default=0, ge=0),  # Optional pagination skip.
    limit: int = Query(default=100, ge=1, le=500),  # Optional pagination limit.
    dal: AdsDataAccess = Depends(get_ads_dal),  # Injects ads DAL.
) -> dict[str, Any]:
    ads: list[dict[str, Any]] = await ad_service.list_current_ads(  # Calls service layer only.
        dal=dal,  # Passes DAL.
        as_of_date=as_of_date,  # Passes date filter.
        store_ref=store_ref,  # Passes store filter.
        skip=skip,  # Passes skip.
        limit=limit,  # Passes limit.
        
    )
    return {"success": True, "data": ads, "meta": {"count": len(ads)}}  # Returns standard response.
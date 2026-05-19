# =============================================================================
# File: api/coupons.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines manual H-E-B coupon CRUD endpoints.
# Security Note: Route handlers must not directly access MongoDB.
# SRS Traceability: Supports SRS v5.0 CP-001 through CP-005 and CP-010.
# SDD Traceability: Supports SDD v5.0 coupon endpoint architecture.
# =============================================================================

from __future__ import annotations  # Enables postponed evaluation of annotations.

from typing import Any  # Imports Any for generic response typing.

from fastapi import APIRouter  # Imports FastAPI router support.
from fastapi import Depends  # Imports dependency injection support.
from fastapi import Query  # Imports typed query parameter support.
from motor.motor_asyncio import AsyncIOMotorDatabase  # Imports MongoDB database type.

from backend.database import get_db  # Imports shared database dependency.

from backend.data_access.coupons import (
    CouponsDataAccess,
)  # Imports coupon DAL helper.

from backend.models.coupon import (
    CouponModel,
)  # Imports validated coupon model.

from backend.services import coupon_service  # Imports coupon business logic.


router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
)  # Creates coupon router.


@router.get("")
async def get_coupons(
    include_expired: bool = Query(
        default=False,
        description="Controls whether expired coupons are included.",
    ),
    store_ref: str | None = Query(
        default=None,
        description="Optional store ObjectId filter.",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip.",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Maximum records returned.",
    ),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict[str, Any]:  # Returns a standard API response dictionary.
    """Lists coupon records."""  # Documents purpose.

    dal = CouponsDataAccess(
        db
    )  # Creates coupon DAL dependency.

    coupons = await coupon_service.list_coupons(
        dal=dal,
        include_expired=include_expired,
        store_ref=store_ref,
        skip=skip,
        limit=limit,
    )  # Gets coupon records through the service layer.

    return {
        "success": True,
        "data": coupons,
        "meta": {
            "count": len(coupons)
        },
    }  # Returns response shape consistent with ad endpoints.

@router.post("")
async def create_coupon(
    coupon: CouponModel,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict[str, str]:
    """Creates one coupon."""  # Documents purpose.

    dal = CouponsDataAccess(
        db
    )  # Creates coupon DAL dependency.

    coupon_id = await coupon_service.create_coupon(
        dal=dal,
        coupon=coupon,
    )  # Creates coupon through service layer.

    return {
        "coupon_id": coupon_id
    }  # Returns created coupon identifier.


@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict[str, bool]:
    """Deletes one coupon."""  # Documents purpose.

    dal = CouponsDataAccess(
        db
    )  # Creates coupon DAL dependency.

    deleted = await coupon_service.delete_coupon(
        dal=dal,
        coupon_id=coupon_id,
    )  # Deletes coupon through service layer.

    return {
        "deleted": deleted
    }  # Returns deletion status.
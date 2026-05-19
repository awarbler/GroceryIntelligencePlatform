# =============================================================================
# File: services/coupon_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Implements business logic for coupon CRUD operations.
# Security Note: Service layer prevents route handlers from directly accessing MongoDB.
# SRS Traceability: Supports SRS v5.0 CP-001 through CP-005 and CP-010.
# SDD Traceability: Supports SDD v5.0 coupon API service architecture.
# =============================================================================

from __future__ import annotations  # Enables postponed evaluation of annotations.

from datetime import date  # Imports date for expiration filtering.
from typing import Any  # Imports Any for generic dictionary values.

from backend.data_access.coupons import (
    CouponsDataAccess,
)  # Imports coupon DAL helper.

from backend.models.coupon import (
    CouponModel,
)  # Imports validated coupon model.


async def list_coupons(
    dal: CouponsDataAccess,
    include_expired: bool = False,
    store_ref: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Lists coupons with optional expiration filtering."""  # Documents purpose.

    return await dal.list_by_filters(
        store_ref=store_ref,
        include_expired=include_expired,
        as_of_date=date.today().isoformat(),
        skip=skip,
        limit=limit,
    )  # Returns filtered coupon records.


async def create_coupon(
    dal: CouponsDataAccess,
    coupon: CouponModel,
) -> str:
    """Creates one validated coupon."""  # Documents purpose.

    coupon_document = coupon.model_dump(
        by_alias=True
    )  # Converts Pydantic model into MongoDB-ready dictionary.

    return await dal.create_coupon(
        coupon_document
    )  # Creates coupon through DAL.


async def delete_coupon(
    dal: CouponsDataAccess,
    coupon_id: str,
) -> bool:
    """Deletes one coupon."""  # Documents purpose.

    return await dal.delete_coupon(
        coupon_id
    )  # Deletes coupon through DAL.
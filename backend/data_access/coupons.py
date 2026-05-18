# =============================================================================
# File: coupons.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the coupons collection.
# Security Note: Coupon records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 CP-018, SE-009, and Section 19 coupons collection.
# SDD Traceability: Supports SDD v5.0 coupons database design.
# =============================================================================
from __future__ import annotations# Enables modern type hints without runtime forward-reference issues.

from collections.abc import Mapping# Imports Mapping for read-only dictionary-style inputs.
from typing import Any# Imports Any because MongoDB document values vary by collection.

from bson import ObjectId  # Imports ObjectId for MongoDB primary key handling.
from motor.motor_asyncio import AsyncIOMotorCollection # Imports the async Motor collection type.


from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import COUPONS_COLLECTION # Imports the approved coupons collection name.


class CouponsDataAccess(MongoDataAccess):  # Defines collection-specific access for coupons.
    """Data access helper for coupon documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[COUPONS_COLLECTION])  # Connects this helper to the coupons collection.

    async def list_by_filters(
        self,  # Uses this coupons data access helper.
        store_ref: str | None = None,  # Optionally filters by store reference.
        include_expired: bool = False,  # Controls whether expired coupons are included.
        as_of_date: str
        | None = None,  # Receives the current date for expiration filtering.
        skip: int = 0,  # Skips this many records for pagination.
        limit: int = 100,  # Limits the number of returned records.
    ) -> list[dict[str, Any]]:  # Returns matching coupon documents.
        filters: dict[str, Any] = {}  # Builds a MongoDB filter dictionary.

        if store_ref is not None:  # Checks whether a store filter was supplied.
            filters["store_ref"] = store_ref  # Adds the store filter.

        if (
            include_expired is False and as_of_date is not None
        ):  # Checks whether expired coupons should be excluded.
            filters["expiration_date"] = {
                "$gte": as_of_date
            }  # Adds the active coupon date filter.

        return await self.list_records(
            filters=filters, skip=skip, limit=limit
        )  # Returns matching coupons.

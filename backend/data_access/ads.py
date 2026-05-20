# =============================================================================
# File: backend/data_access/ads.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the ads collection.
# Security Note: Ad records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 AD requirements and Section 19 ads collection.
# SDD Traceability: Supports SDD v5.0 ads database design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints without runtime forward-reference issues.

from datetime import date  # Supports date filtering.
from typing import Any  # Supports MongoDB document dictionaries.

from motor.motor_asyncio import AsyncIOMotorDatabase  # Imports async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import ADS_COLLECTION  # Imports approved ads collection name.


class AdsDataAccess(MongoDataAccess):  # Defines collection-specific access for ads.
    """Data access helper for ad documents."""  # Documents class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives MongoDB database dependency.
        super().__init__(database[ADS_COLLECTION])  # Connects helper to ads collection.

    async def create_ad(self, ad_doc: dict[str, Any]) -> str:  # Inserts one ad document.
        return await self.create_one(ad_doc)  # Delegates insert to base DAL.

    async def list_valid_ads(
        self,
        as_of_date: date | str,
        store_ref: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return ads valid on the requested date."""
        as_of: str = as_of_date.isoformat() if isinstance(as_of_date, date) else as_of_date  # Supports both date objects and existing string tests.
        filters: dict[str, Any] = {  # Builds valid-date filter.
            "start_date": {"$lte": as_of},  # Includes ads starting on or before date.
            "end_date": {"$gte": as_of},  # Includes ads ending on or after date.
        }

        if store_ref is not None:  # Applies store filter only when provided.
            filters["store_ref"] = store_ref  # Filters by store reference.

        return await self.list_records(filters=filters, skip=skip, limit=limit)  # Returns matching ads.
    
    async def list_active_heb_ads(self) -> list[dict]:  # Lists active H-E-B ads
        cursor = self.collection.find({"store": "HEB", "is_active": True})  # Finds active H-E-B ad records
        return await cursor.to_list(length=None)  # Returns all active ads
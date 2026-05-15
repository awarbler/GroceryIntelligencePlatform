# =============================================================================
# File: ads.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the ads collection.
# Security Note: Ad records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 AD requirements and Section 19 ads collection.
# SDD Traceability: Supports SDD v5.0 ads database design.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without runtime forward-reference issues.

from typing import (
    Any,
)  # Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
)  # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import ADS_COLLECTION  # Imports the approved ads collection name.


class AdsDataAccess(MongoDataAccess):  # Defines collection-specific access for ads.
    """Data access helper for ad documents."""  # Documents the class purpose.

    def __init__(
        self, database: AsyncIOMotorDatabase
    ) -> None:  # Receives the MongoDB database dependency.
        super().__init__(
            database[ADS_COLLECTION]
        )  # Connects this helper to the ads collection.

    async def list_valid_ads(
        self,  # Uses this ads data access helper.
        as_of_date: str,  # Receives the date used to determine ad validity.
        store_ref: str | None = None,  # Optionally filters by store reference.
    ) -> list[dict[str, Any]]:  # Returns matching ad documents.
        filters: dict[str, Any] = {  # Builds a MongoDB filter for valid ads.
            "start_date": {
                "$lte": as_of_date
            },  # Requires ad start date to be on or before the date.
            "end_date": {
                "$gte": as_of_date
            },  # Requires ad end date to be on or after the date.
        }  # Completes the default valid-ad filter.

        if store_ref is not None:  # Checks whether a store filter was supplied.
            filters["store_ref"] = store_ref  # Adds the store filter.

        return await self.list_records(filters=filters)  # Returns currently valid ads.

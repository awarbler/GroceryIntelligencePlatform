# =============================================================================
# File: data_access/rebates.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the rebates collection.
# Security Note: Rebate records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 rebate lifecycle requirements and Section 19.
# SDD Traceability: Supports SDD v5.0 rebates database design.
# =============================================================================

from __future__ import annotations # Enables modern type hints without runtime forward-reference issues.

from typing import Any# Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.

from backend.database import REBATES_COLLECTION# Imports the approved rebates collection name.


class RebatesDataAccess(MongoDataAccess):  # Defines collection-specific access for rebates.
    """Data access helper for rebate documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[REBATES_COLLECTION])  # Connects this helper to the rebates collection.

    async def list_by_filters(
        self,  # Uses this rebates data access helper.
        company: str | None = None,  # Optionally filters by rebate company.
        status: str | None = None,  # Optionally filters by rebate lifecycle status.
        skip: int = 0,  # Skips this many records for pagination.
        limit: int = 100,  # Limits the number of returned records.
    ) -> list[dict[str, Any]]:  # Returns matching rebate documents.
        filters: dict[str, Any] = {}  # Builds a MongoDB filter dictionary.

        if company is not None:  # Checks whether a company filter was supplied.
            filters["company"] = company  # Adds the company filter.

        if status is not None:  # Checks whether a status filter was supplied.
            filters["status"] = status  # Adds the status filter.

        return await self.list_records(filters=filters, skip=skip, limit=limit)  # Returns matching rebates.

    async def update_status(self, record_id: str, new_status: str) -> bool:  # Updates one rebate status.
        return await self.update_one_by_id(record_id, {"status": new_status})  # Updates only the status field.

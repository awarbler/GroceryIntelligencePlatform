# =============================================================================
# File: deal_matches.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the deal_matches collection.
# Security Note: Deal match records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 deal report requirements and Section 19.
# SDD Traceability: Supports SDD v5.0 deal matching database design.
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
from backend.database import (
    DEAL_MATCHES_COLLECTION,
)  # Imports the approved deal matches collection name.


class DealMatchesDataAccess(
    MongoDataAccess
):  # Defines collection-specific access for deal matches.
    """Data access helper for deal match documents."""  # Documents the class purpose.

    def __init__(
        self, database: AsyncIOMotorDatabase
    ) -> None:  # Receives the MongoDB database dependency.
        super().__init__(
            database[DEAL_MATCHES_COLLECTION]
        )  # Connects this helper to the deal matches collection.

    async def find_by_week(
        self, week_of: str
    ) -> dict[str, Any] | None:  # Finds the deal match document for one week.
        return await self.collection.find_one(
            {"week_of": week_of}
        )  # Returns the matching deal match document or None.

# =============================================================================
# File: stores.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the stores collection.
# Security Note: Store credentials must not be stored in this collection.
# SRS Traceability: Supports SRS v5.0 U-005, SE-009, and Section 19 stores collection.
# SDD Traceability: Supports SDD v5.0 database design and backend modular architecture.
# =============================================================================
from __future__ import annotations # Enables modern type hints without runtime forward-reference issues.

from typing import Any# Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.



from backend.database import STORES_COLLECTION# Imports the approved stores collection name.


class StoresDataAccess(MongoDataAccess):  # Defines collection-specific access for stores.
    """Data access helper for store documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[STORES_COLLECTION])  # Connects this helper to the stores collection.

    async def find_by_store_id(self, store_id: str) -> dict[str, Any] | None:  # Finds one store by store_id.
        return await self.collection.find_one({"store_id": store_id})  # Returns the matching store or None.

    async def list_active(self) -> list[dict[str, Any]]:  # Lists only active stores.
        return await self.list_records(filters={"active": True})  # Returns store documents marked active.

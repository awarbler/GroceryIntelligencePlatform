# =============================================================================
# File: raw_inputs.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the raw_inputs collection.
# Security Note: Raw input records may contain source text but must not contain secrets.
# SRS Traceability: Supports SRS v5.0 RD-001, RD-002, RD-003, RD-004, and Section 19.
# SDD Traceability: Supports SDD v5.0 ETL raw input preservation.
# =============================================================================
from __future__ import annotations # Enables modern type hints without runtime forward-reference issues.

from typing import Any# Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import RAW_INPUTS_COLLECTION # Imports the approved raw inputs collection name.
from bson import ObjectId  # Imports ObjectId so string IDs can be converted for MongoDB updates.

class RawInputsDataAccess(MongoDataAccess):  # Defines collection-specific access for raw inputs.
    """Data access helper for raw input documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[RAW_INPUTS_COLLECTION])  # Connects this helper to the raw inputs collection.

    async def insert_raw_input(self, document: dict[str, Any]) -> str:  # Inserts one raw input archive document.
        result = await self.collection.insert_one(document)  # Saves the raw input archive before purchase records are inserted.
        return str(result.inserted_id)  # Converts the inserted MongoDB ObjectId to a string.

    async def append_linked_record_ids(self, raw_input_id: str, record_ids: list[str]) -> None:  # Links saved purchase IDs back to the raw input archive.
        await self.collection.update_one(  # Updates one raw input archive document.
            {"_id": ObjectId(raw_input_id)},  # Finds the archive document by its MongoDB ObjectId.
            {"$push": {"linked_record_ids": {"$each": record_ids}}},  # Appends all purchase IDs to linked_record_ids.
        )  # Ends the MongoDB update call.
        
    async def list_by_store(self, store_ref: str, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:  # Lists raw inputs by store.
        return await self.list_records(filters={"store_ref": store_ref}, skip=skip, limit=limit)  # Returns matching raw inputs.

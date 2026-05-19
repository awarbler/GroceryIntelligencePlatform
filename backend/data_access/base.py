# =============================================================================
# File: data_access/base.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides shared async MongoDB CRUD helpers for the Data Access Layer.
# Security Note: Receives validated data from services and does not log secrets.
# SRS Traceability: Supports SRS v5.0 SE-009, PL-032, PL-033, and Section 19.
# SDD Traceability: Supports SDD v5.0 backend folder structure and database design.
# =============================================================================

from __future__ import annotations# Enables modern type hints without runtime forward-reference issues.

from collections.abc import Mapping# Imports Mapping for read-only dictionary-style inputs.
from typing import Any# Imports Any because MongoDB document values vary by collection.

from bson import ObjectId  # Imports ObjectId for MongoDB primary key handling.
from motor.motor_asyncio import AsyncIOMotorCollection # Imports the async Motor collection type.


DEFAULT_LIMIT = (100 )

MAX_LIMIT = (500)


class DataAccessError(RuntimeError):  # Defines a shared Data Access Layer exception type.
    """Raised when a data access operation cannot be completed."""  # Documents the exception purpose.


def normalize_object_id(record_id: str | ObjectId,) -> ObjectId:  # Converts incoming IDs to ObjectId.
    """Return a valid MongoDB ObjectId from a string or ObjectId."""  # Documents the helper behavior.
    if isinstance(record_id, ObjectId):  # Checks whether the ID is already an ObjectId.
        return record_id  # Returns the existing ObjectId unchanged.

    if not ObjectId.is_valid(record_id):  # Checks whether the string can become an ObjectId.
        raise ValueError(f"Invalid MongoDB ObjectId: {record_id!r}")  # Raises a safe validation error.

    return ObjectId(record_id)  # Converts the valid string into an ObjectId.


class MongoDataAccess:  # Defines the shared async CRUD helper for one collection.
    """Shared async CRUD helper for one MongoDB collection."""  # Documents the class purpose.

    def __init__(self, collection: AsyncIOMotorCollection) -> None:  # Receives the MongoDB collection dependency.
        self.collection = collection  # Stores the collection for CRUD methods.

    async def create_one(self, data: Mapping[str, Any]) -> str:  # Inserts one validated document.
        document = dict(data)  # Copies the incoming mapping into a mutable dictionary.
        result = await self.collection.insert_one(document)  # Inserts the document into MongoDB.
        return str(result.inserted_id)  # Returns the inserted MongoDB ID as a string.

    async def find_one_by_id(self, record_id: str | ObjectId) -> dict[str, Any] | None:  # Finds one document by ID.
        try:  # Starts safe ObjectId conversion.
            object_id = normalize_object_id(record_id)  # Converts the incoming ID to ObjectId.
        except ValueError:  # Handles invalid ObjectId strings.
            return None  # Returns None instead of leaking a low-level database error.

        document = await self.collection.find_one({"_id": object_id})  # Queries MongoDB by primary key.
        return document  # Returns the found document or None.

    async def list_records(self, filters: Mapping[str, Any] | None = None,skip: int = 0, limit: int = DEFAULT_LIMIT ) -> list[dict[str, Any]]:  # Returns MongoDB documents as dictionaries.
        safe_limit = min(max(limit, 1), MAX_LIMIT)  # Forces the limit into a safe allowed range.
        safe_skip = max(skip, 0)  # Prevents negative skip values.
        safe_filters = dict( filters or {})  # Copies filters so caller input is not mutated.
        cursor = (self.collection.find(safe_filters).skip(safe_skip).limit(safe_limit))  # Builds the async cursor.
        return await cursor.to_list(length=safe_limit
        )  # Converts the cursor into a list.

    async def update_one_by_id(
        self,  # Uses the current Data Access Layer instance.
        record_id: str | ObjectId,  # Receives the MongoDB document ID.
        updates: Mapping[str, Any],  # Receives already-validated update data.
    ) -> bool:  # Returns whether MongoDB modified a document.
        try:  # Starts safe ObjectId conversion.
            object_id = normalize_object_id(
                record_id
            )  # Converts the incoming ID to ObjectId.
        except ValueError:  # Handles invalid ObjectId strings.
            return False  # Returns False because no valid document can be updated.

        update_data = {
            key: value for key, value in updates.items() if key != "_id"
        }  # Prevents changing `_id`.
        if not update_data:  # Checks whether anything remains after filtering.
            return False  # Returns False because there is nothing safe to update.

        result = await self.collection.update_one(
            {"_id": object_id}, {"$set": update_data}
        )  # Updates one document.
        return (
            result.modified_count == 1
        )  # Returns True only when MongoDB changed one document.

    async def delete_one_by_id(
        self, record_id: str | ObjectId
    ) -> bool:  # Deletes one document by ID.
        try:  # Starts safe ObjectId conversion.
            object_id = normalize_object_id(
                record_id
            )  # Converts the incoming ID to ObjectId.
        except ValueError:  # Handles invalid ObjectId strings.
            return False  # Returns False because no valid document can be deleted.

        result = await self.collection.delete_one(
            {"_id": object_id}
        )  # Deletes one matching MongoDB document.
        return (
            result.deleted_count == 1
        )  # Returns True only when MongoDB deleted one document.

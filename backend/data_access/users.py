# =============================================================================
# File: users.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the users collection.
# Security Note: Password hashes may be stored, but plain text passwords must never reach this layer.
# SRS Traceability: Supports SRS v5.0 SE-001, SE-009, and Section 19 users collection.
# SDD Traceability: Supports SDD v5.0 database design and backend modular architecture.
# =============================================================================

from __future__ import annotations  # Enables modern type hints without runtime forward-reference issues.

from typing import Any  # Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase  # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import USERS_COLLECTION  # Imports the approved users collection name.


class UsersDataAccess(MongoDataAccess):  # Defines collection-specific access for users.
    """Data access helper for user documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[USERS_COLLECTION])  # Connects this helper to the users collection.

    async def find_by_username(self, username: str) -> dict[str, Any] | None:  # Finds one user by username.
        return await self.collection.find_one({"username": username})  # Returns the matching user or None.


async def get_user_by_username(db: Any, username: str) -> dict[str, Any] | None:  # Finds one user document by username.
    user_doc = await db["users"].find_one({"username": username})  # Queries the users collection for the matching username.
    return user_doc  # Returns the matching user document or None.


async def create_user(db: Any, user_doc: dict[str, Any]) -> str:  # Inserts a new user document into MongoDB.
    insert_result = await db["users"].insert_one(user_doc)  # Inserts the user document into the users collection.
    return str(insert_result.inserted_id)  # Returns the inserted MongoDB ObjectId as a string.
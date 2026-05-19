# =============================================================================
# File: data_access/token_denylist.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for revoked JWT token identifiers.
# Security Note: Stores only hashed JWT IDs, never raw JWT tokens.
# SRS Traceability: Supports SRS v5.0 SE-003, SE-004, SE-008, and SE-009.
# SDD Traceability: Supports SDD v5.0 authentication, API security, and backend modular architecture.
# =============================================================================

from __future__ import annotations  # Enables modern type hints without runtime forward-reference issues.

from datetime import datetime  # Imports datetime for token denylist expiration timestamps.
from typing import Any  # Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase  # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.


TOKEN_DENYLIST_COLLECTION = "token_denylist"  # Defines the MongoDB collection name for revoked token IDs.


class TokenDenylistDataAccess(MongoDataAccess):  # Defines collection-specific access for revoked JWT token IDs.
    """Data access helper for revoked JWT token identifiers."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[TOKEN_DENYLIST_COLLECTION])  # Connects this helper to the token denylist collection.

    async def add_token(self, jti_hash: str, expires_at: datetime) -> None:  # Stores a revoked token ID hash.
        await self.collection.update_one(  # Updates an existing denylist record or inserts a new one.
            {"jti_hash": jti_hash},  # Finds the denylist record by hashed JWT ID.
            {"$set": {"jti_hash": jti_hash, "expires_at": expires_at}},  # Stores the token hash and expiration timestamp.
            upsert=True,  # Creates the record if it does not already exist.
        )  # Ends the MongoDB update operation.

    async def is_denied(self, jti_hash: str) -> bool:  # Checks whether a token ID hash has been revoked.
        denylist_doc = await self.collection.find_one({"jti_hash": jti_hash})  # Searches for the token hash.
        return denylist_doc is not None  # Returns True when the token hash is already revoked.

    async def ensure_indexes(self) -> None:  # Creates indexes for token denylist uniqueness and cleanup.
        await self.collection.create_index("jti_hash", unique=True)  # Prevents duplicate denylist entries.
        await self.collection.create_index("expires_at", expireAfterSeconds=0)  # Removes denylist records after token expiration.


async def add_token_to_denylist(db: Any, jti_hash: str, expires_at: datetime) -> None:  # Stores a revoked token ID hash.
    await db[TOKEN_DENYLIST_COLLECTION].update_one(  # Updates an existing denylist record or inserts a new one.
        {"jti_hash": jti_hash},  # Finds the denylist record by hashed JWT ID.
        {"$set": {"jti_hash": jti_hash, "expires_at": expires_at}},  # Stores the token hash and expiration timestamp.
        upsert=True,  # Creates the record if it does not already exist.
    )  # Ends the MongoDB update operation.


async def is_token_denied(db: Any, jti_hash: str) -> bool:  # Checks whether a token ID hash has already been revoked.
    denylist_doc = await db[TOKEN_DENYLIST_COLLECTION].find_one({"jti_hash": jti_hash})  # Searches the denylist collection.
    return denylist_doc is not None  # Returns True when the token hash is found.


async def ensure_token_denylist_indexes(db: Any) -> None:  # Creates indexes for the token denylist collection.
    await db[TOKEN_DENYLIST_COLLECTION].create_index("jti_hash", unique=True)  # Prevents duplicate denylist entries.
    await db[TOKEN_DENYLIST_COLLECTION].create_index("expires_at", expireAfterSeconds=0)  # Removes records after expiration.
# =============================================================================
# File: reward_accounts.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the reward_accounts collection.
# Security Note: Reward account records must not contain account login credentials.
# SRS Traceability: Supports SRS v5.0 rewards requirements and Section 19.
# SDD Traceability: Supports SDD v5.0 reward accounts database design.
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
    REWARD_ACCOUNTS_COLLECTION,
)  # Imports the approved reward accounts collection name.


class RewardAccountsDataAccess(
    MongoDataAccess
):  # Defines collection-specific access for reward accounts.
    """Data access helper for reward account documents."""  # Documents the class purpose.

    def __init__(
        self, database: AsyncIOMotorDatabase
    ) -> None:  # Receives the MongoDB database dependency.
        super().__init__(
            database[REWARD_ACCOUNTS_COLLECTION]
        )  # Connects this helper to the reward accounts collection.

    async def find_by_program(
        self, program: str
    ) -> dict[str, Any] | None:  # Finds one reward account by program.
        return await self.collection.find_one(
            {"program": program}
        )  # Returns the matching reward account or None.

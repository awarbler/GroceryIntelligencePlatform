# =============================================================================
# File: reward_transactions.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the reward_transactions collection.
# Security Note: Reward transaction records must not contain credentials or tokens.
# SRS Traceability: Supports SRS v5.0 rewards transaction requirements and Section 19.
# SDD Traceability: Supports SDD v5.0 reward transactions database design.
# =============================================================================

from __future__ import annotations # Enables modern type hints without runtime forward-reference issues.

from typing import Any# Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.

from backend.database import REWARD_TRANSACTIONS_COLLECTION # Imports the approved reward transactions collection name.


class RewardTransactionsDataAccess(MongoDataAccess):  # Defines collection-specific access for reward transactions.
    """Data access helper for reward transaction documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[REWARD_TRANSACTIONS_COLLECTION])  # Connects this helper to the reward transactions collection.

    async def list_by_program(self, program_ref: str, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:  # Lists transactions by program.
        return await self.list_records(filters={"program_ref": program_ref}, skip=skip, limit=limit)  # Returns matching transactions.

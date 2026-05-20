# =============================================================================
# File: backend/data_access/deal_matches.py
# Project: Grocery Intelligence Platform
# Purpose: Provides Data Access Layer methods for saved deal matches.
# SRS Traceability: Section 16, Section 17, Section 18, Section 23
# SDD Traceability: Section 7.10, Section 9, Section 15
# =============================================================================

from datetime import date
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.data_access.base import MongoDataAccess
from backend.database import DEAL_MATCHES_COLLECTION
from backend.models.base import PyObjectId


class DealMatchesDataAccess(MongoDataAccess):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db[DEAL_MATCHES_COLLECTION])

    async def delete_by_week(self, week_of: date) -> int:
        result = await self.collection.delete_many({"week_of": week_of.isoformat()})
        return result.deleted_count

    async def insert_many_matches(self, matches: list[dict[str, Any]]) -> list[PyObjectId]:
        if not matches:
            return []

        result = await self.collection.insert_many(matches)
        return list(result.inserted_ids)

    async def list_by_week(self, week_of: date) -> list[dict[str, Any]]:
        cursor = self.collection.find({"week_of": week_of.isoformat()})
        return await cursor.to_list(length=None)

    async def find_by_week(self, week_of: str | date) -> dict[str, Any] | None:
        week_date = date.fromisoformat(week_of) if isinstance(week_of, str) else week_of
        matches = await self.list_by_week(week_date)
        return matches[0] if matches else None
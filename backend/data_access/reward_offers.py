# =============================================================================
# File: backend/data_access/reward_offers.py
# Project: Grocery Intelligence Platform
# Purpose: Provides Data Access Layer helpers for reward offer documents.
# SRS Traceability: SRS Section 16, SRS Section 17 SB-004, SRS Section 20 TS-005, SRS Section 23
# SDD Traceability: SDD Section 7, SDD Section 9, SDD Section 15
# =============================================================================

from datetime import date  # Imports date for expiration-window filtering.

from motor.motor_asyncio import AsyncIOMotorDatabase  # Imports MongoDB async database type.

from backend.data_access.base import MongoDataAccess  # Imports the shared DAL base class.
from backend.models.reward_offer import RewardProvider  # Imports provider enum for provider filters.


class RewardOffersDataAccess(MongoDataAccess):  # Defines reward offer DAL operations.
    def __init__(self, db: AsyncIOMotorDatabase) -> None:  # Initializes the reward offer DAL with a database.
        super().__init__(db=db, collection_name="reward_offers")  # Connects this DAL to the reward_offers collection.

    async def list_active_reward_offers(self) -> list[dict]:  # Lists active reward offers.
        cursor = self.collection.find({"is_active": True})  # Builds query for active offers only.
        return await cursor.to_list(length=None)  # Converts Mongo cursor results to a list.

    async def list_by_provider(self, provider: RewardProvider) -> list[dict]:  # Lists offers for one provider.
        cursor = self.collection.find({"reward_provider": provider.value})  # Builds provider-specific query.
        return await cursor.to_list(length=None)  # Converts Mongo cursor results to a list.

    async def list_by_retailer(self, retailer: str) -> list[dict]:  # Lists offers for one retailer.
        cursor = self.collection.find({"retailer": retailer})  # Builds retailer-specific query.
        return await cursor.to_list(length=None)  # Converts Mongo cursor results to a list.

    async def list_expiring_between(self, start_date: date, end_date: date) -> list[dict]:  # Lists offers by expiration window.
        cursor = self.collection.find({"expiration_date": {"$gte": start_date, "$lte": end_date}})  # Builds date-window query.
        return await cursor.to_list(length=None)  # Converts Mongo cursor results to a list.
    
    async def list_active_offers(self, retailer: str) -> list[dict]:  # Lists active reward offers by retailer
        cursor = self.collection.find({"retailer": retailer, "is_active": True})  # Finds active retailer rewards
        return await cursor.to_list(length=None)  # Returns all active rewards
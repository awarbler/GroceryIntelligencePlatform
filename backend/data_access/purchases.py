# =============================================================================
# File: data_access/purchases.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the purchases collection.
# Security Note: Purchase records must not contain passwords, tokens, or store credentials.
# SRS Traceability: Supports SRS v5.0 PL-032, PL-033, PL-034, SE-009, and Section 19.
# SDD Traceability: Supports SDD v5.0 purchases database design.
# =============================================================================

from __future__ import annotations # Enables modern type hints without runtime forward-reference issues.

from typing import Any# Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import  PURCHASES_COLLECTION# Imports the approved purchases collection name.
from bson import ObjectId  # Converts purchase id strings to MongoDB ObjectId values.

class PurchasesDataAccess(MongoDataAccess):  # Defines collection-specific access for purchases.
    """Data access helper for purchase documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[PURCHASES_COLLECTION])  # Connects this helper to the purchases collection.
        
    async def insert_many_purchases(self, documents: list[dict[str, Any]]) -> list[str]:  # Inserts multiple approved purchase documents.
            if not documents:  # Checks whether the loader received an empty purchase list.
                return []  # Returns no IDs because there are no purchase documents to insert.

            result = await self.collection.insert_many(documents)  # Inserts all approved purchase documents through the Data Access Layer.
            return [str(inserted_id) for inserted_id in result.inserted_ids]  # Converts MongoDB ObjectIds to strings for the loader result.


    async def list_by_filters(
        self,  # Uses this purchases data access helper.
        store_ref: str | None = None,  # Optionally filters by store reference.
        start_date: str
        | None = None,  # Optionally filters purchases on or after this date.
        end_date: str
        | None = None,  # Optionally filters purchases on or before this date.
        category: str | None = None,  # Optionally filters by product category.
        rebate_status: str | None = None,  # Optionally filters by rebate status.
        source_type: str | None = None,  # Optionally filters by input source type.
        skip: int = 0,  # Skips this many records for pagination.
        limit: int = 100,  # Limits the number of returned records.
    ) -> list[dict[str, Any]]:  # Returns matching purchase documents.
        filters: dict[str, Any] = {}  # Builds a MongoDB filter dictionary.

        if store_ref is not None:  # Checks whether a store filter was supplied.
            filters["store_ref"] = store_ref  # Adds the store filter.

        if category is not None:  # Checks whether a category filter was supplied.
            filters["category"] = category  # Adds the category filter.

        if (rebate_status is not None):  # Checks whether a rebate status filter was supplied.
            filters["rebate_status"] = rebate_status  # Adds the rebate status filter.

        if source_type is not None:  # Checks whether a source type filter was supplied.
            filters["source_type"] = source_type  # Adds the source type filter.

        if (start_date is not None or end_date is not None):  # Checks whether a date range filter is needed.
            date_filter: dict[str, str] = {}  # Builds a nested purchase date filter.

            if start_date is not None:  # Checks whether a start date was supplied.
                date_filter["$gte"] = start_date  # Adds the lower bound date filter.

            if end_date is not None:  # Checks whether an end date was supplied.
                date_filter["$lte"] = end_date  # Adds the upper bound date filter.

            filters["purchase_date"] = date_filter  # Adds the date range filter.

        return await self.list_records(
            filters=filters, skip=skip, limit=limit
        )  # Returns matching purchases.

    async def create_purchase(self, purchase_doc: dict[str, Any]) -> dict[str, Any] | None:  # Inserts one validated purchase document.
        result = await self.collection.insert_one(purchase_doc)  # Writes the purchase document to MongoDB.
        return await self.collection.find_one({"_id": result.inserted_id})  # Returns the inserted document.

    async def get_purchase_by_id(self, purchase_id: ObjectId) -> dict[str, Any] | None:  # Finds one purchase by ObjectId.
        return await self.collection.find_one({"_id": purchase_id})  # Returns the matching purchase or None.

    async def update_purchase_by_id(self, purchase_id: ObjectId, updates: dict[str, Any]) -> dict[str, Any] | None:  # Updates one purchase.
        await self.collection.update_one({"_id": purchase_id}, {"$set": updates})  # Applies the update document.
        return await self.collection.find_one({"_id": purchase_id})  # Returns the updated document.

    async def delete_purchase_by_id(self, purchase_id: ObjectId) -> bool:  # Deletes one purchase record.
        result = await self.collection.delete_one({"_id": purchase_id})  # Removes one matching purchase.
        return result.deleted_count == 1  # Returns True when one record was deleted.

    async def list_purchases(self, filters: dict[str, Any]) -> list[dict[str, Any]]:  # Lists purchases using optional filters.
        cursor = self.collection.find(filters).sort("purchase_date", -1)  # Queries matching purchases newest first.
        return await cursor.to_list(length=500)  # Returns up to 500 matching purchases.
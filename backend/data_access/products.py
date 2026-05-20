# =============================================================================
# File: data_access/products.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the products collection.
# Security Note: Product records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 Section 18 MI-001 through MI-004 and Section 19 products collection.
# SDD Traceability: Supports SDD v5.0 Section 7.3 product catalog and database design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints without runtime forward-reference issues.

from datetime import date  # Imports date for price history observed_date values.
from datetime import datetime  # Imports datetime for MongoDB-compatible date storage.
from datetime import timezone  # Imports timezone for UTC datetime values.
from decimal import Decimal  # Imports Decimal for exact money values.
from typing import Any  # Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase  # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import PRODUCTS_COLLECTION  # Imports the approved products collection name.


class ProductsDataAccess(MongoDataAccess):  # Defines collection-specific access for products.
    """Data access helper for product documents."""  # Documents the class purpose.

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # Receives the MongoDB database dependency.
        super().__init__(database[PRODUCTS_COLLECTION])  # Connects this helper to the products collection.

    async def find_by_canonical_name(self, canonical_name: str) -> dict[str, Any] | None:  # Finds a product by canonical name.
        return await self.collection.find_one({"canonical_name": canonical_name})  # Returns the product document or None.

    async def list_by_category(self, category: str) -> list[dict[str, Any]]:  # Lists products by category.
        return await self.list_records(filters={"category": category})  # Returns matching product documents.

    async def find_all_products(self) -> list[dict[str, Any]]:  # Returns all product documents for normalization lookup.
        cursor = self.collection.find({})  # Reads product documents through the Data Access Layer collection.
        return [document async for document in cursor]  # Converts the async cursor into a list inside the async method.

    async def upsert_product_alias_seed(  # Defines idempotent alias seed upsert for P1-09 normalization.
        self,  # Receives the product data access instance.
        canonical_name: str,  # Receives the canonical product name.
        aliases: list[str],  # Receives aliases to store in products.aliases[].
        brand: str | None,  # Receives optional brand metadata.
        category: str | None,  # Receives optional category metadata.
    ) -> None:  # Returns no value after the upsert completes.
        await self.collection.update_one(  # Updates products collection through the Data Access Layer only.
            {"canonical_name": canonical_name},  # Finds the product by canonical name.
            {  # Starts the MongoDB update document.
                "$setOnInsert": {  # Sets these fields only when inserting a new product document.
                    "canonical_name": canonical_name,  # Stores the canonical product name.
                    "brand": brand,  # Stores the product brand.
                    "category": category,  # Stores the product category.
                    "aliases": [],  # Initializes aliases for new product documents.
                },  # Ends insert-only field map.
                "$addToSet": {"aliases": {"$each": aliases}},  # Adds aliases without creating duplicates.
            },  # Ends the MongoDB update document.
            upsert=True,  # Creates the product document if it does not already exist.
        )  # Ends the MongoDB update call.

    async def update_price_history(  # Appends one observed price entry to a product document.
        self,  # Receives the products data access instance.
        canonical_name: str,  # Receives the normalized product name used to find the product.
        store_ref: str,  # Receives the store identifier or reference.
        regular_price: Decimal,  # Receives the observed regular price.
        sale_price: Decimal | None,  # Receives the observed sale price when known.
        observed_date: date,  # Receives the date when the price was observed.
        source: str,  # Receives the source label for the price observation.
    ) -> None:  # Returns no value after update.
        price_entry: dict[str, Any] = {  # Builds the price history entry.
            "store_ref": store_ref,  # Stores the store reference.
            "regular_price": float(regular_price),  # Stores the regular price in MongoDB-compatible form.
            "sale_price": float(sale_price) if sale_price is not None else None,  # Stores sale price when present.
            "observed_date": datetime(observed_date.year, observed_date.month, observed_date.day, tzinfo=timezone.utc),  # Stores date as UTC datetime.
            "source": source,  # Stores the price source.
        }  # Ends the price history entry.
        await self.collection.update_one(  # Updates the matching product document.
            {"canonical_name": canonical_name},  # Finds the product by canonical name.
            {"$push": {"price_history": price_entry}},  # Appends the price entry.
        )  # Ends MongoDB update call.

    async def add_product_alias(self, canonical_name: str, alias: str) -> bool:  # Adds one owner-approved alias.
        result = await self.collection.update_one(  # Updates the matching product document.
            {"canonical_name": canonical_name},  # Finds the product by canonical name.
            {"$addToSet": {"aliases": alias}},  # Adds alias without duplicates.
            upsert=False,  # Prevents accidental product creation.
        )  # Ends update call.
        return result.matched_count > 0  # Returns True when a product was matched.

    async def list_my_items(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:  # Lists owner My Items.
        return await self.list_records(filters={"is_my_item": True}, skip=skip, limit=limit)  # Returns only My Items.

    async def find_my_item_by_id(self, product_id: str) -> dict[str, Any] | None:  # Finds one My Item by id.
        document = await self.find_one_by_id(product_id)  # Reads the product document by id.
        if document is None:  # Checks whether the document exists.
            return None  # Returns no match.
        if document.get("is_my_item") is not True:  # Ensures normal catalog products are not returned.
            return None  # Returns no match.
        return document  # Returns the My Item document.

    async def create_my_item(self, document: dict[str, Any]) -> str:  # Inserts one My Item document.
        document["is_my_item"] = True  # Forces the My Item flag.
        return await self.create_one(document)  # Inserts through shared DAL helper.

    async def update_my_item(self, product_id: str, updates: dict[str, Any]) -> bool:  # Updates one My Item.
        existing = await self.find_my_item_by_id(product_id)  # Confirms the document is a My Item.
        if existing is None:  # Checks whether the item exists.
            return False  # Reports no update.
        return await self.update_one_by_id(product_id, updates)  # Updates through shared DAL helper.

    async def delete_my_item(self, product_id: str) -> bool:  # Deletes one My Item.
        existing = await self.find_my_item_by_id(product_id)  # Confirms the document is a My Item.
        if existing is None:  # Checks whether the item exists.
            return False  # Reports no delete.
        return await self.delete_one_by_id(product_id)  # Deletes through shared DAL helper.

    async def update_my_item_avg_price(self, canonical_name: str, observed_price: Decimal) -> bool:  # Updates running avg_price.
        document = await self.collection.find_one({"canonical_name": canonical_name, "is_my_item": True})  # Finds matching My Item.
        if document is None:  # Checks whether a matching My Item exists.
            return False  # Reports no update.
        old_avg = Decimal(str(document.get("avg_price", "0.00")))  # Reads existing average safely.
        old_count = int(document.get("avg_price_observation_count", 0))  # Reads existing observation count.
        new_count = old_count + 1  # Adds the new observation.
        new_avg = ((old_avg * old_count) + observed_price) / new_count  # Calculates running average.
        await self.collection.update_one(  # Updates the matching document.
            {"_id": document["_id"]},  # Targets the matched document.
            {"$set": {"avg_price": float(new_avg), "avg_price_observation_count": new_count}},  # Stores updated average.
        )  # Ends update call.
        return True  # Reports update success.
    async def find_my_items(self) -> list[dict]:  # Lists products marked as My Items
        cursor = self.collection.find({"is_my_item": True})  # Finds user regular items
        return await cursor.to_list(length=None)  # Returns all matching products
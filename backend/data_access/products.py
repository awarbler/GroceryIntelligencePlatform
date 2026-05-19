# =============================================================================
# File: data_access/products.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the products collection.
# Security Note: Product records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 Section 19 products collection.
# SDD Traceability: Supports SDD v5.0 product catalog and database design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints without runtime forward-reference issues.

from typing import Any  # Imports Any because MongoDB documents contain mixed field types.

from motor.motor_asyncio import AsyncIOMotorDatabase  # Imports the async Motor database type.

from backend.data_access.base import MongoDataAccess  # Imports shared CRUD behavior.
from backend.database import PRODUCTS_COLLECTION  # Imports the approved products collection name.
from datetime import date  # Imports date for price history observed_date values.
from decimal import Decimal  # Imports Decimal for exact money values.

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
            self,
            canonical_name: str,
            store_ref: str,
            regular_price: Decimal,
            sale_price: Decimal | None,
            observed_date: date,
            source: str,
        ) -> None:
            from datetime import datetime, timezone
            price_entry: dict = {
                "store_ref": store_ref,
                "regular_price": float(regular_price),  # Convert Decimal for MongoDB BSON.
                "sale_price": float(sale_price) if sale_price is not None else None,
                "observed_date": datetime(observed_date.year, observed_date.month, observed_date.day, tzinfo=timezone.utc),  # Convert date to datetime for MongoDB BSON.
                "source": source,
            }
            await self.collection.update_one(
                {"canonical_name": canonical_name},
                {"$push": {"price_history": price_entry}},
            )

        async def add_product_alias(  # Adds one owner-approved alias to a product document.
            self,
            canonical_name: str,
            alias: str,
        ) -> bool:
            result = await self.collection.update_one(
                {"canonical_name": canonical_name},
                {"$addToSet": {"aliases": alias}},
                upsert=False,
            )
            return result.matched_count > 0

        async def list_my_items(self) -> list[dict]:  # Returns all products where is_my_item is True.
            return await self.list_records(filters={"is_my_item": True})

        async def find_by_id(self, product_id: str) -> dict | None:  # Finds one product by ID.
            return await self.find_one_by_id(product_id)

        async def update_my_item(self, product_id: str, updates: dict) -> bool:  # Updates one product by ID.
            return await self.update_one_by_id(product_id, updates)

        async def delete_my_item(self, product_id: str) -> bool:  # Deletes one product by ID.
            return await self.delete_one_by_id(product_id)

        async def create_my_item(self, document: dict) -> str:  # Inserts one My Items product document.
            return await self.create_one(document)

        async def update_avg_price_for_store(  # Updates avg_price_by_store for one store after a purchase is saved.
            self,
            canonical_name: str,
            store_id: str,
            price: float,
        ) -> None:
            await self.collection.update_one(
                {"canonical_name": canonical_name},
                {"$set": {f"avg_price_by_store.{store_id}": price}},
            )
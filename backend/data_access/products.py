# =============================================================================
# File: products.py
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
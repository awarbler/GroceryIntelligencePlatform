# =============================================================================
# File: products.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides Data Access Layer operations for the products collection.
# Security Note: Product records must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 Section 19 products collection.
# SDD Traceability: Supports SDD v5.0 product catalog and database design.
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
    PRODUCTS_COLLECTION,
)  # Imports the approved products collection name.


class ProductsDataAccess(
    MongoDataAccess
):  # Defines collection-specific access for products.
    """Data access helper for product documents."""  # Documents the class purpose.

    def __init__(
        self, database: AsyncIOMotorDatabase
    ) -> None:  # Receives the MongoDB database dependency.
        super().__init__(
            database[PRODUCTS_COLLECTION]
        )  # Connects this helper to the products collection.

    async def find_by_canonical_name(
        self, canonical_name: str
    ) -> dict[str, Any] | None:  # Finds a product by canonical name.
        return await self.collection.find_one(
            {"canonical_name": canonical_name}
        )  # Returns the product or None.

    async def list_by_category(
        self, category: str
    ) -> list[dict[str, Any]]:  # Lists products by category.
        return await self.list_records(
            filters={"category": category}
        )  # Returns matching product documents.

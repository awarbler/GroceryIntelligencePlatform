# =============================================================================
# File: services/my_items_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides service-layer operations for My Items CRUD.
# Security Note: My Items must not contain credentials, tokens, or payment data.
# SRS Traceability: Supports SRS v5.0 Section 18 MI-001 through MI-004.
# SDD Traceability: Supports SDD v5.0 Section 7.3 products and Section 8 API Endpoint Design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints.

from datetime import datetime  # Imports datetime for timestamp conversion.
from datetime import timezone  # Imports timezone for UTC timestamps.
from decimal import Decimal  # Imports Decimal for exact money values.
from typing import Any  # Imports Any for MongoDB document dictionaries.

from backend.data_access.products import ProductsDataAccess  # Imports the existing products DAL.


class MyItemNotFoundError(KeyError):  # Defines the service error for missing My Items.
    """Raised when a My Item cannot be found."""  # Documents the exception purpose.


class MyItemService:  # Defines service-layer behavior for My Items.
    """Coordinates My Items CRUD through ProductsDataAccess."""  # Documents the service purpose.

    def __init__(self, products_access: ProductsDataAccess) -> None:  # Receives the DAL dependency.
        self._products_access = products_access  # Stores the products DAL dependency.

    async def list_my_items(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:  # Lists My Items.
        documents = await self._products_access.list_my_items(skip=skip, limit=limit)  # Reads My Items from DAL.
        return [_serialize_document(document) for document in documents]  # Returns serialized documents.

    async def get_my_item(self, item_id: str) -> dict[str, Any]:  # Gets one My Item.
        document = await self._products_access.find_my_item_by_id(item_id)  # Reads one My Item from DAL.
        if document is None:  # Checks whether the item exists.
            raise MyItemNotFoundError(item_id)  # Raises not-found error.
        return _serialize_document(document)  # Returns serialized document.

    async def create_my_item(self, payload: dict[str, Any]) -> dict[str, Any]:  # Creates one My Item.
        document = _prepare_create_document(payload)  # Prepares MongoDB-safe document.
        item_id = await self._products_access.create_my_item(document)  # Inserts through DAL.
        created = await self._products_access.find_my_item_by_id(item_id)  # Reads created document.
        if created is None:  # Checks for unexpected insert failure.
            raise MyItemNotFoundError(item_id)  # Raises not-found error.
        return _serialize_document(created)  # Returns serialized created document.

    async def update_my_item(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:  # Updates one My Item.
        updates = _prepare_update_document(payload)  # Prepares MongoDB-safe updates.
        updated = await self._products_access.update_my_item(item_id, updates)  # Updates through DAL.
        if updated is False:  # Checks whether update matched a My Item.
            raise MyItemNotFoundError(item_id)  # Raises not-found error.
        document = await self._products_access.find_my_item_by_id(item_id)  # Reads updated item.
        if document is None:  # Checks whether updated item exists.
            raise MyItemNotFoundError(item_id)  # Raises not-found error.
        return _serialize_document(document)  # Returns serialized updated document.

    async def delete_my_item(self, item_id: str) -> dict[str, bool]:  # Deletes one My Item.
        deleted = await self._products_access.delete_my_item(item_id)  # Deletes through DAL.
        if deleted is False:  # Checks whether delete matched a My Item.
            raise MyItemNotFoundError(item_id)  # Raises not-found error.
        return {"deleted": True}  # Returns delete confirmation.

    async def update_avg_price_after_purchase(self, canonical_name: str, observed_price: Decimal) -> bool:  # Updates running average.
        return await self._products_access.update_my_item_avg_price(canonical_name, observed_price)  # Delegates to DAL.


def _prepare_create_document(payload: dict[str, Any]) -> dict[str, Any]:  # Converts create payload into MongoDB document.
    document = _convert_for_mongo(payload)  # Converts unsafe values for MongoDB.
    now = datetime.now(timezone.utc)  # Creates UTC timestamp.
    document["is_my_item"] = True  # Forces My Item flag.
    document["created_at"] = now  # Stores created timestamp.
    document["updated_at"] = now  # Stores updated timestamp.
    document.setdefault("raw_names", [])  # Ensures raw_names exists.
    document.setdefault("size_variants", [])  # Ensures size_variants exists.
    document.setdefault("avg_price_by_store", {})  # Ensures avg_price_by_store exists.
    document.setdefault("acceptable_substitutes", [])  # Ensures acceptable_substitutes exists.
    document.setdefault("preferred_stores", [])  # Ensures preferred_stores exists.
    document.setdefault("price_history", [])  # Ensures price_history exists.
    document.setdefault("store_refs", [])  # Ensures store_refs exists.
    document.setdefault("is_active", True)  # Ensures item is active by default.
    document.setdefault("notes", "")  # Ensures notes exists.
    document.setdefault("avg_price_observation_count", 0)  # Ensures average count exists.
    return document  # Returns prepared document.


def _prepare_update_document(payload: dict[str, Any]) -> dict[str, Any]:  # Converts update payload into MongoDB update fields.
    updates = _convert_for_mongo(payload)  # Converts unsafe values for MongoDB.
    updates.pop("_id", None)  # Prevents changing MongoDB id.
    updates.pop("id", None)  # Prevents changing API id.
    updates.pop("is_my_item", None)  # Prevents changing My Item ownership flag.
    updates.pop("created_at", None)  # Prevents changing created timestamp.
    updates["updated_at"] = datetime.now(timezone.utc)  # Updates modified timestamp.
    return updates  # Returns safe update dictionary.


def _convert_for_mongo(value: Any) -> Any:  # Converts values into MongoDB-safe types.
    if isinstance(value, Decimal):  # Checks for Decimal values.
        return float(value)  # Converts Decimal to MongoDB-compatible float.
    if isinstance(value, dict):  # Checks for dictionaries.
        return {key: _convert_for_mongo(item) for key, item in value.items()}  # Converts dictionary values.
    if isinstance(value, list):  # Checks for lists.
        return [_convert_for_mongo(item) for item in value]  # Converts list items.
    return value  # Returns already-safe value.


def _serialize_document(document: dict[str, Any]) -> dict[str, Any]:  # Converts MongoDB document into API-safe response.
    serialized = dict(document)  # Copies the document.
    if "_id" in serialized:  # Checks for MongoDB id.
        serialized["id"] = str(serialized.pop("_id"))  # Converts _id to string id.
    if "avg_price" in serialized and serialized["avg_price"] is not None:  # Checks for avg_price.
        serialized["avg_price"] = str(serialized["avg_price"])  # Serializes avg_price consistently.
    serialized["acceptable_substitutes"] = list(serialized.get("acceptable_substitutes", []))  # Ensures substitutes is a list.
    serialized["preferred_stores"] = list(serialized.get("preferred_stores", []))  # Ensures preferred stores is a list.
    return serialized  # Returns API-safe document.
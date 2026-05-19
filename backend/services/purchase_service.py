# =============================================================================
# File: backend/services/purchase_service.py
# Project: Grocery Intelligence Platform
# Purpose: Provides business logic for P1-14 purchase CRUD endpoints.
# SRS Traceability: SRS v5.0 Section 5 PL-001 through PL-034; Section 21 SE-009.
# SDD Traceability: SDD v5.0 Section 7.4 purchases document; Section 8 API Endpoint Design.
# =============================================================================

from datetime import date, datetime, time, timezone  # Supports date range filter conversion.

from bson import ObjectId  # Converts route id strings into MongoDB ObjectId values.
from pydantic import ValidationError  # Handles Pydantic validation failures.

from backend.data_access.purchases import PurchasesDataAccess  # Uses the existing purchases Data Access Layer.
from backend.models.purchase import PurchaseModel  # Validates full purchase documents.


def _validate_object_id(purchase_id: str) -> ObjectId:  # Validates a route id string.
    if not ObjectId.is_valid(purchase_id):  # Rejects malformed MongoDB ids.
        raise ValueError("Invalid purchase id.")  # Raises a service-level validation error.
    return ObjectId(purchase_id)  # Returns a valid ObjectId.


def _start_of_day(value: date) -> datetime:  # Converts date_from into inclusive datetime.
    return datetime.combine(value, time.min, tzinfo=timezone.utc)  # Uses UTC start of day.


def _end_of_day(value: date) -> datetime:  # Converts date_to into inclusive datetime.
    return datetime.combine(value, time.max, tzinfo=timezone.utc)  # Uses UTC end of day.


def build_purchase_filters(  # Builds MongoDB-safe filters from query parameters.
    store: str | None = None,  # Optional store filter.
    date_from: date | None = None,  # Optional start date filter.
    date_to: date | None = None,  # Optional end date filter.
    category: str | None = None,  # Optional category filter.
    input_type: str | None = None,  # Optional input type filter.
    rebate_status: str | None = None,  # Optional rebate status filter.
) -> dict:  # Returns a MongoDB filter dictionary.
    filters: dict = {}  # Starts with no filters.

    if store is not None:  # Applies store filter only when provided.
        filters["store_ref"] = store  # Matches the purchase store reference.

    if category is not None:  # Applies category filter only when provided.
        filters["category"] = category  # Matches purchase category.

    if input_type is not None:  # Applies input type filter only when provided.
        filters["input_type"] = input_type  # Matches manual, PDF, receipt, or other input type values.

    if rebate_status is not None:  # Applies rebate status filter only when provided.
        filters["rebate_status"] = rebate_status  # Matches rebate workflow state.

    if date_from is not None or date_to is not None:  # Adds purchase date filter only when needed.
        filters["purchase_date"] = {}  # Creates a date range filter object.

    if date_from is not None:  # Adds lower date bound when provided.
        filters["purchase_date"]["$gte"] = _start_of_day(date_from)  # Includes purchases on or after date_from.

    if date_to is not None:  # Adds upper date bound when provided.
        filters["purchase_date"]["$lte"] = _end_of_day(date_to)  # Includes purchases on or before date_to.

    return filters  # Returns the final filters.


async def list_purchases(  # Lists purchases through the Data Access Layer.
    dal: PurchasesDataAccess,  # Receives the purchases DAL.
    store: str | None = None,  # Optional store filter.
    date_from: date | None = None,  # Optional date_from filter.
    date_to: date | None = None,  # Optional date_to filter.
    category: str | None = None,  # Optional category filter.
    input_type: str | None = None,  # Optional input type filter.
    rebate_status: str | None = None,  # Optional rebate status filter.
) -> list[dict]:  # Returns purchase documents.
    filters = build_purchase_filters(store, date_from, date_to, category, input_type, rebate_status)  # Builds filters.
    return await dal.list_purchases(filters)  # Reads matching purchases from MongoDB.


async def create_purchase(dal: PurchasesDataAccess, payload: dict) -> dict:  # Creates one manual purchase.
    try:  # Starts validation block.
        purchase = PurchaseModel.model_validate(payload)  # Validates the request using the existing model.
    except ValidationError as exc:  # Handles invalid request data.
        raise ValueError(str(exc)) from exc  # Converts validation error to service error.

    purchase_doc = purchase.model_dump(by_alias=True, exclude_none=True)  # Converts model to Mongo-ready dict.
    return await dal.create_purchase(purchase_doc)  # Saves through DAL only.


async def update_purchase(dal: PurchasesDataAccess, purchase_id: str, payload: dict) -> dict:  # Updates one purchase.
    object_id = _validate_object_id(purchase_id)  # Validates the purchase id.
    existing = await dal.get_purchase_by_id(object_id)  # Loads existing purchase.

    if existing is None:  # Handles missing purchase.
        raise LookupError("Purchase not found.")  # Raises not-found error.

    merged = {**existing, **payload}  # Merges existing document with requested changes.
    merged["_id"] = existing["_id"]  # Preserves the original MongoDB id.

    try:  # Starts validation block.
        validated = PurchaseModel.model_validate(merged)  # Validates the updated full purchase document.
    except ValidationError as exc:  # Handles invalid update data.
        raise ValueError(str(exc)) from exc  # Converts validation error to service error.

    update_doc = validated.model_dump(by_alias=True, exclude_none=True)  # Converts validated model to dict.
    update_doc.pop("_id", None)  # Prevents changing MongoDB primary key.

    updated = await dal.update_purchase_by_id(object_id, update_doc)  # Updates through DAL only.
    if updated is None:  # Handles unexpected missing record.
        raise LookupError("Purchase not found.")  # Raises not-found error.
    return updated  # Returns updated purchase.


async def delete_purchase(dal: PurchasesDataAccess, purchase_id: str) -> bool:  # Deletes one purchase.
    object_id = _validate_object_id(purchase_id)  # Validates the purchase id.
    deleted = await dal.delete_purchase_by_id(object_id)  # Deletes through DAL only.

    if not deleted:  # Handles missing purchase.
        raise LookupError("Purchase not found.")  # Raises not-found error.

    return deleted  # Returns deletion result.
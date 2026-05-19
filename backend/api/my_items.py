# =============================================================================
# File: api/my_items.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines My Items CRUD API endpoints.
# Security Note: Routes validate input and do not access MongoDB directly.
# SRS Traceability: Supports SRS v5.0 Section 18 MI-001 through MI-004.
# SDD Traceability: Supports SDD v5.0 Section 7.3 products and Section 8 API Endpoint Design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints.

from decimal import Decimal  # Imports Decimal for exact money validation.

from fastapi import APIRouter  # Imports API router.
from fastapi import Depends  # Imports dependency injection helper.
from fastapi import HTTPException  # Imports HTTP error helper.
from fastapi import Query  # Imports query parameter validation.
from fastapi import status  # Imports HTTP status constants.

from pydantic import BaseModel  # Imports Pydantic base model.
from pydantic import ConfigDict  # Imports Pydantic config helper.
from pydantic import Field  # Imports Pydantic field helper.

from backend.data_access.products import ProductsDataAccess  # Imports products DAL for service wiring.
from backend.database import get_db  # Imports centralized database dependency.
from backend.models.base import SuccessResponse  # Imports standard success response wrapper.
from backend.services.my_items_service import MyItemNotFoundError  # Imports not-found service error.
from backend.services.my_items_service import MyItemService  # Imports My Items service.


router = APIRouter(prefix="/my-items", tags=["my-items"])  # Creates router mounted under /api/v1 by routes.py.


class MyItemCreate(BaseModel):  # Defines POST request body validation.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected request fields.

    item_name: str = Field(..., min_length=1)  # Stores owner-facing item name.
    canonical_name: str = Field(..., min_length=1)  # Stores normalized name used for matching.
    category: str = Field(default="grocery", min_length=1)  # Stores item category.
    brand: str | None = Field(default=None)  # Stores optional brand.
    size: str | None = Field(default=None, min_length=1)  # Stores optional package size text.
    avg_price: Decimal | None = Field(default=None, ge=Decimal("0.00"))  # Stores optional average price.
    acceptable_substitutes: list[str] = Field(default_factory=list)  # Stores acceptable substitutes as a list.
    preferred_stores: list[str] = Field(default_factory=list)  # Stores preferred stores as a list.
    notes: str = Field(default="")  # Stores optional notes.


class MyItemUpdate(BaseModel):  # Defines PATCH request body validation.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected request fields.

    item_name: str | None = Field(default=None, min_length=1)  # Updates owner-facing item name.
    canonical_name: str | None = Field(default=None, min_length=1)  # Updates normalized name.
    category: str | None = Field(default=None, min_length=1)  # Updates item category.
    brand: str | None = Field(default=None)  # Updates optional brand.
    size: str | None = Field(default=None, min_length=1)  # Updates optional package size text.
    avg_price: Decimal | None = Field(default=None, ge=Decimal("0.00"))  # Updates optional average price.
    acceptable_substitutes: list[str] | None = Field(default=None)  # Updates acceptable substitutes.
    preferred_stores: list[str] | None = Field(default=None)  # Updates preferred stores.
    notes: str | None = Field(default=None)  # Updates notes.

def get_my_items_service(database=Depends(get_db)) -> MyItemService:  # Builds service dependency without importing Motor in the route.
    return MyItemService(ProductsDataAccess(database))  # Injects products DAL into service.


@router.get("", response_model=SuccessResponse)  # Defines GET /api/v1/my-items.
async def list_my_items(  # Handles My Items list requests.
    skip: int = Query(default=0, ge=0),  # Reads pagination skip.
    limit: int = Query(default=100, ge=1, le=500),  # Reads pagination limit.
    service: MyItemService = Depends(get_my_items_service),  # Injects service.
) -> SuccessResponse:  # Returns standard success response.
    items = await service.list_my_items(skip=skip, limit=limit)  # Reads My Items through service.
    return SuccessResponse(data=items, meta={"count": len(items), "skip": skip, "limit": limit})  # Returns wrapped response.


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)  # Defines POST /api/v1/my-items.
async def create_my_item(  # Handles My Item creation.
    payload: MyItemCreate,  # Receives validated request body.
    service: MyItemService = Depends(get_my_items_service),  # Injects service.
) -> SuccessResponse:  # Returns standard success response.
    created = await service.create_my_item(payload.model_dump(exclude_none=True))  # Creates item through service.
    return SuccessResponse(data=created, meta={"created": True})  # Returns created item.


@router.patch("/{item_id}", response_model=SuccessResponse)  # Defines PATCH /api/v1/my-items/{item_id}.
async def update_my_item(  # Handles My Item updates.
    item_id: str,  # Receives item id from path.
    payload: MyItemUpdate,  # Receives validated request body.
    service: MyItemService = Depends(get_my_items_service),  # Injects service.
) -> SuccessResponse:  # Returns standard success response.
    try:  # Starts not-found handling.
        updated = await service.update_my_item(item_id, payload.model_dump(exclude_unset=True, exclude_none=True))  # Updates item.
        return SuccessResponse(data=updated, meta={"updated": True})  # Returns updated item.
    except MyItemNotFoundError as error:  # Handles missing My Item.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="My Item not found.") from error  # Returns 404.


@router.delete("/{item_id}", response_model=SuccessResponse)  # Defines DELETE /api/v1/my-items/{item_id}.
async def delete_my_item(  # Handles My Item deletion.
    item_id: str,  # Receives item id from path.
    service: MyItemService = Depends(get_my_items_service),  # Injects service.
) -> SuccessResponse:  # Returns standard success response.
    try:  # Starts not-found handling.
        deleted = await service.delete_my_item(item_id)  # Deletes item through service.
        return SuccessResponse(data=deleted, meta={"deleted": True})  # Returns delete confirmation.
    except MyItemNotFoundError as error:  # Handles missing My Item.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="My Item not found.") from error  # Returns 404.
# =============================================================================
# File: backend/api/purchases.py
# Project: Grocery Intelligence Platform
# Purpose: Defines P1-14 purchase CRUD API endpoints.
# SRS Traceability: SRS v5.0 Section 5 PL-001 through PL-034; Section 21 SE-009.
# SDD Traceability: SDD v5.0 Section 7.4 purchases document; Section 8 API Endpoint Design.
# =============================================================================

from datetime import date  # Supports date query parameters.
from typing import Any  # Supports generic API response typing.

from fastapi import APIRouter, Depends, HTTPException, Query, status  # Provides FastAPI routing utilities.
from motor.motor_asyncio import AsyncIOMotorDatabase  # Used only as a dependency type annotation.

from backend.data_access.purchases import PurchasesDataAccess  # Builds the DAL dependency.
from backend.database import get_db  # Provides the database dependency.
from backend.services import purchase_service  # Calls service layer only for business logic.

router = APIRouter(prefix="/purchases", tags=["purchases"])  # Defines purchase routes mounted under /api/v1.


def get_purchases_dal(db: AsyncIOMotorDatabase = Depends(get_db)) -> PurchasesDataAccess:  # Creates DAL dependency.
    return PurchasesDataAccess(db)  # Returns purchases DAL for service calls.


@router.get("")  # Handles GET /api/v1/purchases.
async def get_purchases(  # Lists purchase records.
    store: str | None = Query(default=None),  # Optional store filter.
    date_from: date | None = Query(default=None),  # Optional inclusive start date.
    date_to: date | None = Query(default=None),  # Optional inclusive end date.
    category: str | None = Query(default=None),  # Optional category filter.
    input_type: str | None = Query(default=None),  # Optional input type filter.
    rebate_status: str | None = Query(default=None),  # Optional rebate status filter.
    dal: PurchasesDataAccess = Depends(get_purchases_dal),  # Injects purchases DAL.
) -> dict[str, Any]:  # Returns standard response dict.
    purchases = await purchase_service.list_purchases(  # Calls service layer only.
        dal=dal,  # Passes the DAL to the service.
        store=store,  # Passes store filter.
        date_from=date_from,  # Passes date_from filter.
        date_to=date_to,  # Passes date_to filter.
        category=category,  # Passes category filter.
        input_type=input_type,  # Passes input_type filter.
        rebate_status=rebate_status,  # Passes rebate_status filter.
    )
    return {"success": True, "data": purchases, "meta": {"count": len(purchases)}}  # Returns list response.


@router.post("", status_code=status.HTTP_201_CREATED)  # Handles POST /api/v1/purchases.
async def create_purchase(  # Creates one purchase.
    payload: dict[str, Any],  # Receives request body.
    dal: PurchasesDataAccess = Depends(get_purchases_dal),  # Injects purchases DAL.
) -> dict[str, Any]:  # Returns standard response dict.
    try:  # Starts service call block.
        purchase = await purchase_service.create_purchase(dal, payload)  # Calls service layer only.
    except ValueError as exc:  # Handles validation errors.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc  # Returns 422.
    return {"success": True, "data": purchase}  # Returns created purchase.


@router.patch("/{purchase_id}")  # Handles PATCH /api/v1/purchases/{id}.
async def patch_purchase(  # Updates one purchase.
    purchase_id: str,  # Receives purchase id from path.
    payload: dict[str, Any],  # Receives fields to update.
    dal: PurchasesDataAccess = Depends(get_purchases_dal),  # Injects purchases DAL.
) -> dict[str, Any]:  # Returns standard response dict.
    try:  # Starts service call block.
        purchase = await purchase_service.update_purchase(dal, purchase_id, payload)  # Calls service layer only.
    except LookupError as exc:  # Handles missing purchase.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc  # Returns 404.
    except ValueError as exc:  # Handles invalid id or invalid payload.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc  # Returns 422.
    return {"success": True, "data": purchase}  # Returns updated purchase.


@router.delete("/{purchase_id}")  # Handles DELETE /api/v1/purchases/{id}.
async def delete_purchase(  # Deletes one purchase.
    purchase_id: str,  # Receives purchase id from path.
    dal: PurchasesDataAccess = Depends(get_purchases_dal),  # Injects purchases DAL.
) -> dict[str, Any]:  # Returns standard response dict.
    try:  # Starts service call block.
        await purchase_service.delete_purchase(dal, purchase_id)  # Calls service layer only.
    except LookupError as exc:  # Handles missing purchase.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc  # Returns 404.
    except ValueError as exc:  # Handles invalid id.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc  # Returns 422.
    return {"success": True, "data": {"deleted": True}}  # Returns deletion result.
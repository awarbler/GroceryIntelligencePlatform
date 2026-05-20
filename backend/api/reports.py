# =============================================================================
# File: backend/api/reports.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines P1-19B weekly report JSON endpoint.
# Security Note: Route delegates report formatting to service layer.
# SRS Traceability: SRS Section 16 DR-001 through DR-021; SRS Section 20 TS-005.
# SDD Traceability: SDD Section 8 API Endpoint Design; SDD Section 9 Spending Analytics Design.
# =============================================================================

from __future__ import annotations  # Enables modern type-hint behavior.

from datetime import date  # Supports week_of query parsing.
from typing import Any  # Supports flexible response data.

from fastapi import APIRouter, Depends, Query  # Supports routing, dependency injection, and query validation.
from motor.motor_asyncio import AsyncIOMotorDatabase  # Provides database dependency type.

from backend.data_access.deal_matches import DealMatchesDataAccess  # Wires DAL dependency.
from backend.database import get_db  # Provides shared database dependency.
from backend.models.base import SuccessResponse  # Uses standard success response.
from backend.services.report_service import ReportService  # Uses report service.

router = APIRouter(prefix="/report", tags=["reports"])  # Creates /report router.


def get_report_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> ReportService:  # Builds service dependency.
    return ReportService(DealMatchesDataAccess(db))  # Injects DAL into service.


@router.get("/generate", response_model=SuccessResponse)  # Registers GET /api/v1/report/generate.
async def generate_report(  # Defines weekly report endpoint.
    week_of: date = Query(..., description="Report week date in YYYY-MM-DD format."),  # Requires week_of.
    store_ref: str | None = Query(default=None, description="Optional store reference filter."),  # Allows store filter.
    service: ReportService = Depends(get_report_service),  # Injects report service.
) -> SuccessResponse:  # Returns standard success response.
    report: dict[str, Any] = await service.generate_weekly_report(  # Builds report from saved matches.
        week_of=week_of,  # Passes week date.
        store_ref=store_ref,  # Passes optional store filter.
    )  # Ends service call.

    return SuccessResponse(  # Returns standardized response.
        data=report,  # Stores report payload.
        meta={  # Starts response metadata.
            "week_of": week_of.isoformat(),  # Stores report week.
            "match_count": report.get("match_count", 0),  # Stores match count.
            "store_count": len(report.get("stores", [])),  # Stores store count.
        },  # Ends metadata.
    )  # Ends response.
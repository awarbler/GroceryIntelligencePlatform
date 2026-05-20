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

from fastapi.responses import Response  # Supports downloadable binary file responses.
from backend.services.report_export_service import ReportExportService  # Builds PDF and DOCX report files.

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
    
@router.get("/download/pdf")  # Registers GET /api/v1/report/download/pdf.
async def download_report_pdf(  # Defines PDF download endpoint.
    week_of: date = Query(..., description="Report week date in YYYY-MM-DD format."),  # Requires week_of.
    store_ref: str | None = Query(default=None, description="Optional store reference filter."),  # Allows store filter.
    service: ReportService = Depends(get_report_service),  # Injects report JSON service.
) -> Response:  # Returns a binary PDF response.
    report: dict[str, Any] = await service.generate_weekly_report(  # Gets same JSON data as /generate.
        week_of=week_of,  # Passes week date.
        store_ref=store_ref,  # Passes optional store filter.
    )  # Ends report service call.

    pdf_bytes = ReportExportService().build_pdf(report=report)  # Converts report JSON to PDF bytes.
    filename = f"weekly-report-{week_of.isoformat()}.pdf"  # Builds safe deterministic filename.

    return Response(  # Returns downloadable PDF response.
        content=pdf_bytes,  # Sends generated PDF bytes.
        media_type="application/pdf",  # Sets correct PDF content type.
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},  # Sets download filename.
    )  # Ends response.


@router.get("/download/docx")  # Registers GET /api/v1/report/download/docx.
async def download_report_docx(  # Defines DOCX download endpoint.
    week_of: date = Query(..., description="Report week date in YYYY-MM-DD format."),  # Requires week_of.
    store_ref: str | None = Query(default=None, description="Optional store reference filter."),  # Allows store filter.
    service: ReportService = Depends(get_report_service),  # Injects report JSON service.
) -> Response:  # Returns a binary Word response.
    report: dict[str, Any] = await service.generate_weekly_report(  # Gets same JSON data as /generate.
        week_of=week_of,  # Passes week date.
        store_ref=store_ref,  # Passes optional store filter.
    )  # Ends report service call.

    docx_bytes = ReportExportService().build_docx(report=report)  # Converts report JSON to DOCX bytes.
    filename = f"weekly-report-{week_of.isoformat()}.docx"  # Builds safe deterministic filename.

    return Response(  # Returns downloadable DOCX response.
        content=docx_bytes,  # Sends generated DOCX bytes.
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # Sets Word content type.
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},  # Sets download filename.
    )  # Ends response.
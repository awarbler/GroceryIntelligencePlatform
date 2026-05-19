# =============================================================================
# File: backend/api/ad_etl.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Defines H-E-B weekly ad ETL upload, paste, session, and approval routes.
# Security Note: Handles public weekly ad data only and does not store credentials.
# SRS Traceability: Supports SRS v5.0 Section 7, Section 12, and Section 13.
# SDD Traceability: Supports SDD v5.0 Section 4, Section 7.5, and Section 8.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations.

from datetime import date  # Supports date fields.
from pathlib import Path  # Handles temporary PDF paths.
from tempfile import NamedTemporaryFile  # Creates temporary upload files.
from typing import Any  # Supports generic metadata dictionaries.

from fastapi import APIRouter  # Provides API router.
from fastapi import Depends  # Provides dependency injection.
from fastapi import File  # Supports file upload.
from fastapi import HTTPException  # Supports HTTP error responses.
from fastapi import UploadFile  # Represents uploaded file.
from motor.motor_asyncio import AsyncIOMotorDatabase  # Provides database type annotation.

from backend.data_access.ads import AdsDataAccess  # Imports ads DAL.
from backend.database import get_db  # Imports DB dependency.
from backend.etl.extractor import extract_pdf  # Reuses existing PDF extractor.
from backend.models.ad_correction import AdCorrectionItem  # Imports ad correction item.
from backend.models.ad_correction import AdCorrectionSession  # Imports ad correction session.
from backend.models.ad_correction import AdCorrectionSessionResponse  # Imports session response.
from backend.models.ad_correction import AdPipelineSessionResponse  # Imports session creation response.
from backend.models.ad_correction import ApproveAdSessionResponse  # Imports approval response.
from backend.models.ad_correction import PasteAdRequest  # Imports paste request.
from backend.parsers.heb.weekly_ad_parser import ParsedWeeklyAd  # Imports parser result type.
from backend.parsers.heb.weekly_ad_parser import parse_heb_weekly_ad  # Imports H-E-B weekly ad parser.
from backend.services import ad_service  # Imports ad service.
from backend.services.ad_correction_service import AdCorrectionSessionNotFoundError  # Imports not-found error.
from backend.services.ad_correction_service import ad_correction_session_store  # Imports shared session store.


router: APIRouter = APIRouter(tags=["ad-etl"])  # Creates ad ETL router.
HEB_AD_SOURCE_TYPE: str = "heb_weekly_ad"  # Defines H-E-B weekly ad source type.
HEB_STORE_NAME: str = "HEB"  # Defines Phase 1 store label.
HEB_STORE_REF: str = "507f1f77bcf86cd799439011"  # Defines fake ObjectId-compatible H-E-B store ref for Phase 1 tests.


@router.post("/etl/ad/paste", response_model=AdPipelineSessionResponse)  # Handles pasted H-E-B ad text.
async def paste_heb_weekly_ad(
    request: PasteAdRequest,  # Receives pasted ad text and optional dates.
) -> AdPipelineSessionResponse:
    raw_lines: list[str] = [line.strip() for line in request.text.splitlines() if line.strip()]  # Splits pasted text into lines.
    parsed_ad: ParsedWeeklyAd = parse_heb_weekly_ad(  # Parses pasted weekly ad text.
        raw_lines=raw_lines,  # Passes raw lines.
        source_type=HEB_AD_SOURCE_TYPE,  # Passes source type.
        store=HEB_STORE_NAME,  # Passes store label.
        start_date=request.start_date,  # Passes optional start date.
        end_date=request.end_date,  # Passes optional end date.
    )

    session: AdCorrectionSession = _build_ad_session(parsed_ad, raw_lines, {"file_path": "paste://heb-weekly-ad"})  # Builds ad session.
    saved_session: AdCorrectionSession = ad_correction_session_store.create_session(session)  # Saves session.
    return AdPipelineSessionResponse(session_id=saved_session.session_id, expires_at=saved_session.expires_at)  # Returns session ID.


@router.post("/etl/ad/upload", response_model=AdPipelineSessionResponse)  # Handles uploaded H-E-B weekly ad PDF.
async def upload_heb_weekly_ad(
    file: UploadFile = File(...),  # Receives uploaded PDF.
) -> AdPipelineSessionResponse:
    if file.filename is None or not file.filename.lower().endswith(".pdf"):  # Validates PDF filename.
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported for H-E-B weekly ads.")  # Rejects non-PDF upload.

    temp_path: Path | None = None  # Tracks temporary upload path.

    try:  # Starts protected file handling.
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:  # Creates temporary PDF.
            temp_path = Path(temp_file.name)  # Stores temp path.
            temp_file.write(await file.read())  # Writes uploaded bytes.

        extraction = extract_pdf(temp_path, file.filename)  # Reuses existing PDF extractor.
        parsed_ad: ParsedWeeklyAd = parse_heb_weekly_ad(  # Parses extracted PDF text.
            raw_lines=extraction.raw_lines,  # Passes extracted lines.
            source_type=HEB_AD_SOURCE_TYPE,  # Passes ad source type.
            store=HEB_STORE_NAME,  # Passes store label.
        )
        session: AdCorrectionSession = _build_ad_session(  # Builds correction session.
            parsed_ad=parsed_ad,  # Passes parsed ad.
            raw_lines=extraction.raw_lines,  # Passes raw lines.
            metadata={"filename": file.filename, "file_path": str(temp_path)},  # Stores metadata.
        )
        saved_session: AdCorrectionSession = ad_correction_session_store.create_session(session)  # Saves session.
        return AdPipelineSessionResponse(session_id=saved_session.session_id, expires_at=saved_session.expires_at)  # Returns session ID.

    finally:  # Ensures cleanup.
        if temp_path is not None and temp_path.exists():  # Checks temp file exists.
            temp_path.unlink()  # Deletes temp file.


@router.get("/ad-correction/{session_id}", response_model=AdCorrectionSessionResponse)  # Retrieves ad correction session.
def get_ad_correction_session(session_id: str) -> AdCorrectionSessionResponse:
    try:  # Starts protected lookup.
        session: AdCorrectionSession = ad_correction_session_store.get_session(session_id)  # Loads session.
        return AdCorrectionSessionResponse(session=session)  # Returns session.
    except AdCorrectionSessionNotFoundError as exc:  # Handles missing session.
        raise HTTPException(status_code=404, detail="Ad correction session was not found.") from exc  # Returns 404.


@router.post("/ad-correction/{session_id}/approve", response_model=ApproveAdSessionResponse)  # Approves ad session.
async def approve_ad_correction_session(
    session_id: str,  # Receives session ID.
    database: AsyncIOMotorDatabase = Depends(get_db),  # Receives database dependency.
) -> ApproveAdSessionResponse:
    try:  # Starts protected approval.
        session: AdCorrectionSession = ad_correction_session_store.get_session(session_id)  # Loads session.
    except AdCorrectionSessionNotFoundError as exc:  # Handles missing session.
        raise HTTPException(status_code=404, detail="Ad correction session was not found.") from exc  # Returns 404.

    ad_payload: dict[str, Any] = _session_to_ad_payload(session)  # Converts session to ad model payload.
    ads_access: AdsDataAccess = AdsDataAccess(database)  # Creates ads DAL.
    ad_id: str = await ad_service.create_ad(ads_access, ad_payload)  # Saves ad through service.
    ad_correction_session_store.delete_session(session_id)  # Removes approved session.
    return ApproveAdSessionResponse(ad_id=ad_id, item_count=len(ad_payload["items"]), parser_version=str(session.source_metadata.get("parser_version", "unknown")))  # Returns approval result.


def _build_ad_session(
    parsed_ad: ParsedWeeklyAd,
    raw_lines: list[str],
    metadata: dict[str, Any],
) -> AdCorrectionSession:
    """Build an ad correction session from parsed ad data."""
    if parsed_ad.start_date is None or parsed_ad.end_date is None:  # Requires dates before correction session.
        raise HTTPException(status_code=422, detail="start_date and end_date are required when ad text does not include a date range.")  # Returns validation error.

    items: list[AdCorrectionItem] = [  # Converts parsed items to correction items.
        AdCorrectionItem(  # Builds one correction item.
            raw_text=item.raw_text,  # Stores raw text.
            item_name=item.item_name,  # Stores item name.
            sale_price=item.sale_price,  # Stores sale price.
            regular_price=item.regular_price,  # Stores regular price.
            deal_type=item.deal_type,  # Stores deal type.
            size=item.size,  # Stores size.
        )
        for item in parsed_ad.items  # Iterates parsed items.
    ]

    metadata["parser_version"] = parsed_ad.parser_version  # Stores parser version.

    return AdCorrectionSession(  # Builds session.
        source_type=parsed_ad.source_type,  # Stores source type.
        store=parsed_ad.store,  # Stores store.
        start_date=parsed_ad.start_date,  # Stores start date.
        end_date=parsed_ad.end_date,  # Stores end date.
        raw_lines=raw_lines,  # Stores raw lines.
        items=items,  # Stores correction items.
        parse_errors=parsed_ad.parse_errors,  # Stores parse errors.
        source_metadata=metadata,  # Stores metadata.
    )


def _session_to_ad_payload(session: AdCorrectionSession) -> dict[str, Any]:
    """Convert approved ad correction session to AdModel payload."""
    return {  # Returns AdModel-compatible dictionary.
        "store_ref": HEB_STORE_REF,  # Stores Phase 1 H-E-B store reference.
        "start_date": session.start_date,  # Stores start date.
        "end_date": session.end_date,  # Stores end date.
        "source_type": session.source_type,  # Stores source type.
        "items": [  # Stores approved items.
            {  # Builds one ad item.
                "item_name": item.item_name,  # Stores item name.
                "sale_price": item.sale_price,  # Stores sale price.
                "regular_price": item.regular_price,  # Stores regular price.
                "deal_type": item.deal_type,  # Stores deal type.
                "size": item.size,  # Stores size.
                "raw_text": item.raw_text,  # Stores raw text.
            }
            for item in session.items  # Iterates correction items.
            if not item.skipped  # Excludes skipped items.
        ],
    }
    
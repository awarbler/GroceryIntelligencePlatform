# =============================================================================
# File: etl.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines P1-11 ETL and correction API routes.
# Security Note: Routes validate input and call pipeline functions instead of MongoDB directly.
# SRS Traceability: Supports SRS v5.0 Section 12, Section 13, and Section 21 SE-009.
# SDD Traceability: Supports SDD v5.0 Section 8 API Endpoint Design and Section 10.3 Input Validation.
# =============================================================================

from __future__ import annotations  # Enables modern type hint behavior.

from pathlib import Path  # Imports Path for temporary upload paths.
from tempfile import NamedTemporaryFile  # Imports temporary file support for uploads.

from fastapi import APIRouter  # Imports APIRouter for route registration.
from fastapi import Depends  # Imports Depends for dependency injection.
from fastapi import File  # Imports File for multipart upload handling.
from fastapi import HTTPException  # Imports HTTPException for API errors.
from fastapi import UploadFile  # Imports UploadFile for uploaded receipt PDFs.

from backend.data_access.products import ProductsDataAccess  # Imports products Data Access Layer.
from backend.data_access.purchases import PurchasesDataAccess  # Imports purchases Data Access Layer.
from backend.data_access.raw_inputs import RawInputsDataAccess  # Imports raw inputs Data Access Layer.
from backend.database import get_db  # Imports database accessor dependency.
from backend.etl.pipeline import approve_correction_session  # Imports approval pipeline function.
from backend.etl.pipeline import create_session_from_pasted_text  # Imports paste pipeline function.
from backend.etl.pipeline import create_session_from_pdf  # Imports upload pipeline function.
from backend.etl.pipeline import get_correction_session  # Imports session retrieval function.
from backend.etl.pipeline import save_item_normalization  # Imports alias-save pipeline function.
from backend.etl.pipeline import update_correction_item  # Imports item update pipeline function.
from backend.models.correction import ApproveSessionResponse  # Imports approval response model.
from backend.models.correction import CorrectionItemUpdateRequest  # Imports item update request model.
from backend.models.correction import CorrectionSessionResponse  # Imports session response model.
from backend.models.correction import NormalizeCorrectionRequest  # Imports normalize request model.
from backend.models.correction import NormalizeCorrectionResponse  # Imports normalize response model.
from backend.models.correction import PasteReceiptRequest  # Imports paste request model.
from backend.models.correction import PipelineSessionResponse  # Imports pipeline session response model.
from backend.services.correction_service import CorrectionItemNotFoundError  # Imports missing item error.
from backend.services.correction_service import CorrectionSessionNotFoundError  # Imports missing session error.

router: APIRouter = APIRouter(tags=["etl"])  # Creates the ETL API router.


@router.post("/etl/upload", response_model=PipelineSessionResponse)  # Registers the PDF upload route.
async def upload_heb_receipt(  # Defines the upload route handler.
    file: UploadFile = File(...),  # Receives the uploaded PDF file.
    database=Depends(get_db),  # Receives the active database dependency.
) -> PipelineSessionResponse:  # Returns the created correction session ID.
    if file.filename is None or not file.filename.lower().endswith(".pdf"):  # Checks whether the upload is a PDF.
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported for P1-11.")  # Rejects invalid uploads.

    temp_path: Path | None = None  # Tracks the temporary file path for cleanup.

    try:  # Starts protected upload handling.
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:  # Creates a temporary PDF file.
            temp_path = Path(temp_file.name)  # Stores the temporary file path.
            temp_file.write(await file.read())  # Writes uploaded bytes to the temporary file.

        product_access: ProductsDataAccess = ProductsDataAccess(database)  # Creates the products DAL.
        session = await create_session_from_pdf(temp_path, file.filename, product_access)  # Runs the upload pipeline.
        return PipelineSessionResponse(session_id=session.session_id, expires_at=session.expires_at)  # Returns session data.

    finally:  # Ensures cleanup always runs.
        if temp_path is not None and temp_path.exists():  # Checks whether the temporary file still exists.
            temp_path.unlink()  # Deletes the temporary upload file.


@router.post("/etl/paste", response_model=PipelineSessionResponse)  # Registers the paste route.
async def paste_heb_receipt(  # Defines the paste route handler.
    request: PasteReceiptRequest,  # Receives validated pasted text.
    database=Depends(get_db),  # Receives the active database dependency.
) -> PipelineSessionResponse:  # Returns the created correction session ID.
    product_access: ProductsDataAccess = ProductsDataAccess(database)  # Creates the products DAL.
    session = await create_session_from_pasted_text(request.text, product_access)  # Runs the paste pipeline.
    return PipelineSessionResponse(session_id=session.session_id, expires_at=session.expires_at)  # Returns session data.


@router.get("/correction/{session_id}", response_model=CorrectionSessionResponse)  # Registers the session retrieval route.
def get_session(session_id: str) -> CorrectionSessionResponse:  # Defines the session retrieval handler.
    try:  # Starts protected session lookup.
        session = get_correction_session(session_id)  # Retrieves the correction session.
        return CorrectionSessionResponse(session=session)  # Returns the session.
    except CorrectionSessionNotFoundError as exc:  # Handles missing or expired sessions.
        raise HTTPException(status_code=404, detail="Correction session was not found or has expired.") from exc  # Returns 404.


@router.patch("/correction/{session_id}/item/{item_id}", response_model=CorrectionSessionResponse)  # Registers item update route.
def patch_session_item(  # Defines the item update handler.
    session_id: str,  # Receives the session ID.
    item_id: str,  # Receives the item ID.
    request: CorrectionItemUpdateRequest,  # Receives validated update fields.
) -> CorrectionSessionResponse:  # Returns the updated session.
    try:  # Starts protected update.
        session = update_correction_item(session_id, item_id, request)  # Updates one item.
        return CorrectionSessionResponse(session=session)  # Returns updated session.
    except CorrectionSessionNotFoundError as exc:  # Handles missing session.
        raise HTTPException(status_code=404, detail="Correction session was not found or has expired.") from exc  # Returns 404.
    except CorrectionItemNotFoundError as exc:  # Handles missing item.
        raise HTTPException(status_code=404, detail="Correction item was not found.") from exc  # Returns 404.


@router.post("/correction/{session_id}/item/{item_id}/normalize", response_model=NormalizeCorrectionResponse)  # Registers alias-save route.
async def normalize_session_item(  # Defines the normalization correction handler.
    session_id: str,  # Receives the session ID.
    item_id: str,  # Receives the item ID.
    request: NormalizeCorrectionRequest,  # Receives validated alias data.
    database=Depends(get_db),  # Receives the active database dependency.
) -> NormalizeCorrectionResponse:  # Returns the updated session and alias.
    try:  # Starts protected alias save.
        product_access: ProductsDataAccess = ProductsDataAccess(database)  # Creates the products DAL.
        session = await save_item_normalization(session_id, item_id, request, product_access)  # Saves alias and updates session.
        return NormalizeCorrectionResponse(session=session, canonical_name=request.canonical_name, alias=request.alias)  # Returns result.
    except CorrectionSessionNotFoundError as exc:  # Handles missing session.
        raise HTTPException(status_code=404, detail="Correction session was not found or has expired.") from exc  # Returns 404.
    except CorrectionItemNotFoundError as exc:  # Handles missing item.
        raise HTTPException(status_code=404, detail="Correction item was not found.") from exc  # Returns 404.


@router.post("/correction/{session_id}/approve", response_model=ApproveSessionResponse)  # Registers approval route.
async def approve_session(  # Defines the approval route handler.
    session_id: str,  # Receives the session ID.
    database=Depends(get_db),  # Receives the active database dependency.
) -> ApproveSessionResponse:  # Returns Stage 3 load result.
    try:  # Starts protected approval.
        purchases_access: PurchasesDataAccess = PurchasesDataAccess(database)  # Creates purchases DAL.
        raw_inputs_access: RawInputsDataAccess = RawInputsDataAccess(database)  # Creates raw inputs DAL.
        products_access: ProductsDataAccess = ProductsDataAccess(database)  # Creates products DAL.
        return await approve_correction_session(session_id, purchases_access, raw_inputs_access, products_access)  # Runs approval.
    except CorrectionSessionNotFoundError as exc:  # Handles missing session.
        raise HTTPException(status_code=404, detail="Correction session was not found or has expired.") from exc  # Returns 404.
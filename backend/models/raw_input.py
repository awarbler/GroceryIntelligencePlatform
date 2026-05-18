# =============================================================================
# File: raw_input.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines the raw input document model used to preserve uploaded receipt, PDF, photo, CSV, and manual-entry data before parsing.
# Security Note: This model stores file metadata and extracted raw text lines, but it should not store passwords, tokens, or secret credentials.
# SRS Traceability: Supports SRS v5.0 raw input capture, ETL traceability, parser review, and reprocessing requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and ETL pipeline design.
# =============================================================================

from __future__ import annotations # Enables postponed evaluation of type hints for cleaner model references.

from datetime import datetime,timezone # Imports datetime tools for timestamp defaults.

from pydantic import ConfigDict,Field # Imports Pydantic configuration and field helpers.

from backend.models.base import BaseDocument,PyObjectId# Imports the shared MongoDB document base class and ObjectId type.
from backend.models.purchase import InputType# Imports the shared input source enum from the purchase model.
from bson import ObjectId  # Imports ObjectId so string IDs can be converted for MongoDB updates.

class RawInputModel(BaseDocument):  # Defines the MongoDB document model for raw uploaded or entered input.
    """Represents raw receipt, file, OCR, CSV, copy-paste, or manual input before parsing."""  # Documents the purpose of the raw input model.

    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields so raw input documents stay schema-controlled.

    source_type: InputType  # Stores the source category using the shared InputType enum from purchase.py.
    store_ref: PyObjectId  # Stores the MongoDB reference for the store connected to this raw input.
    filename: str  # Stores the original uploaded filename or generated source name.
    file_path: str  # Stores the local or managed path where the source file is stored.
    raw_lines: list[str] = Field(default_factory=list)  # Stores extracted raw text lines from OCR, PDF parsing, CSV, or manual input.
    ocr_confidence: float | None = (None)
    page_count: int = Field(ge=1)  # Stores the number of pages represented by the input and requires at least one page.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Stores when the raw input record was created.
    linked_record_ids: list[PyObjectId] = Field(default_factory=list)  # Stores references to parsed or corrected records created from this input.
    reprocessed: bool = False  # Tracks whether the raw input has been reprocessed after its first parse.
    parser_version: str  # Stores the parser version used or planned for this raw input.

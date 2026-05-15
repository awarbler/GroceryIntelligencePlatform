# =============================================================================
# File: store.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines store configuration models for parser routing and store-specific behavior.
# Security Note: Stores configuration references only and does not store login credentials.
# SRS Traceability: Supports SRS v5.0 store-specific parsing, receipt source handling, and correction workflow routing.
# SDD Traceability: Supports SDD v5.0 backend model validation and store configuration design.
# =============================================================================

from __future__ import annotations  # Enables forward-compatible type annotations.

from typing import Optional  # Imports Optional for fields that may be missing.

from pydantic import (
    Field,
)  # Imports Field for validation constraints and default values.

from backend.models.base import (
    BaseDocument,
    PyObjectId,
)  # Imports the shared document base and MongoDB object id type.


class StoreModel(BaseDocument):  # Defines the store configuration document.
    """Model representing a supported grocery, pharmacy, or retail store."""  # Documents the model purpose.

    store_id: str = Field(..., min_length=1)  # Stores the internal store identifier.
    display_name: str = Field(
        ..., min_length=1
    )  # Stores the human-readable store name.
    parser_module: Optional[str] = Field(
        default=None
    )  # Stores the parser module path for this store.
    active: bool = Field(
        default=True
    )  # Stores whether this store is active in the application.
    session_file: Optional[str] = Field(
        default=None
    )  # Stores the session file reference for browser-based workflows.
    login_url: Optional[str] = Field(
        default=None
    )  # Stores the store login URL when needed.
    abbreviation_table_ref: Optional[PyObjectId] = Field(
        default=None
    )  # Stores a reference to abbreviation mappings for this store.

# =============================================================================  # File header separator.
# File: models/correction.py  # Identifies this model file.
# Project: Grocery Intelligence Platform  # Identifies the project.
# Author: Anita Woodford  # Identifies the project author.
# Description: Defines correction-session models for the P1-11 ETL review workflow.  # Explains the file purpose.
# Security Note: Correction sessions must not store credentials, tokens, or payment card data.  # States security boundary.
# SRS Traceability: Supports SRS v5.0 Section 12 ET-003 and Section 13 HC-001 through HC-009.  # Maps to SRS.
# SDD Traceability: Supports SDD v5.0 Section 4 ETL Pipeline Design and Section 8 API Endpoint Design.  # Maps to SDD.
# =============================================================================  # File header separator.

from __future__ import annotations  # Enables modern type hint behavior.

from datetime import datetime  # Imports datetime for session timestamps.
from decimal import Decimal  # Imports Decimal for exact grocery quantity and money values.
from typing import Any  # Imports Any for flexible source metadata.

from pydantic import BaseModel  # Imports BaseModel for Pydantic validation.
from pydantic import ConfigDict  # Imports ConfigDict for strict model configuration.
from pydantic import Field  # Imports Field for validation constraints.


REVIEW_REQUIRED_THRESHOLD: float = 0.70  # Defines the required-review confidence threshold.
AUTO_ACCEPT_THRESHOLD: float = 0.85  # Defines the auto-accepted confidence threshold.


class CorrectionItem(BaseModel):  # Defines one reviewable correction-session item.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields for safer API validation.

    item_id: str  # Stores the correction-session item ID.
    raw_name: str  # Stores the original parsed item name.
    parsed_name: str  # Stores the parser-cleaned item name.
    normalized_name: str  # Stores the canonical normalized name or raw fallback.
    product_ref: str | None = None  # Stores the matched product ID when available.
    quantity: Decimal  # Stores the item quantity.
    quantity_unit: str  # Stores the item quantity unit.
    unit_price: Decimal | None = None  # Stores the item unit price when calculable.
    line_total: Decimal  # Stores the item line total.
    purchase_date: str | None = None  # Stores the parsed purchase date as text for Phase 1.
    parser_version: str  # Stores the parser version used.
    normalizer_version: str | None = None  # Stores the normalizer version used.
    confidence: float = Field(ge=0.0, le=1.0)  # Stores the combined confidence score.
    matched_rule_type: str | None = None  # Stores the normalizer match type.
    substituted: bool = False  # Stores whether the item was a substituted replacement.
    out_of_stock: bool = False  # Stores whether the item was an unavailable original item.
    user_corrected: bool = False  # Stores whether the owner edited this item.
    skipped: bool = False  # Stores whether the owner skipped this item.
    review_required: bool = False  # Stores whether the item requires review.
    review_suggested: bool = False  # Stores whether the item should be reviewed.
    auto_accepted: bool = False  # Stores whether the item can be auto-accepted but still edited.


class CorrectionSession(BaseModel):  # Defines a full correction session.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields for safer session state.

    session_id: str  # Stores the correction session ID.
    source_type: str  # Stores the input source type.
    store: str  # Stores the store label.
    raw_lines: list[str]  # Stores raw extracted or pasted text lines.
    items: list[CorrectionItem]  # Stores reviewable parsed and normalized items.
    parse_errors: list[str] = Field(default_factory=list)  # Stores parser warnings and errors.
    source_metadata: dict[str, Any] = Field(default_factory=dict)  # Stores filename, path, page count, and related metadata.
    created_at: datetime  # Stores when the session was created.
    expires_at: datetime  # Stores when the session expires.
    approved: bool = False  # Stores whether the session has been approved.


class PasteReceiptRequest(BaseModel):  # Defines the paste endpoint request body.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected request fields.

    text: str = Field(min_length=1)  # Stores pasted receipt text and requires at least one character.


class CorrectionItemUpdateRequest(BaseModel):  # Defines fields the owner may edit on one item.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected request fields.

    raw_name: str | None = None  # Allows the owner to update the raw name if needed.
    parsed_name: str | None = None  # Allows the owner to update the parsed name.
    normalized_name: str | None = None  # Allows the owner to update the canonical name.
    product_ref: str | None = None  # Allows the owner to update the product reference.
    quantity: Decimal | None = None  # Allows the owner to update quantity.
    quantity_unit: str | None = None  # Allows the owner to update quantity unit.
    unit_price: Decimal | None = None  # Allows the owner to update unit price.
    line_total: Decimal | None = None  # Allows the owner to update line total.
    skipped: bool | None = None  # Allows the owner to skip or unskip the item.


class NormalizeCorrectionRequest(BaseModel):  # Defines the request body for saving an alias correction.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected request fields.

    canonical_name: str = Field(min_length=1)  # Stores the canonical product name to update.
    alias: str = Field(min_length=1)  # Stores the alias to add to products.aliases[].


class PipelineSessionResponse(BaseModel):  # Defines the response returned after upload or paste.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected response fields.

    session_id: str  # Returns the created correction session ID.
    expires_at: datetime  # Returns the session expiration timestamp.


class CorrectionSessionResponse(BaseModel):  # Defines the response returned by session retrieval and item update.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected response fields.

    session: CorrectionSession  # Returns the correction session.


class NormalizeCorrectionResponse(BaseModel):  # Defines the response returned after saving an alias.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected response fields.

    session: CorrectionSession  # Returns the updated correction session.
    canonical_name: str  # Returns the canonical product name.
    alias: str  # Returns the saved alias.


class ApproveSessionResponse(BaseModel):  # Defines the response returned after approval and Stage 3 load.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected response fields.

    raw_input_id: str  # Returns the created raw_inputs ID.
    purchase_ids: list[str]  # Returns created purchase IDs.
    purchase_count: int  # Returns the number of created purchases.
    price_history_updates: int  # Returns the number of price history updates.
    loader_version: str  # Returns the loader version used.
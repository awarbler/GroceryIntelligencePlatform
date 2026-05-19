# =============================================================================
# File: backend/models/ad_correction.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Defines ad correction session models for parsed H-E-B weekly ad deals.
# Security Note: Models store public ad text only and must not store credentials.
# SRS Traceability: Supports SRS v5.0 Section 7 and Section 13.
# SDD Traceability: Supports SDD v5.0 Section 4, Section 7.5, and Section 8.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations.

from datetime import UTC  # Provides UTC timezone.
from datetime import date  # Represents ad validity dates.
from datetime import datetime  # Represents session timestamps.
from decimal import Decimal  # Represents money values exactly.
from uuid import uuid4  # Generates session and item IDs.

from pydantic import BaseModel  # Provides Pydantic validation.
from pydantic import Field  # Provides field validation helpers.

from backend.models.ad import DealType  # Imports shared deal type enum.


class PasteAdRequest(BaseModel):  # Defines request body for pasted ad text.
    text: str = Field(..., min_length=1)  # Stores pasted H-E-B weekly ad text.
    start_date: date | None = None  # Stores optional supplied ad start date.
    end_date: date | None = None  # Stores optional supplied ad end date.


class AdCorrectionItem(BaseModel):  # Defines one reviewable ad correction item.
    item_id: str = Field(default_factory=lambda: str(uuid4()))  # Stores stable correction item ID.
    raw_text: str  # Stores original parsed ad block.
    item_name: str  # Stores parsed item name.
    sale_price: Decimal  # Stores sale price.
    regular_price: Decimal | None = None  # Stores optional regular price.
    deal_type: DealType  # Stores classified deal type.
    size: str | None = None  # Stores optional size.
    skipped: bool = False  # Allows owner to skip bad parsed items.
    user_corrected: bool = False  # Marks whether owner edited item.


class AdCorrectionSession(BaseModel):  # Defines one ad correction session.
    session_id: str = Field(default_factory=lambda: str(uuid4()))  # Stores session ID.
    source_type: str  # Stores source type.
    store: str  # Stores store label.
    start_date: date  # Stores ad start date.
    end_date: date  # Stores ad end date.
    raw_lines: list[str]  # Stores raw source lines.
    items: list[AdCorrectionItem]  # Stores reviewable ad items.
    parse_errors: list[str] = Field(default_factory=list)  # Stores parser errors.
    source_metadata: dict = Field(default_factory=dict)  # Stores source metadata.
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))  # Stores creation time.
    expires_at: datetime | None = None  # Stores optional expiration time.


class AdPipelineSessionResponse(BaseModel):  # Defines upload/paste response.
    session_id: str  # Returns created session ID.
    expires_at: datetime | None = None  # Returns optional expiration time.


class AdCorrectionSessionResponse(BaseModel):  # Defines session response.
    session: AdCorrectionSession  # Returns correction session.


class ApproveAdSessionResponse(BaseModel):  # Defines ad approval response.
    ad_id: str  # Returns inserted ad ID.
    item_count: int  # Returns saved item count.
    parser_version: str  # Returns parser version.
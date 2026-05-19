# =============================================================================
# File: backend/services/ad_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Provides business logic for H-E-B weekly ad records.
# Security Note: Handles public ad data only and does not access secrets.
# SRS Traceability: Supports SRS v5.0 Section 7 AD-001 through AD-010.
# SDD Traceability: Supports SDD v5.0 Section 7.5 ads collection and Section 8 API design.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations.

from datetime import UTC  # Provides UTC timezone.
from datetime import date  # Supports valid-ad date filtering.
from datetime import datetime  # Provides current date fallback.
from typing import Any  # Supports MongoDB document dictionaries.

from pydantic import ValidationError  # Handles Pydantic validation failures.

from backend.data_access.ads import AdsDataAccess  # Imports ads Data Access Layer.
from backend.models.ad import AdModel  # Imports ad model validation.


async def list_current_ads(
    dal: AdsDataAccess,
    as_of_date: date | None = None,
    store_ref: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List ads valid on a date."""
    effective_date: date = as_of_date or datetime.now(UTC).date()  # Uses today if no date supplied.
    return await dal.list_valid_ads(effective_date, store_ref, skip, limit)  # Reads valid ads through DAL.


async def create_ad(dal: AdsDataAccess, payload: dict[str, Any]) -> str:
    """Validate and save one ad document."""
    try:  # Starts validation block.
        ad_model: AdModel = AdModel.model_validate(payload)  # Validates against AdModel.
    except ValidationError as exc:  # Handles validation failure.
        raise ValueError(str(exc)) from exc  # Converts to service-level error.

    ad_doc: dict[str, Any] = ad_model.model_dump(by_alias=True, exclude_none=True)  # Converts model to dictionary.
    ad_doc["start_date"] = ad_model.start_date.isoformat()  # Stores start date as ISO string.
    ad_doc["end_date"] = ad_model.end_date.isoformat()  # Stores end date as ISO string.
    return await dal.create_ad(ad_doc)  # Saves through DAL only.

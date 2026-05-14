# =============================================================================
# File: rebate.py
# Project: Grocery Intelligence Platform
# Created Date: 2024-06-01
# Author: Anita Woodford
# Description: Models for rebates in the Grocery Intelligence Platform.
# security note: 
# SRS Traceability Supports SRS 
# SDD Traceability Supports SDD 
# =============================================================================

from __future__ import annotations
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Optional
from pydantic import ConfigDict, Field, model_validator
from backend.models.base import BaseDocument

# define the approved rebate lifecycle status
class RebateStatus(StrEnum):
    """Enum representing the lifecycle status of a rebate."""
    PENDING = "PENDING" # rebate is pending and has not been processed yet
    SUBMITTED = "SUBMITTED" # rebate has been submitted to the store/manufacturer but not yet approved
    RECEIVED = "RECEIVED" # rebate has been received by the user but not yet processed for rewards
    DENIED = "DENIED" # rebate has been denied by the store/manufacturer
    

# define a validated rebate document for mongodb storage
class RebateModel(BaseDocument):
    """Pydantic model representing a rebate document stored in MongoDB."""
    # # Rejects unknown fields and validates defaults.
    model_config = ConfigDict(extra="forbid", from_attributes=True, validate_default=True) 
    # store the rebate company name 
    company: str = Field(...,min_length=2)
                         
    # store the item name connected to the rebate
    item_name: str = Field(...,min_length=2)
    # store the product branch when know 
    brand: Optional[str] = Field(None, min_length=2)
    # store the required produce size or quantity for the rebate when known
    size_or_quantity: Optional[str] = Field(None, min_length=1)
    # store dollar rebate amount cash back amount for the rebate when known
    rebate_amount: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Stores the cash-back rebate amount as a money-safe Decimal.
    points_amount: Optional[int] = Field(default=None, ge=0)  # Stores points amount when the rebate is points-based, such as Fetch.
    # TODO: convert points to cash 
    dollar_equivalent: Decimal = Field(..., ge=Decimal("0.00"))  # Stores the estimated or known dollar value of the rebate.
    min_qty: int = Field(default=1, ge=1)  # Stores the minimum quantity required to qualify for the rebate.
    stores_valid: list[str] = Field(default_factory=list)  # Stores stores where the rebate is valid.
    description: Optional[str] = Field(default=None)  # Stores a readable rebate description.
    expiration_date: date = Field(...)  # Stores the required rebate expiration date.
    status: RebateStatus = Field(default=RebateStatus.PENDING)  # Stores the rebate lifecycle status.
    denial_reason: Optional[str] = Field(default=None)  # Stores the denial reason when the rebate is denied.
    raw_text: Optional[str] = Field(default=None)  # Stores original rebate text copied from the app or source.
    is_fetch_2x: bool = Field(default=False)  # Tracks whether the Fetch offer is a 2x points promotion.
    source_type: Optional[str] = Field(default=None)  # Stores where the rebate data came from, such as app, PDF, or manual entry.
    must_unlock_before_purchase: bool = Field(default=False)  # Tracks whether the rebate must be unlocked before buying.
    unlocked_before_purchase: bool = Field(default=False)  # Tracks whether the rebate was actually unlocked before purchase.
    receipt_submitted: bool = Field(default=False)  # Tracks whether the receipt was submitted after purchase.
    barcode_scan_required: bool = Field(default=False)  # Tracks whether the rebate app may require barcode scanning.
    submitted_date: Optional[date] = Field(default=None)  # Stores the date the rebate was submitted.
    received_date: Optional[date] = Field(default=None)  # Stores the date the rebate was received.

    @model_validator(mode="after")  # Runs validation after all fields are loaded.
    def validate_fetch_points_equivalent(self) -> RebateModel:  # Validates Fetch-style point conversion when points are provided.
        if self.points_amount is not None:  # Checks whether the rebate uses points.
            expected_dollar_equivalent = Decimal(self.points_amount) / Decimal("1000")  # Converts points to dollars using 1000 points per dollar.
            if self.dollar_equivalent != expected_dollar_equivalent:  # Compares the provided dollar value to the expected value.
                raise ValueError("dollar_equivalent must equal points_amount / 1000 when points_amount is provided")  # Raises an error for mismatched point conversion.
        return self  # Returns the validated model instance.

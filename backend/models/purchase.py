# =============================================================================
# File: purchase.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines purchase models for tracking store purchase facts before report calculations.
# Security Note: This model stores purchase metadata only and must not store payment credentials.
# SRS Traceability: Supports SRS v5.0 purchase history, coupon tracking, reward tracking, and report input requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and data access layer purchase documents.
# =============================================================================

from __future__ import annotations  # Enables forward-compatible type annotations.

from datetime import date  # Imports the date type used for purchase dates.
from decimal import Decimal  # Imports Decimal for exact money values.
from enum import StrEnum  # Imports StrEnum so enum values behave like strings.
from typing import Optional  # Imports Optional for fields that are not required in Phase 1.

from pydantic import ConfigDict  # Imports ConfigDict to control Pydantic model behavior.
from pydantic import Field  # Imports Field to define defaults and validation constraints.

from backend.models.base import BaseDocument  # Imports the shared Mongo-style base document model.
from backend.models.base import PyObjectId  # Imports the shared Mongo ObjectId-compatible type.
from backend.models.rebate import RebateStatus  # Imports the existing rebate lifecycle enum.


class InputType(StrEnum):  # Defines the allowed sources for purchase input records.
    """Allowed source types for purchase records."""  # Documents the purpose of the enum.

    ONLINE_RECEIPT = "ONLINE_RECEIPT"  # Represents a purchase parsed from an online receipt.
    EMAIL_RECEIPT = "EMAIL_RECEIPT"  # Represents a purchase parsed from an email receipt.
    PDF = "PDF"  # Represents a purchase parsed from a PDF file.
    PHOTO = "PHOTO"  # Represents a purchase parsed from a receipt photo.
    CSV_IMPORT = "CSV_IMPORT"  # Represents a purchase imported from a CSV file.
    MANUAL_ENTRY = "MANUAL_ENTRY"  # Represents a purchase entered manually by the user.
    COPY_PASTE = "COPY_PASTE"  # Represents a purchase created from pasted receipt text.


class CouponSource(StrEnum):  # Defines the allowed coupon-source values.
    """Allowed coupon sources for purchase records."""  # Documents the purpose of the enum.

    WALGREENS_DIGITAL = "WALGREENS_DIGITAL"  # Represents a Walgreens digital coupon.
    CVS_DIGITAL = "CVS_DIGITAL"  # Represents a CVS digital coupon.
    HEB_DIGITAL = "HEB_DIGITAL"  # Represents an H-E-B digital coupon.
    WALMART_DIGITAL = "WALMART_DIGITAL"  # Represents a Walmart digital coupon.
    MANUFACTURER = "MANUFACTURER"  # Represents a manufacturer coupon.
    PAPER = "PAPER"  # Represents a paper coupon.


class RewardUsed(BaseDocument):  # Defines a reusable reward-used value object.
    """Tracks whether a store reward was used and how much value was applied."""  # Explains the model purpose.

    model_config = ConfigDict(extra="forbid")  # Rejects undefined fields during validation.

    used: bool = Field(default=False)  # Stores whether this reward type was used.
    amount: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))  # Stores the reward amount used.


class PurchaseModel(BaseDocument):  # Defines the purchase document stored by the backend.
    """Stores purchase facts before later report-level calculations."""  # Explains the model purpose.

    model_config = ConfigDict(extra="forbid")  # Rejects undefined fields such as final_cost_after_rebates.

    product_ref: Optional[PyObjectId] = Field(default=None)  # Optionally links this purchase to a product document.
    store_ref: PyObjectId = Field(...)  # Links this purchase to the store where it happened.
    canonical_name: str = Field(..., min_length=1)  # Stores the normalized product name.
    raw_name: Optional[str] = Field(default=None)  # Stores the original receipt text when available.
    category: str = Field(..., min_length=1)  # Stores the product category.
    brand: Optional[str] = Field(default=None)  # Stores the product brand when available.
    size: Optional[str] = Field(default=None)  # Stores the product size when available.
    quantity: int = Field(default=1, ge=1)  # Stores the purchased quantity.
    purchase_date: date = Field(...)  # Stores the date the purchase occurred.

    shelf_price: Decimal = Field(..., ge=Decimal("0.00"))  # Stores the regular shelf price before sales.
    sale_price: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Stores the sale price when available.
    register_price: Decimal = Field(..., ge=Decimal("0.00"))  # Stores the register item total before register coupons.
    subtotal_before_coupons: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Stores basket subtotal before coupons.
    out_of_pocket: Decimal = Field(..., ge=Decimal("0.00"))  # Stores actual register cost after register coupons.

    coupon_used: bool = Field(default=False)  # Stores whether a coupon was used.
    coupon_source: Optional[CouponSource] = Field(default=None)  # Stores the coupon source when a coupon was used.
    coupon_amount: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))  # Stores the coupon amount applied.

    register_rewards_used: RewardUsed = Field(default_factory=RewardUsed)  # Stores Walgreens Register Reward usage.
    cvs_ecb_used: RewardUsed = Field(default_factory=RewardUsed)  # Stores CVS ExtraBucks usage.

    rebate_company: Optional[str] = Field(default=None)  # Stores the rebate company name when available.
    rebate_amount: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))  # Stores expected or recorded rebate value.
    rebate_status: Optional[RebateStatus] = Field(default=None)  # Stores rebate lifecycle status when available.

    source_type: InputType = Field(...)  # Stores how the purchase record entered the system.
    raw_input_ref: Optional[PyObjectId] = Field(default=None)  # Optionally links to the raw receipt input document.
    parse_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)  # Stores parser confidence when available.
    user_corrected: bool = Field(default=False)  # Stores whether the user corrected the parsed data.
    notes: str = Field(default="")  # Stores user or system notes.

    walgreens_cash_redeemed: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores Walgreens Cash redeemed.
    walgreens_cash_earned: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores Walgreens Cash earned.
    walgreens_cash_earned_by_item_ref: Optional[PyObjectId] = Field(default=None)  # Optionally links Walgreens Cash earned to an item.
    rr_used_amount: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores Register Rewards used amount.
    rr_earned_amount: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores Register Rewards earned amount.
    rr_earned_by_item_ref: Optional[PyObjectId] = Field(default=None)  # Optionally links Register Rewards earned to an item.
    walmart_cash_earned: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores Walmart Cash earned.
    walmart_cash_earned_by_item_ref: Optional[PyObjectId] = Field(default=None)  # Optionally links Walmart Cash earned to an item.
    walmart_cash_used: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores Walmart Cash used.
    ecb_earned: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores CVS ExtraBucks earned.
    ecb_earned_by_item_ref: Optional[PyObjectId] = Field(default=None)  # Optionally links CVS ExtraBucks earned to an item.
    ecb_used: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Optionally stores CVS ExtraBucks used.
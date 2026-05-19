# =============================================================================
# File: backend/models/reward_offer.py
# Project: Grocery Intelligence Platform
# Purpose: Defines provider-neutral reward offer models for external rewards.
# SRS Traceability: SRS Section 16, SRS Section 17 SB-004, SRS Section 20 TS-005, SRS Section 23
# SDD Traceability: SDD Section 7, SDD Section 9, SDD Section 15
# =============================================================================

from datetime import date, datetime, timezone  # Imports date and datetime types for offer validity fields.
from decimal import Decimal  # Imports Decimal for money-safe reward values.
from enum import Enum  # Imports Enum for controlled provider and reward type values.

from pydantic import BaseModel, ConfigDict, Field  # Imports Pydantic tools for validation.

from backend.models.base import BaseDocument, PyObjectId  # Imports shared Mongo document base and ObjectId type.


class RewardProvider(str, Enum):  # Defines supported external reward providers.
    IBOTTA = "ibotta"  # Represents Ibotta cash-back offers.
    FETCH = "fetch"  # Represents Fetch points, bundles, and spend offers.
    SWAGBUCKS = "swagbucks"  # Represents Swagbucks SB receipt offers.
    CHECKOUT_51 = "checkout_51"  # Represents Checkout 51 receipt-upload offers.
    AISLE = "aisle"  # Represents Aisle claim/reimbursement offers.
    SHOPKICK = "shopkick"  # Represents Shopkick kicks rewards.
    OTHER = "other"  # Represents unsupported or manually entered providers.


class RewardType(str, Enum):  # Defines supported reward behavior types.
    CASH_BACK = "cash_back"  # Represents direct cash-back offers.
    POINTS_BACK = "points_back"  # Represents provider points rewards.
    FREE_ITEM = "free_item"  # Represents free-item rewards.
    BOGO = "bogo"  # Represents buy-one-get-one rewards.
    BUY_X_GET_Y = "buy_x_get_y"  # Represents buy-X-get-Y rewards.
    SPEND_THRESHOLD = "spend_threshold"  # Represents spend-threshold rewards.
    BUNDLE = "bundle"  # Represents bundle-based rewards.
    CLAIM_REIMBURSEMENT = "claim_reimbursement"  # Represents claim-based reimbursement offers.
    PUNCHCARD = "punchcard"  # Represents progressive punchcard rewards.
    OTHER = "other"  # Represents provider-specific reward types not yet modeled.


class RewardCurrencyType(str, Enum):  # Defines the original provider reward value unit.
    USD = "usd"  # Represents dollars.
    POINTS = "points"  # Represents generic points.
    SB = "sb"  # Represents Swagbucks SB points.
    KICKS = "kicks"  # Represents Shopkick kicks.
    FREE_ITEM = "free_item"  # Represents free item value.
    PERCENT_OFF = "percent_off"  # Represents percent-off rewards.
    OTHER = "other"  # Represents unsupported reward units.


class RewardSourceType(str, Enum):  # Defines how the reward offer was captured.
    MANUAL_ENTRY = "manual_entry"  # Represents manually entered reward data.
    SCREENSHOT = "screenshot"  # Represents screenshot-captured reward data.
    PDF_EXPORT = "pdf_export"  # Represents exported PDF reward data.
    APP_CAPTURE = "app_capture"  # Represents app-captured reward data.
    WEBSITE_CAPTURE = "website_capture"  # Represents website-captured reward data.
    OTHER = "other"  # Represents any other capture method.


class BundleRequirement(BaseModel):  # Defines one item or category requirement inside a bundle offer.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields to keep bundle data clean.

    name: str = Field(..., min_length=1)  # Stores the required product or category name.
    quantity: int = Field(default=1, ge=1)  # Stores how many units are required.


class RewardOfferModel(BaseDocument):  # Defines the MongoDB document model for reward offers.
    model_config = ConfigDict(extra="forbid", populate_by_name=True)  # Rejects extras and supports alias population.

    reward_provider: RewardProvider  # Stores the provider such as Ibotta, Fetch, or Aisle.
    reward_type: RewardType  # Stores the reward structure such as cash back or bundle.
    reward_currency_type: RewardCurrencyType  # Stores the original provider currency type.
    reward_value: Decimal = Field(..., ge=Decimal("0"))  # Stores the original provider value.
    estimated_cash_value: Decimal = Field(..., ge=Decimal("0"))  # Stores report-ready estimated cash value.

    retailer: str | None = Field(default=None)  # Stores the retailer name when provider offer is store-specific.
    store_ref: PyObjectId | None = Field(default=None)  # Stores optional MongoDB store reference.
    offer_title: str | None = Field(default=None)  # Stores user-facing offer title.
    product_name: str | None = Field(default=None)  # Stores the main product name if available.
    brand: str | None = Field(default=None)  # Stores brand name if available.
    category: str | None = Field(default=None)  # Stores broad product category if available.

    qualifying_products: list[str] = Field(default_factory=list)  # Stores eligible product names.
    qualifying_categories: list[str] = Field(default_factory=list)  # Stores eligible categories.
    bundle_requirements: list[BundleRequirement] = Field(default_factory=list)  # Stores bundle item requirements.

    spend_requirement: Decimal | None = Field(default=None, ge=Decimal("0"))  # Stores spend threshold if required.
    quantity_requirement: int | None = Field(default=None, ge=1)  # Stores minimum quantity if required.
    limit: int | None = Field(default=None, ge=1)  # Stores redemption limit if known.

    expiration_date: date | None = Field(default=None)  # Stores offer expiration date if known.
    valid_from: date | None = Field(default=None)  # Stores offer start date if known.

    claim_required: bool = Field(default=False)  # Tracks whether a claim workflow is required.
    phone_number_required: bool = Field(default=False)  # Tracks whether phone submission is required.
    receipt_submission_required: bool = Field(default=False)  # Tracks whether receipt upload is required.
    progressive_unlock_required: bool = Field(default=False)  # Tracks whether offer unlocks progressively.
    punchcard_program: bool = Field(default=False)  # Tracks punchcard-style reward programs.
    free_item_quantity: int | None = Field(default=None, ge=1)  # Stores free item quantity if applicable.
    remaining_redemptions: int | None = Field(default=None, ge=0)  # Stores remaining uses if provider exposes it.

    offer_details_text: str | None = Field(default=None)  # Stores raw offer terms for audit and display.
    source_type: RewardSourceType  # Stores how this offer was captured.
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Stores capture timestamp.
    is_active: bool = Field(default=True)  # Stores whether offer is active for matching.
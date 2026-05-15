# =============================================================================
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines ad models for store sale ads, coupons, basket deals,
# and reward promotions.
# Security Note: This model stores ad and coupon metadata only and must not store
# secrets or user credentials.
# SRS Traceability: Supports SRS v5.0 store ad ingestion, deal tracking, and
# coupon intelligence requirements.
# SDD Traceability: Supports SDD v5.0 backend model layer and grocery
# deal data modeling.
# =============================================================================

from __future__ import annotations  # Allows forward references in type hints.

from datetime import date  # Imports date for ad start and end dates.
from decimal import Decimal  # Imports Decimal for accurate money and percentage values.
from enum import Enum  # Imports Enum for locked deal type values.
from typing import (
    Optional,
)  # Imports Optional for fields that are allowed to be missing.

from pydantic import Field  # Imports Field for validation rules and default values.
from pydantic import (
    model_validator,
)  # Imports model_validator for cross-field validation.

from backend.models.base import BaseDocument  # Imports the shared base document model.
from backend.models.base import PyObjectId  # Imports the shared MongoDB ObjectId type.


class DealType(
    str, Enum
):  # Defines the approved deal categories for ads, coupons, and promotions.
    """Approved deal classifications for store ads, coupons, and in-store promotions."""  # Documents the enum purpose.

    STANDARD = "STANDARD"  # Represents a normal sale price without additional coupon or reward conditions.
    BOGO = (
        "BOGO"  # Represents buy-one-get-one free or buy-one-get-one discounted deals.
    )
    BUY_X_GET_Y = (
        "BUY_X_GET_Y"  # Represents buy X items and get Y items free or discounted.
    )
    THRESHOLD = (
        "THRESHOLD"  # Represents spend-threshold deals such as spend $X and get $Y off.
    )
    REGISTER_REWARD = "REGISTER_REWARD"  # Represents Walgreens Register Reward deals, not H-E-B deals.
    ECB = "ECB"  # Represents CVS ExtraBucks deals, not H-E-B deals.
    SPEND_BOOSTER = (
        "SPEND_BOOSTER"  # Represents spend $X and get $Y back in store rewards.
    )
    MANUFACTURER_COUPON = (
        "MANUFACTURER_COUPON"  # Represents a manufacturer coupon accepted at checkout.
    )
    DIGITAL_COUPON = "DIGITAL_COUPON"  # Represents a digital coupon selected in a store website or app.
    COMBO_LOCO = (
        "COMBO_LOCO"  # Represents an H-E-B Combo Loco style paired-item promotion.
    )
    BASKET_COUPON = "BASKET_COUPON"  # Represents a coupon applied to the basket total.
    PERCENT_OFF = "PERCENT_OFF"  # Represents a percentage-off promotion.
    PRICE_OFF = "PRICE_OFF"  # Represents a fixed amount off a product or basket.
    FREE_ITEM = "FREE_ITEM"  # Represents a free-item promotion.


class AdItem(
    BaseDocument
):  # Defines one advertised product, coupon, or promotion line.
    """Represents a single advertised product, coupon, or promotion line."""  # Documents the model purpose.

    item_name: str = Field(
        ..., min_length=1
    )  # Stores the advertised item or promotion name.
    brand: Optional[str] = None  # Stores the optional product brand.
    size: Optional[str] = (
        None  # Stores the optional product size or package description.
    )
    sale_price: Decimal = Field(
        ..., ge=Decimal("0")
    )  # Stores the sale price and prevents negative values.
    regular_price: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores the optional regular price and prevents negative values.
    deal_type: DealType = Field(
        ...
    )  # Stores the required approved deal classification.
    buy_qty: int = Field(
        default=1, ge=1
    )  # Stores the required purchase quantity and defaults to one.
    get_qty: Optional[int] = Field(
        default=None, ge=1
    )  # Stores the quantity received free or discounted when applicable.
    free_item_name: Optional[str] = (
        None  # Stores the free item name for Combo Loco, BOGO, Buy X Get Y, or free-item deals.
    )
    store_coupon_amount: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores an optional store-issued coupon dollar amount.
    store_coupon_desc: Optional[str] = None  # Stores optional store coupon wording.
    mfr_coupon_amount: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores an optional manufacturer coupon dollar amount.
    mfr_coupon_desc: Optional[str] = (
        None  # Stores optional manufacturer coupon wording.
    )
    digital_coupon_amount: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores an optional digital coupon dollar amount.
    digital_coupon_desc: Optional[str] = None  # Stores optional digital coupon wording.
    price_off_amount: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores a fixed amount off when the deal is PRICE_OFF.
    percent_off: Optional[Decimal] = Field(
        default=None, ge=Decimal("0"), le=Decimal("100")
    )  # Stores a percent-off value from 0 through 100.
    register_reward: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores an optional Walgreens-style Register Reward value.
    register_reward_desc: Optional[str] = (
        None  # Stores optional Register Reward wording.
    )
    basket_threshold: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores the required basket spend threshold when applicable.
    basket_discount: Optional[Decimal] = Field(
        default=None, ge=Decimal("0")
    )  # Stores the basket-level discount amount when applicable.
    raw_text: Optional[str] = (
        None  # Preserves the original ad wording for traceability and later parser review.
    )


class AdModel(BaseDocument):  # Defines a complete store ad document.
    """Represents a store ad with a date range, source, and typed ad items."""  # Documents the model purpose.

    store_ref: PyObjectId = Field(
        ...
    )  # Stores the MongoDB reference to the store document.
    start_date: date = Field(...)  # Stores the first valid date of the ad.
    end_date: date = Field(...)  # Stores the last valid date of the ad.
    source_type: str = Field(
        ..., min_length=1
    )  # Stores the ad source type such as PDF, app, website, email, or manual.
    raw_input_ref: Optional[PyObjectId] = (
        None  # Stores an optional reference to the raw imported source document.
    )
    items: list[AdItem] = Field(
        default_factory=list
    )  # Stores typed ad items using a fresh list for each ad document.

    @model_validator(
        mode="after"
    )  # Runs this validation after the model fields are parsed.
    def validate_date_range(
        self,
    ) -> "AdModel":  # Defines cross-field validation for start and end dates.
        """Validate that the ad end date is not before the ad start date."""  # Documents the validator purpose.
        if (
            self.end_date < self.start_date
        ):  # Checks whether the end date is earlier than the start date.
            raise ValueError(
                "end_date must be greater than or equal to start_date"
            )  # Raises a clear date range error.
        return self  # Returns the validated model instance.

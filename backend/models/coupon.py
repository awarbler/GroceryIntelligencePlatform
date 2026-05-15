# =============================================================================
# File: coupon.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines coupon enums and the CouponModel for store, manufacturer, paper, app-only, basket, item, combo, and rebate coupon records.
# Security Note: This model stores coupon metadata only and should not store payment data, account credentials, or personal customer information.
# SRS Traceability: Supports SRS v5.0 P1-04 coupon validation, coupon expiration tracking, coupon source classification, and H-E-B coupon workflow requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and coupon data modeling for the Grocery Intelligence Platform.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern Python type-hint behavior and forward references.

from datetime import (
    date,
)  # Imports the date type for coupon availability and expiration dates.
from decimal import (
    Decimal,
)  # Imports Decimal for money and percent fields to avoid floating-point rounding errors.
from enum import (
    StrEnum,
)  # Imports StrEnum so enum values behave like strings in JSON and MongoDB-friendly output.
from typing import (
    Optional,
)  # Imports Optional for fields that may be absent or unknown.

from pydantic import (
    Field,
    model_validator,
)  # Imports Field for field rules and model_validator for cross-field validation.

from backend.models.base import (
    BaseDocument,
    PyObjectId,
)  # Imports the shared base document and MongoDB ObjectId type.


class CouponType(StrEnum):  # Defines the approved coupon source/type values.
    """Enum representing the source or type of coupon."""  # Documents the purpose of this enum.

    STORE_DIGITAL = "STORE_DIGITAL"  # Represents a store-issued digital coupon.
    MANUFACTURER = "MANUFACTURER"  # Represents a manufacturer-issued coupon.
    PAPER = "PAPER"  # Represents a paper coupon.
    MYW_EXCLUSIVE = "MYW_EXCLUSIVE"  # Represents a My H-E-B or MyWay exclusive coupon.
    APP_ONLY = "APP_ONLY"  # Represents a coupon available only through an app workflow.


class CouponScope(StrEnum):  # Defines where the coupon applies.
    """Enum representing the redemption scope of a coupon."""  # Documents the purpose of this enum.

    ITEM = "ITEM"  # Applies to one qualifying item.
    BASKET = "BASKET"  # Applies to the basket or order total.
    COMBO = "COMBO"  # Applies to a combination offer such as buy X get Y.
    REBATE = "REBATE"  # Applies through a rebate workflow instead of direct checkout discount.


class CouponModel(BaseDocument):  # Defines the MongoDB-ready coupon document model.
    """Model representing a coupon, coupon workflow requirement, or rebate-style coupon offer."""  # Documents the purpose of the model.

    store_ref: PyObjectId = Field(
        ...,
        description="MongoDB ObjectId reference for the store that owns or provides the coupon.",
    )  # Requires the store reference.
    coupon_type: CouponType = Field(
        ...,
        description="Coupon source type such as STORE_DIGITAL, MANUFACTURER, PAPER, MYW_EXCLUSIVE, or APP_ONLY.",
    )  # Requires the coupon type.
    coupon_scope: CouponScope = Field(
        ...,
        description="Coupon redemption scope such as ITEM, BASKET, COMBO, or REBATE.",
    )  # Requires the coupon scope.
    is_store_coupon: bool = Field(
        ..., description="True when the coupon is issued by the store."
    )  # Requires the store coupon flag.
    store_name: Optional[str] = Field(
        default=None, description="Optional display name for the store."
    )  # Stores the optional store name.
    is_manufacturer_coupon: bool = Field(
        ..., description="True when the coupon is issued by the manufacturer."
    )  # Requires the manufacturer coupon flag.
    coupon_date: Optional[date] = Field(
        default=None, description="Optional date when the coupon became available."
    )  # Stores the optional coupon availability date.
    expiration_date: date = Field(
        ..., description="Required date when the coupon expires."
    )  # Requires the expiration date for P1-04 compliance.
    item_name: str = Field(
        ...,
        min_length=1,
        description="Name of the eligible coupon item or basket offer.",
    )  # Requires the eligible item or offer name.
    item_size: Optional[str] = Field(
        default=None, description="Optional eligible item size."
    )  # Stores the optional item size.
    brand: Optional[str] = Field(
        default=None, description="Optional eligible brand name."
    )  # Stores the optional brand.
    discount_amount: Decimal = Field(
        ..., ge=Decimal("0"), description="Dollar discount amount for the coupon."
    )  # Requires a non-negative dollar discount amount.
    discount_percent: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
        description="Optional percentage discount from 0 to 100.",
    )  # Stores the optional percent discount.
    discount_type: str = Field(
        ..., min_length=1, description='Discount type such as "dollars" or "percent".'
    )  # Requires the discount type label.
    required_purchase_quantity: int = Field(
        default=1, ge=1, description="Quantity required to redeem the coupon."
    )  # Defaults required quantity to one.
    required_purchase_amount: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0"),
        description="Optional basket threshold amount required for redemption.",
    )  # Stores the optional basket threshold.
    store_purchased: Optional[str] = Field(
        default=None,
        description="Optional store where the coupon was redeemed or planned for use.",
    )  # Stores the optional redemption store.
    description: Optional[str] = Field(
        default=None, description="Optional human-readable coupon description."
    )  # Stores the optional coupon description.
    via_rebate_flag: bool = Field(
        default=False,
        description="True when the coupon value is received through a rebate workflow.",
    )  # Tracks rebate-style coupon behavior.
    myw_exclusive: bool = Field(
        default=False,
        description="True when the coupon is a My H-E-B or MyWay exclusive offer.",
    )  # Tracks MyWay exclusive behavior.
    online_only: bool = Field(
        default=False, description="True when the coupon is limited to online use."
    )  # Tracks online-only coupon restrictions.
    on_card: bool = Field(
        default=False,
        description="True when the coupon has been clipped or sent to the user account/card.",
    )  # Tracks whether the coupon is on the card.
    send_to_card: bool = Field(
        default=False,
        description="True when the coupon supports a send-to-card workflow.",
    )  # Tracks whether the coupon can be sent to card.
    is_unlimited: bool = Field(
        default=False,
        description="True when the coupon can be used repeatedly according to the offer terms.",
    )  # Tracks unlimited coupon support.
    must_clip_before_checkout: bool = Field(
        default=True,
        description="True when the coupon must be clipped before checkout.",
    )  # Defaults to clip-first behavior.
    must_scan_barcode_to_verify: bool = Field(
        default=True,
        description="True when barcode scanning is required to verify the coupon.",
    )  # Defaults to barcode verification behavior.
    verified_attaches_before_purchase: bool = Field(
        default=False,
        description="True when the user verified the coupon attaches before purchase.",
    )  # Tracks user verification before purchase.
    raw_text: Optional[str] = Field(
        default=None,
        description="Optional original coupon text copied from an app, receipt, PDF, ad, or manual entry.",
    )  # Stores source text for traceability.
    source_type: Optional[str] = Field(
        default=None,
        description="Optional source label such as app, PDF, receipt, ad, or manual.",
    )  # Stores the source type.

    @model_validator(
        mode="after"
    )  # Runs validation after Pydantic has parsed all coupon fields.
    def validate_coupon_business_rules(
        self,
    ) -> "CouponModel":  # Defines cross-field validation rules for coupon data.
        """Validate coupon rules that depend on more than one field."""  # Explains that this validator checks relationships between fields.

        if (
            self.coupon_date is not None and self.expiration_date < self.coupon_date
        ):  # Checks whether the coupon expires before it becomes available.
            raise ValueError(
                "expiration_date must be on or after coupon_date."
            )  # Rejects coupons with invalid date order.

        if self.discount_type not in {
            "dollars",
            "percent",
        }:  # Checks whether the discount type is one of the allowed values.
            raise ValueError(
                'discount_type must be either "dollars" or "percent".'
            )  # Rejects unsupported discount type values.

        if self.discount_type == "dollars" and self.discount_amount <= Decimal(
            "0"
        ):  # Checks that dollar coupons have a positive dollar amount.
            raise ValueError(
                "discount_amount must be greater than 0 when discount_type is dollars."
            )  # Rejects zero-dollar dollar coupons.

        if (
            self.discount_type == "dollars" and self.discount_percent is not None
        ):  # Checks that dollar coupons do not also carry a percent value.
            raise ValueError(
                "discount_percent must be None when discount_type is dollars."
            )  # Rejects mixed dollar and percent coupon data.

        if (
            self.discount_type == "percent" and self.discount_percent is None
        ):  # Checks that percent coupons include a percent value.
            raise ValueError(
                "discount_percent is required when discount_type is percent."
            )  # Rejects percent coupons without a percent value.

        if (
            self.discount_type == "percent"
            and self.discount_percent is not None
            and self.discount_percent <= Decimal("0")
        ):  # Checks that percent coupons have a positive percent value.
            raise ValueError(
                "discount_percent must be greater than 0 when discount_type is percent."
            )  # Rejects zero-percent percent coupons.

        if self.discount_type == "percent" and self.discount_amount != Decimal(
            "0"
        ):  # Checks that percent coupons do not also carry a dollar discount amount.
            raise ValueError(
                "discount_amount must be 0 when discount_type is percent."
            )  # Rejects mixed percent and dollar coupon data.

        if (
            self.coupon_scope == CouponScope.BASKET
            and self.required_purchase_amount is None
        ):  # Checks that basket coupons include a basket spending threshold.
            raise ValueError(
                "required_purchase_amount is required when coupon_scope is BASKET."
            )  # Rejects basket coupons without a required purchase amount.

        if (
            self.required_purchase_amount is not None
            and self.required_purchase_amount <= Decimal("0")
        ):  # Checks that any provided purchase amount is positive.
            raise ValueError(
                "required_purchase_amount must be greater than 0 when provided."
            )  # Rejects invalid purchase threshold values.

        if (
            self.coupon_type == CouponType.MANUFACTURER
            and self.is_manufacturer_coupon is not True
        ):  # Checks that manufacturer coupon type matches the manufacturer flag.
            raise ValueError(
                "is_manufacturer_coupon must be True when coupon_type is MANUFACTURER."
            )  # Rejects inconsistent manufacturer coupon data.

        if (
            self.coupon_type == CouponType.MANUFACTURER
            and self.is_store_coupon is not False
        ):  # Checks that manufacturer coupons are not also marked as store coupons.
            raise ValueError(
                "is_store_coupon must be False when coupon_type is MANUFACTURER."
            )  # Rejects conflicting coupon source flags.

        if (
            self.coupon_type
            in {CouponType.STORE_DIGITAL, CouponType.MYW_EXCLUSIVE, CouponType.APP_ONLY}
            and self.is_store_coupon is not True
        ):  # Checks that store and app coupon types are marked as store coupons.
            raise ValueError(
                "is_store_coupon must be True for store-issued coupon types."
            )  # Rejects inconsistent store coupon data.

        if (
            self.coupon_type
            in {CouponType.STORE_DIGITAL, CouponType.MYW_EXCLUSIVE, CouponType.APP_ONLY}
            and self.is_manufacturer_coupon is not False
        ):  # Checks that store and app coupon types are not marked as manufacturer coupons.
            raise ValueError(
                "is_manufacturer_coupon must be False for store-issued coupon types."
            )  # Rejects conflicting manufacturer flag data.

        if (
            self.coupon_type == CouponType.MYW_EXCLUSIVE
            and self.myw_exclusive is not True
        ):  # Checks that MyWay exclusive coupon type matches the MyWay flag.
            raise ValueError(
                "myw_exclusive must be True when coupon_type is MYW_EXCLUSIVE."
            )  # Rejects inconsistent MyWay exclusive data.

        if (
            self.coupon_type == CouponType.APP_ONLY and self.online_only is not True
        ):  # Checks that app-only coupon type matches online/app workflow restriction.
            raise ValueError(
                "online_only must be True when coupon_type is APP_ONLY."
            )  # Rejects inconsistent app-only coupon data.

        if (
            self.coupon_type == CouponType.PAPER
            and self.must_scan_barcode_to_verify is not True
        ):  # Checks that paper coupons require barcode verification.
            raise ValueError(
                "must_scan_barcode_to_verify must be True when coupon_type is PAPER."
            )  # Rejects paper coupons without barcode verification.

        if (
            self.coupon_scope == CouponScope.REBATE and self.via_rebate_flag is not True
        ):  # Checks that rebate-scope coupons are marked as rebate workflow coupons.
            raise ValueError(
                "via_rebate_flag must be True when coupon_scope is REBATE."
            )  # Rejects inconsistent rebate coupon data.

        if (
            self.verified_attaches_before_purchase is True and self.on_card is not True
        ):  # Checks that verified digital attachment implies the coupon is on card.
            raise ValueError(
                "on_card must be True when verified_attaches_before_purchase is True."
            )  # Rejects impossible verified attachment state.

        if (
            self.send_to_card is True and self.on_card is not True
        ):  # Checks that sent-to-card state means the coupon is also on card.
            raise ValueError(
                "on_card must be True when send_to_card is True."
            )  # Rejects impossible send-to-card state.

        return self  # Returns the validated coupon model.

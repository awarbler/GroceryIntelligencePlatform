# =============================================================================
# File: deal.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines deal match models for generated weekly grocery deal reports.
# Security Note: This model stores deal calculation references and financial fields only.
# SRS Traceability: Supports SRS v5.0 deal matching, coupon matching, rebate matching, and report generation requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and generated deal report design.
# =============================================================================

from __future__ import annotations  # Enables forward-compatible type annotations.

from datetime import UTC, date, datetime  # Imports date and timezone-aware datetime support.
from decimal import Decimal  # Imports Decimal for exact currency values.
from typing import Optional  # Imports Optional for nullable reference fields.

from pydantic import ConfigDict, Field  # Imports Pydantic configuration and field helpers.

from backend.models.ad import DealType  # Imports the shared DealType enum instead of redefining it.
from backend.models.base import BaseDocument, PyObjectId  # Imports the shared base document and MongoDB object id type.


class DealMatchItem(BaseDocument):  # Defines one matched deal result inside a weekly deal report.
    """Represents one product-store deal match with coupon, rebate, and reward results."""  # Documents the purpose of the nested model.

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)  # Rejects unknown fields and allows ObjectId-compatible values.

    product_ref: PyObjectId  # Stores the matched product reference id.
    store_ref: PyObjectId  # Stores the store reference id for the matched deal.
    deal_ref: Optional[PyObjectId] = None  # Stores the optional ad or deal reference id.
    coupon_refs: list[PyObjectId] = Field(default_factory=list)  # Stores coupon reference ids used in the deal.
    rebate_refs: list[PyObjectId] = Field(default_factory=list)  # Stores rebate reference ids used in the deal.
    shelf_price: Decimal  # Stores the regular shelf price before sale pricing.
    register_price: Decimal  # Stores the register price after store sale pricing and coupons.
    oop: Decimal  # Stores the out-of-pocket amount paid at checkout.
    rr_earned: Decimal = Decimal("0.00")  # Stores Walgreens Register Rewards earned.
    ecb_earned: Decimal = Decimal("0.00")  # Stores CVS ExtraBucks earned.
    total_rebates_back: Decimal = Decimal("0.00")  # Stores total rebate value expected back.
    deal_type: DealType  # Stores the shared deal type imported from the ad model.
    is_money_maker: bool = False  # Marks whether rewards and rebates exceed out-of-pocket cost.
    matched_as_substitute: bool = False  # Marks whether the item matched through an acceptable substitute.


class DealModel(BaseDocument):  # Defines the weekly generated deal report model.
    """Represents generated deal matches for one shopping week."""  # Documents the purpose of the top-level model.

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)  # Rejects unknown fields and allows ObjectId-compatible values.

    week_of: date  # Stores the week date for the generated deal report.
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))  # Stores the UTC generation timestamp.
    matches: list[DealMatchItem] = Field(default_factory=list)  # Stores typed deal match items instead of raw dictionaries.
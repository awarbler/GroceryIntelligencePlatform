# =============================================================================  # File header separator
# File: backend/models/deal_match.py  # Identifies the file path
# Project: Grocery Intelligence Platform  # Identifies the project
# Purpose: Defines saved deal opportunity matches for report generation.  # Explains the file purpose
# SRS Traceability: Section 16, Section 17, Section 18, Section 23  # Links model to SRS sections
# SDD Traceability: Section 7.10, Section 9, Section 15  # Links model to SDD sections
# =============================================================================  # File header separator

from datetime import date, datetime, timezone  # Imports date and timestamp types
from decimal import Decimal  # Imports Decimal for currency-safe arithmetic
from enum import Enum  # Imports Enum for controlled field values
from typing import Optional  # Imports Optional for nullable fields

from pydantic import BaseModel, Field  # Imports Pydantic model tools

from backend.models.base import BaseDocument, PyObjectId  # Imports shared Mongo document base and ObjectId type


class DealMatchType(str, Enum):  # Defines supported deal match types
    AD = "ad"  # Represents an ad-only opportunity
    COUPON = "coupon"  # Represents a coupon-only opportunity
    REWARD = "reward"  # Represents a reward-only opportunity
    STACKED = "stacked"  # Represents ad + coupon + reward opportunities


class DealMatchModel(BaseDocument):  # Defines the persisted deal match document
    product_ref: PyObjectId  # Stores the matched product ObjectId
    store_ref: PyObjectId  # Stores the store ObjectId
    deal_ref: Optional[PyObjectId] = None  # Stores the matched ad/deal ObjectId when present
    coupon_refs: list[PyObjectId] = Field(default_factory=list)  # Stores attached coupon ObjectIds
    reward_offer_refs: list[PyObjectId] = Field(default_factory=list)  # Stores attached reward offer ObjectIds
    shelf_price: Decimal = Decimal("0.00")  # Stores regular shelf price before sale pricing
    register_price: Decimal = Decimal("0.00")  # Stores price expected at register before register coupons
    subtotal_before_coupons: Decimal = Decimal("0.00")  # Stores subtotal before coupons are applied
    register_coupon_total: Decimal = Decimal("0.00")  # Stores only register-applied coupon value
    out_of_pocket: Decimal = Decimal("0.00")  # Stores register amount after coupons but before rewards
    total_rewards_value: Decimal = Decimal("0.00")  # Stores estimated reward value after purchase
    final_after_rewards: Decimal = Decimal("0.00")  # Stores net cost after rewards are considered
    deal_type: DealMatchType = DealMatchType.STACKED  # Stores the opportunity type
    is_money_maker: bool = False  # Flags whether rewards exceed out-of-pocket
    matched_as_substitute: bool = False  # Flags whether the match came from acceptable_substitutes
    week_of: date  # Stores the report week date
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Stores generation timestamp


class DealMatchCreate(BaseModel):  # Defines data required to create a deal match
    product_ref: PyObjectId  # Stores the matched product ObjectId
    store_ref: PyObjectId  # Stores the store ObjectId
    deal_ref: Optional[PyObjectId] = None  # Stores the matched ad/deal ObjectId when present
    coupon_refs: list[PyObjectId] = Field(default_factory=list)  # Stores attached coupon ObjectIds
    reward_offer_refs: list[PyObjectId] = Field(default_factory=list)  # Stores attached reward offer ObjectIds
    shelf_price: Decimal = Decimal("0.00")  # Stores regular shelf price before sale pricing
    register_price: Decimal = Decimal("0.00")  # Stores price expected at register before register coupons
    subtotal_before_coupons: Decimal = Decimal("0.00")  # Stores subtotal before coupons are applied
    register_coupon_total: Decimal = Decimal("0.00")  # Stores only register-applied coupon value
    out_of_pocket: Decimal = Decimal("0.00")  # Stores register amount after coupons but before rewards
    total_rewards_value: Decimal = Decimal("0.00")  # Stores estimated reward value after purchase
    final_after_rewards: Decimal = Decimal("0.00")  # Stores net cost after rewards are considered
    deal_type: DealMatchType = DealMatchType.STACKED  # Stores the opportunity type
    is_money_maker: bool = False  # Flags whether rewards exceed out-of-pocket
    matched_as_substitute: bool = False  # Flags whether the match came from acceptable_substitutes
    week_of: date  # Stores the report week date
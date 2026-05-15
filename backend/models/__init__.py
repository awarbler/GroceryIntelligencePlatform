# =============================================================================
# File: __init__.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Re-exports backend model classes and enums for cleaner import paths.
# Security Note: This file does not store secrets, credentials, or user data.
# SRS Traceability: Supports SRS v5.0 backend model organization and validation requirements.
# SDD Traceability: Supports SDD v5.0 backend model package structure and import design.
# =============================================================================

from backend.models.ad import (
    AdItem as AdItem,
)  # Re-exports the ad item model for package-level imports.
from backend.models.ad import (
    AdModel as AdModel,
)  # Re-exports the ad model for package-level imports.
from backend.models.ad import (
    DealType as DealType,
)  # Re-exports the shared deal type enum for package-level imports.
from backend.models.base import (
    BaseDocument as BaseDocument,
)  # Re-exports the shared base document model.
from backend.models.base import (
    PyObjectId as PyObjectId,
)  # Re-exports the MongoDB object ID type helper.
from backend.models.base import (
    StandardResponse as StandardResponse,
)  # Re-exports the shared response wrapper model.
from backend.models.coupon import (
    CouponModel as CouponModel,
)  # Re-exports the coupon model for package-level imports.
from backend.models.coupon import (
    CouponScope as CouponScope,
)  # Re-exports the coupon scope enum for package-level imports.
from backend.models.coupon import (
    CouponType as CouponType,
)  # Re-exports the coupon type enum for package-level imports.
from backend.models.deal import (
    DealMatchItem as DealMatchItem,
)  # Re-exports the deal match item model.
from backend.models.deal import (
    DealModel as DealModel,
)  # Re-exports the deal model for package-level imports.
from backend.models.product import (
    PriceRecord as PriceRecord,
)  # Re-exports the product price history model.
from backend.models.product import (
    ProductModel as ProductModel,
)  # Re-exports the product catalog model.
from backend.models.product import (
    ProductUnit as ProductUnit,
)  # Re-exports the product unit enum.
from backend.models.purchase import (
    CouponSource as CouponSource,
)  # Re-exports the purchase coupon source enum.
from backend.models.purchase import (
    InputType as InputType,
)  # Re-exports the purchase input type enum.
from backend.models.purchase import (
    PurchaseModel as PurchaseModel,
)  # Re-exports the purchase model.
from backend.models.purchase import (
    RewardUsed as RewardUsed,
)  # Re-exports the reward-used model.
from backend.models.raw_input import (
    RawInputModel as RawInputModel,
)  # Re-exports the raw input model.
from backend.models.rebate import (
    RebateModel as RebateModel,
)  # Re-exports the rebate model.
from backend.models.rebate import (
    RebateStatus as RebateStatus,
)  # Re-exports the rebate lifecycle enum.
from backend.models.store import (
    StoreModel as StoreModel,
)  # Re-exports the store configuration model.
from backend.models.user import (
    ReportFormat as ReportFormat,
)  # Re-exports the user report format enum.
from backend.models.user import UserModel as UserModel  # Re-exports the user model.

__all__ = [  # Defines the public package-level model API.
    "AdItem",  # Allows AdItem to be imported from backend.models.
    "AdModel",  # Allows AdModel to be imported from backend.models.
    "BaseDocument",  # Allows BaseDocument to be imported from backend.models.
    "CouponModel",  # Allows CouponModel to be imported from backend.models.
    "CouponScope",  # Allows CouponScope to be imported from backend.models.
    "CouponSource",  # Allows CouponSource to be imported from backend.models.
    "CouponType",  # Allows CouponType to be imported from backend.models.
    "DealMatchItem",  # Allows DealMatchItem to be imported from backend.models.
    "DealModel",  # Allows DealModel to be imported from backend.models.
    "DealType",  # Allows DealType to be imported from backend.models.
    "InputType",  # Allows InputType to be imported from backend.models.
    "PriceRecord",  # Allows PriceRecord to be imported from backend.models.
    "ProductModel",  # Allows ProductModel to be imported from backend.models.
    "ProductUnit",  # Allows ProductUnit to be imported from backend.models.
    "PurchaseModel",  # Allows PurchaseModel to be imported from backend.models.
    "PyObjectId",  # Allows PyObjectId to be imported from backend.models.
    "RawInputModel",  # Allows RawInputModel to be imported from backend.models.
    "RebateModel",  # Allows RebateModel to be imported from backend.models.
    "RebateStatus",  # Allows RebateStatus to be imported from backend.models.
    "ReportFormat",  # Allows ReportFormat to be imported from backend.models.
    "RewardUsed",  # Allows RewardUsed to be imported from backend.models.
    "StandardResponse",  # Allows StandardResponse to be imported from backend.models.
    "StoreModel",  # Allows StoreModel to be imported from backend.models.
    "UserModel",  # Allows UserModel to be imported from backend.models.
]

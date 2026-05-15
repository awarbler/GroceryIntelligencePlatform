# =============================================================================
# File: product.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines product catalog and price history models for normalized grocery tracking.
# Security Note: Product records do not store user secrets, credentials, or payment information.
# SRS Traceability: Supports SRS v5.0 product normalization, receipt matching, coupon matching, and deal comparison requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and product catalog design.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without requiring runtime forward references.

from datetime import date  # Imports date for observed price record dates.
from decimal import Decimal  # Imports Decimal for exact price-related values.
from enum import StrEnum  # Imports StrEnum so enum values behave like strings.
from typing import (Optional,)  # Imports Optional for fields that may be missing or unknown.

from pydantic import (BaseModel,ConfigDict,Field,)  # Imports Pydantic model tools and validation configuration.

from backend.models.base import (BaseDocument,PyObjectId,)  # Imports the shared document base and MongoDB object id type.


class ProductUnit(StrEnum):  # Defines allowed product measurement units.
    """Enum representing supported product size units."""  # Documents the purpose of the enum.

    EACH = "EACH"  # Represents one countable item.
    OUNCE = "OUNCE"  # Represents ounces.
    POUND = "POUND"  # Represents pounds.
    FLUID_OUNCE = "FLUID_OUNCE"  # Represents fluid ounces.
    COUNT = "COUNT"  # Represents package count.
    GRAM = "GRAM"  # Represents grams.
    LITER = "LITER"  # Represents liters.
    MILLILITER = "MILLILITER"  # Represents milliliters.


class PriceRecord(BaseModel):  # Defines one observed product price at one store.
    """Model representing a product price observed from a store, ad, receipt, or manual entry."""  # Documents the price record model.

    model_config = ConfigDict(
        extra="forbid"
    )  # Rejects unexpected fields during validation.

    store_ref: PyObjectId  # Stores the referenced store ObjectId.
    regular_price: Decimal = Field(
        ..., ge=Decimal("0.00")
    )  # Stores the regular shelf price and prevents negative values.
    sale_price: Optional[Decimal] = Field(
        default=None, ge=Decimal("0.00")
    )  # Stores the sale price when one exists.
    observed_date: date  # Stores the date when this price was observed.
    source: str = Field(..., min_length=1)  # Stores the source of the observed price.


class ProductModel(BaseDocument):  # Defines the normalized product catalog document.
    """Model representing a normalized grocery product."""  # Documents the purpose of the product model.

    model_config = ConfigDict(
        extra="forbid"
    )  # Rejects unexpected fields during validation.

    canonical_name: str = Field(
        ..., min_length=1
    )  # Stores the normalized product name used for matching.
    raw_names: list[str] = Field(
        default_factory=list
    )  # Stores receipt, ad, or coupon names seen before normalization.
    category: str = Field(
        ..., min_length=1
    )  # Stores the product category such as grocery, household, or personal care.
    brand: Optional[str] = Field(default=None)  # Stores the brand when known.
    size_value: Optional[Decimal] = Field(
        default=None, ge=Decimal("0.00")
    )  # Stores the numeric product size when known.
    size_unit: Optional[ProductUnit] = Field(
        default=None
    )  # Stores the unit connected to the product size.
    package_count: int = Field(
        default=1, ge=1
    )  # Stores how many units are included in the package.
    upc: Optional[str] = Field(
        default=None, min_length=8
    )  # Stores the barcode or UPC when available.
    store_refs: list[PyObjectId] = Field(
        default_factory=list
    )  # Stores stores where this product has appeared.
    average_shelf_price: Optional[Decimal] = Field(
        default=None, ge=Decimal("0.00")
    )  # Stores the observed average regular shelf price.
    last_seen_price: Optional[Decimal] = Field(
        default=None, ge=Decimal("0.00")
    )  # Stores the most recent observed shelf or sale price.
    size_variants: list[str] = Field(
        default_factory=list
    )  # Stores acceptable product size strings used during matching.
    avg_price_by_store: dict[str, Decimal] = Field(
        default_factory=dict
    )  # Stores average product price by store identifier.
    acceptable_substitutes: list[PyObjectId] = Field(
        default_factory=list
    )  # Stores product references that can substitute for this product.
    price_history: list[PriceRecord] = Field(
        default_factory=list
    )  # Stores observed price records over time.
    is_active: bool = Field(
        default=True
    )  # Stores whether the product is active for matching and reports.
    notes: str = Field(default="")  # Stores optional product notes.

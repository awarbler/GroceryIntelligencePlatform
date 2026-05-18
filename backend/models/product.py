# =============================================================================
# File: product.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Defines product catalog and price history models for normalized grocery tracking.
# Security Note: Product records do not store user secrets, credentials, or payment information.
# SRS Traceability: Supports SRS v5.0 product normalization, receipt matching, coupon matching, and deal comparison requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and product catalog design.
# =============================================================================

from __future__ import annotations# Enables modern type hints without requiring runtime forward references.

from datetime import date  # Imports date for observed price record dates.
from decimal import Decimal  # Imports Decimal for exact price-related values.
from enum import StrEnum  # Imports StrEnum so enum values behave like strings.
from typing import Optional# Imports Optional for fields that may be missing or unknown.

from pydantic import BaseModel,ConfigDict,Field# Imports Pydantic model tools and validation configuration.

from backend.models.base import BaseDocument,PyObjectId  # Imports the shared document base and MongoDB object id type.

from datetime import date  # Imports date for price history observed_date values.
from decimal import Decimal  # Imports Decimal for exact money values.
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

    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields during validation.

    store_ref: PyObjectId  # Stores the referenced store ObjectId.
    regular_price: Decimal = Field(..., ge=Decimal("0.00"))  # Stores the regular shelf price and prevents negative values.
    sale_price: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Stores the sale price when one exists.
    observed_date: date  # Stores the date when this price was observed.
    source: str = Field(..., min_length=1)  # Stores the source of the observed price.


class ProductModel(BaseDocument):  # Defines the normalized product catalog document.
    """Model representing a normalized grocery product."""  # Documents the purpose of the product model.

    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields during validation.
    canonical_name: str = Field(..., min_length=1)  # Stores the normalized product name used for matching.
    raw_names: list[str] = Field(default_factory=list)  # Stores receipt, ad, or coupon names seen before normalization.
    category: str = Field(..., min_length=1)  # Stores the product category such as grocery, household, or personal care.
    brand: Optional[str] = Field(default=None)  # Stores the brand when known.
    size_value: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Stores the numeric product size when known.
    size_unit: Optional[ProductUnit] = Field(default=None)  # Stores the unit connected to the product size.
    package_count: int = Field(default=1, ge=1)  # Stores how many units are included in the package.
    upc: Optional[str] = Field(default=None, min_length=8)  # Stores the barcode or UPC when available.
    store_refs: list[PyObjectId] = Field(default_factory=list)  # Stores stores where this product has appeared.
    average_shelf_price: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Stores the observed average regular shelf price.
    last_seen_price: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))  # Stores the most recent observed shelf or sale price.
    size_variants: list[str] = Field(default_factory=list)  # Stores acceptable product size strings used during matching.
    avg_price_by_store: dict[str, Decimal] = Field(default_factory=dict)  # Stores average product price by store identifier.
    acceptable_substitutes: list[PyObjectId] = Field(default_factory=list)  # Stores product references that can substitute for this product.
    price_history: list[PriceRecord] = Field(default_factory=list)  # Stores observed price records over time.
    is_active: bool = Field(default=True)  # Stores whether the product is active for matching and reports.
    notes: str = Field(default="")  # Stores optional product notes.

    async def update_price_history(  # Appends one observed price entry to a product document.
        self,  # Uses the current ProductsDataAccess instance.
        canonical_name: str,  # Receives the normalized product name used to find the product.
        store_ref: str,  # Receives the Phase 1 store identifier string, such as "heb".
        regular_price: Decimal,  # Receives the observed regular price as a Decimal.
        sale_price: Decimal | None,  # Receives the observed sale price when known.
        observed_date: date,  # Receives the purchase date as a date object.
        source: str,  # Receives the source label, such as "heb_online_receipt".
    ) -> None:  # Returns no value after the update.
        price_entry: dict[str, object] = {  # Builds one price history entry using PriceRecord-style field names.
            "store_ref": store_ref,  # Stores the store reference for this price observation.
            "regular_price": regular_price,  # Stores the observed regular price.
            "sale_price": sale_price,  # Stores the observed sale price when available.
            "observed_date": observed_date,  # Stores the date when this price was observed.
            "source": source,  # Stores where the price observation came from.
        }  # Ends the price history entry.

        await self.collection.update_one(  # Updates the matching product document.
            {"canonical_name": canonical_name},  # Finds the product by canonical name.
            {"$push": {"price_history": price_entry}},  # Appends the price entry to price_history.
        )  # Ends the MongoDB update call.
        
        async def add_product_alias(  # Defines owner-approved alias saving for P1-11 normalization corrections.
            self,  # Receives the product data access instance.
            canonical_name: str,  # Receives the canonical product name.
            alias: str,  # Receives the raw alias to add.
        ) -> bool:  # Returns whether a product document was updated.
            result = await self.collection.update_one(  # Updates products through the Data Access Layer.
                {"canonical_name": canonical_name},  # Finds the product by canonical name.
                {"$addToSet": {"aliases": alias}},  # Adds the alias without creating duplicates.
                upsert=False,  # Avoids creating accidental products from correction mistakes.
            )  # Ends the MongoDB update operation.
            return result.matched_count > 0  # Returns True only when an existing product was matched.
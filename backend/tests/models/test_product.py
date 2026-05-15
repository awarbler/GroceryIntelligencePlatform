# =============================================================================
# File: test_product.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests product catalog and price history model validation rules.
# Security Note: Tests use fake product data only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 product normalization and price tracking validation.
# SDD Traceability: Supports SDD v5.0 backend model test coverage.
# =============================================================================

from datetime import date  # Imports date for test price observation dates.
from decimal import Decimal  # Imports Decimal for currency-safe test values.

import pytest  # Imports pytest for exception assertions.
from bson import ObjectId  # Imports ObjectId for fake MongoDB references.
from pydantic import (
    ValidationError,
)  # Imports ValidationError for invalid model assertions.

from backend.models.product import (
    PriceRecord,
    ProductModel,
    ProductUnit,
)  # Imports the product models being tested.


def test_price_record_valid() -> (
    None
):  # Verifies that a valid price record can be created.
    store_ref = ObjectId()  # Creates a fake store ObjectId.
    price_record = PriceRecord(  # Creates a valid observed price record.
        store_ref=store_ref,  # Provides the fake store reference.
        regular_price=Decimal("4.99"),  # Provides a valid regular shelf price.
        sale_price=Decimal("3.99"),  # Provides a valid sale price.
        observed_date=date(2026, 5, 14),  # Provides the observed price date.
        source="HEB_RECEIPT",  # Provides the source of the price record.
    )  # Ends the price record construction.

    assert (
        price_record.store_ref == store_ref
    )  # Confirms the store reference is preserved.
    assert price_record.regular_price == Decimal(
        "4.99"
    )  # Confirms the regular price is preserved.
    assert price_record.sale_price == Decimal(
        "3.99"
    )  # Confirms the sale price is preserved.
    assert price_record.observed_date == date(
        2026, 5, 14
    )  # Confirms the observed date is preserved.
    assert price_record.source == "HEB_RECEIPT"  # Confirms the source is preserved.


def test_price_record_rejects_negative_regular_price() -> (
    None
):  # Verifies that negative regular prices are rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PriceRecord(  # Attempts to create an invalid price record.
            store_ref=ObjectId(),  # Provides a fake store reference.
            regular_price=Decimal(
                "-1.00"
            ),  # Provides an invalid negative regular price.
            sale_price=Decimal("0.99"),  # Provides a valid sale price.
            observed_date=date(2026, 5, 14),  # Provides a valid observed date.
            source="HEB_RECEIPT",  # Provides a valid source.
        )  # Ends the invalid price record construction.


def test_price_record_rejects_extra_field() -> (
    None
):  # Verifies that unknown price record fields are rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PriceRecord(  # Attempts to create a price record with an unexpected field.
            store_ref=ObjectId(),  # Provides a fake store reference.
            regular_price=Decimal("4.99"),  # Provides a valid regular price.
            sale_price=Decimal("3.99"),  # Provides a valid sale price.
            observed_date=date(2026, 5, 14),  # Provides a valid observed date.
            source="HEB_RECEIPT",  # Provides a valid source.
            unexpected_field="not allowed",  # Provides a field that should be rejected.
        )  # Ends the invalid price record construction.


def test_product_model_valid() -> (
    None
):  # Verifies that a valid product model can be created.
    store_ref = ObjectId()  # Creates a fake store ObjectId.
    substitute_ref = ObjectId()  # Creates a fake substitute product ObjectId.
    price_record = PriceRecord(  # Creates a nested price record for price history.
        store_ref=store_ref,  # Provides the fake store reference.
        regular_price=Decimal("4.99"),  # Provides a valid regular price.
        sale_price=Decimal("3.99"),  # Provides a valid sale price.
        observed_date=date(2026, 5, 14),  # Provides the observed price date.
        source="HEB_AD",  # Provides the source of the observed price.
    )  # Ends the price record construction.

    product = ProductModel(  # Creates a valid normalized product.
        canonical_name="oikos greek yogurt",  # Provides the normalized product name.
        raw_names=[
            "Oikos Yogurt 5.3 oz"
        ],  # Provides raw product names seen in source data.
        category="Dairy",  # Provides the product category.
        brand="Oikos",  # Provides the product brand.
        size_value=Decimal("5.30"),  # Provides the numeric product size.
        size_unit=ProductUnit.OUNCE,  # Provides the product size unit.
        package_count=1,  # Provides the package count.
        upc="12345678",  # Provides a fake valid UPC length.
        store_refs=[store_ref],  # Provides stores where the product appears.
        average_shelf_price=Decimal("4.99"),  # Provides the average shelf price.
        last_seen_price=Decimal("3.99"),  # Provides the last observed price.
        size_variants=["5.3 oz", "4 pack"],  # Provides acceptable size strings.
        avg_price_by_store={
            "HEB": Decimal("4.99")
        },  # Provides average price by store key.
        acceptable_substitutes=[
            substitute_ref
        ],  # Provides acceptable substitute product references.
        price_history=[price_record],  # Provides one observed price history record.
        is_active=True,  # Marks the product as active.
        notes="Test product only",  # Provides optional product notes.
    )  # Ends the product model construction.

    assert (
        product.canonical_name == "oikos greek yogurt"
    )  # Confirms the canonical name is preserved.
    assert product.brand == "Oikos"  # Confirms the brand is preserved.
    assert product.category == "Dairy"  # Confirms the category is preserved.
    assert (
        product.size_unit == ProductUnit.OUNCE
    )  # Confirms the product unit enum is preserved.
    assert product.price_history[0].regular_price == Decimal(
        "4.99"
    )  # Confirms nested price history is preserved.
    assert product.acceptable_substitutes == [
        substitute_ref
    ]  # Confirms substitute references are preserved.


def test_product_rejects_missing_canonical_name() -> (
    None
):  # Verifies that canonical_name is required.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        ProductModel(  # Attempts to create a product without canonical_name.
            category="Dairy",  # Provides the required category.
        )  # Ends the invalid product construction.


def test_product_rejects_extra_field() -> (
    None
):  # Verifies that unknown product fields are rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        ProductModel(  # Attempts to create a product with an unexpected field.
            canonical_name="oikos greek yogurt",  # Provides the required canonical name.
            category="Dairy",  # Provides the required category.
            unexpected_field="not allowed",  # Provides a field that should be rejected.
        )  # Ends the invalid product construction.

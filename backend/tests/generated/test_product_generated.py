# =============================================================================
# File: test_product_generated.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to generate product and price record validation cases.
# Security Note: Tests use generated fake values only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 generated validation coverage for products and price records.
# SDD Traceability: Supports SDD v5.0 automated model validation strategy.
# =============================================================================

from datetime import date  # Imports date for generated observed price dates.
from decimal import Decimal  # Imports Decimal for generated currency values.

from bson import ObjectId  # Imports ObjectId for generated fake MongoDB references.
from hypothesis import given  # Imports the Hypothesis decorator for generated tests.
from hypothesis import strategies as st  # Imports Hypothesis strategies for generated values.

from backend.models.product import PriceRecord, ProductModel, ProductUnit  # Imports the product models being generated and validated.


positive_decimal_strategy = st.decimals(  # Defines generated non-negative decimal values.
    min_value=Decimal("0.00"),  # Sets the smallest generated currency value.
    max_value=Decimal("999.99"),  # Sets the largest generated currency value.
    places=2,  # Limits generated values to two decimal places.
    allow_nan=False,  # Prevents invalid NaN decimal values.
    allow_infinity=False,  # Prevents invalid infinity decimal values.
)  # Ends the decimal strategy definition.

non_empty_text_strategy = st.text(  # Defines generated non-empty text values.
    min_size=1,  # Requires at least one character.
    max_size=50,  # Limits generated text length.
).filter(lambda value: value.strip() != "")  # Removes blank-only generated strings.


@given(  # Generates many valid price record examples.
    regular_price=positive_decimal_strategy,  # Generates valid regular prices.
    sale_price=st.none() | positive_decimal_strategy,  # Generates either no sale price or a valid sale price.
    observed_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31)),  # Generates realistic observation dates.
    source=non_empty_text_strategy,  # Generates valid source strings.
)  # Ends the generated input list.
def test_generated_price_record_valid(regular_price: Decimal, sale_price: Decimal | None, observed_date: date, source: str) -> None:  # Tests generated valid price records.
    price_record = PriceRecord(  # Creates a generated valid price record.
        store_ref=ObjectId(),  # Provides a fake generated store reference.
        regular_price=regular_price,  # Provides the generated regular price.
        sale_price=sale_price,  # Provides the generated sale price.
        observed_date=observed_date,  # Provides the generated observed date.
        source=source,  # Provides the generated source.
    )  # Ends the price record construction.

    assert price_record.regular_price >= Decimal("0.00")  # Confirms the regular price is non-negative.
    assert price_record.sale_price is None or price_record.sale_price >= Decimal("0.00")  # Confirms the sale price is either missing or non-negative.
    assert price_record.source.strip() != ""  # Confirms the source is not blank.


@given(  # Generates many valid product examples.
    canonical_name=non_empty_text_strategy,  # Generates valid canonical product names.
    category=non_empty_text_strategy,  # Generates valid product categories.
    brand=st.none() | non_empty_text_strategy,  # Generates either no brand or a valid brand.
    package_count=st.integers(min_value=1, max_value=100),  # Generates valid package counts.
    size_unit=st.sampled_from(list(ProductUnit)),  # Generates valid product unit enum values.
    average_shelf_price=st.none() | positive_decimal_strategy,  # Generates optional average shelf prices.
    last_seen_price=st.none() | positive_decimal_strategy,  # Generates optional last seen prices.
)  # Ends the generated input list.
def test_generated_product_model_valid(  # Tests generated valid product models.
    canonical_name: str,  # Receives the generated canonical name.
    category: str,  # Receives the generated category.
    brand: str | None,  # Receives the generated brand.
    package_count: int,  # Receives the generated package count.
    size_unit: ProductUnit,  # Receives the generated product unit.
    average_shelf_price: Decimal | None,  # Receives the generated average shelf price.
    last_seen_price: Decimal | None,  # Receives the generated last seen price.
) -> None:  # Declares that the test returns nothing.
    product = ProductModel(  # Creates a generated valid product model.
        canonical_name=canonical_name,  # Provides the generated canonical name.
        category=category,  # Provides the generated category.
        brand=brand,  # Provides the generated brand.
        package_count=package_count,  # Provides the generated package count.
        size_unit=size_unit,  # Provides the generated product unit.
        average_shelf_price=average_shelf_price,  # Provides the generated average shelf price.
        last_seen_price=last_seen_price,  # Provides the generated last seen price.
    )  # Ends the product model construction.

    assert product.canonical_name == canonical_name  # Confirms the canonical name is preserved.
    assert product.category == category  # Confirms the category is preserved.
    assert product.package_count >= 1  # Confirms the package count is valid.
    assert product.size_unit == size_unit  # Confirms the product unit is preserved.
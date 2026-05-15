# =============================================================================
# File: test_ad_generated.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to test generated AdModel and AdItem validation cases.
# Security Note: Tests use generated fake values only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 ad, coupon, and promotion validation requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and automated test coverage.
# =============================================================================

from datetime import date  # Imports date for generated ad start and end dates.
from datetime import (
    timedelta,
)  # Imports timedelta to create valid and invalid date ranges.
from decimal import (
    Decimal,
)  # Imports Decimal for generated money and percentage values.

import pytest  # Imports pytest for validation error assertions.
from bson import (
    ObjectId,
)  # Imports ObjectId to create fake MongoDB document references.
from hypothesis import (
    given,
)  # Imports the Hypothesis decorator that generates test inputs.
from hypothesis import (
    settings,
)  # Imports settings so this file can limit generated example count.
from hypothesis import (
    strategies as st,
)  # Imports Hypothesis strategies for generated data.

from backend.models.ad import AdItem  # Imports the AdItem model being tested.
from backend.models.ad import AdModel  # Imports the AdModel model being tested.
from backend.models.ad import DealType  # Imports the DealType enum being tested.


money_strategy = st.decimals(  # Creates a reusable strategy for valid money-like Decimal values.
    min_value=Decimal("0.00"),  # Sets the minimum generated value to zero.
    max_value=Decimal(
        "999.99"
    ),  # Sets the maximum generated value to a reasonable test amount.
    places=2,  # Limits generated decimals to two places like currency.
    allow_nan=False,  # Prevents NaN values because money cannot be NaN.
    allow_infinity=False,  # Prevents infinity values because money cannot be infinite.
)

percent_strategy = st.decimals(  # Creates a reusable strategy for valid percentage values.
    min_value=Decimal("0.00"),  # Sets the minimum generated percent to zero.
    max_value=Decimal("100.00"),  # Sets the maximum generated percent to one hundred.
    places=2,  # Limits generated percentages to two decimal places.
    allow_nan=False,  # Prevents NaN values because percent values must be numeric.
    allow_infinity=False,  # Prevents infinity values because percent values must be finite.
)


text_strategy = st.text(  # Creates a reusable strategy for required non-empty strings.
    min_size=1,  # Requires at least one character.
    max_size=80,  # Caps generated text length to keep failing examples readable.
).filter(
    lambda value: value.strip() != ""
)  # Rejects strings that contain only whitespace.


@given(  # Starts a generated test with multiple generated inputs.
    item_name=text_strategy,  # Generates a valid non-empty item name.
    sale_price=money_strategy,  # Generates a valid non-negative sale price.
    deal_type=st.sampled_from(list(DealType)),  # Generates one approved DealType value.
)
@settings(
    max_examples=50
)  # Limits the number of generated examples so the test stays fast.
def test_generated_ad_item_accepts_valid_required_fields(  # Verifies generated valid AdItem inputs are accepted.
    item_name: str,  # Receives the generated item name.
    sale_price: Decimal,  # Receives the generated sale price.
    deal_type: DealType,  # Receives the generated deal type.
) -> None:  # Declares that this test does not return a value.
    ad_item = AdItem(  # Creates an AdItem from generated valid values.
        item_name=item_name,  # Passes the generated item name into the model.
        sale_price=sale_price,  # Passes the generated sale price into the model.
        deal_type=deal_type,  # Passes the generated deal type into the model.
    )
    assert ad_item.item_name == item_name  # Confirms the item name was stored.
    assert ad_item.sale_price == sale_price  # Confirms the sale price was stored.
    assert ad_item.deal_type == deal_type  # Confirms the deal type was stored.


@given(
    start_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))
)  # Generates valid ad start dates.
@settings(max_examples=50)  # Limits generated examples for speed and readability.
def test_generated_ad_model_accepts_same_start_and_end_date(
    start_date: date,
) -> None:  # Verifies one-day ads are valid.
    ad = AdModel(  # Creates an ad where start and end date are the same.
        store_ref=ObjectId(),  # Provides a fake store reference.
        start_date=start_date,  # Uses the generated start date.
        end_date=start_date,  # Uses the same date as the generated end date.
        source_type="generated-test",  # Provides a valid source type.
        items=[],  # Provides an empty item list.
    )
    assert ad.start_date == start_date  # Confirms the start date was stored.
    assert ad.end_date == start_date  # Confirms the same-day end date was stored.


@given(  # Starts a generated test with two generated inputs.
    start_date=st.dates(
        min_value=date(2020, 1, 1), max_value=date(2030, 12, 30)
    ),  # Generates a start date with room for a later end date.
    days_after=st.integers(
        min_value=0, max_value=30
    ),  # Generates how many days after the start date the ad ends.
)
@settings(max_examples=50)  # Limits generated examples for speed and readability.
def test_generated_ad_model_accepts_end_date_on_or_after_start_date(  # Verifies valid generated date ranges are accepted.
    start_date: date,  # Receives the generated start date.
    days_after: int,  # Receives the generated day offset.
) -> None:  # Declares that this test does not return a value.
    end_date = start_date + timedelta(
        days=days_after
    )  # Creates an end date on or after the start date.
    ad = AdModel(  # Creates an ad with a valid generated date range.
        store_ref=ObjectId(),  # Provides a fake store reference.
        start_date=start_date,  # Uses the generated start date.
        end_date=end_date,  # Uses the generated valid end date.
        source_type="generated-test",  # Provides a valid source type.
        items=[],  # Provides an empty item list.
    )
    assert (
        ad.end_date >= ad.start_date
    )  # Confirms the stored end date is not before the start date.


@given(  # Starts a generated test with two generated inputs.
    start_date=st.dates(
        min_value=date(2020, 1, 2), max_value=date(2030, 12, 31)
    ),  # Generates a start date with room for an earlier end date.
    days_before=st.integers(
        min_value=1, max_value=30
    ),  # Generates how many days before the start date the invalid end date occurs.
)
@settings(max_examples=50)  # Limits generated examples for speed and readability.
def test_generated_ad_model_rejects_end_date_before_start_date(  # Verifies invalid generated date ranges are rejected.
    start_date: date,  # Receives the generated start date.
    days_before: int,  # Receives the generated day offset.
) -> None:  # Declares that this test does not return a value.
    end_date = start_date - timedelta(
        days=days_before
    )  # Creates an invalid end date before the start date.
    with pytest.raises(
        ValueError, match="end_date must be greater than or equal to start_date"
    ):  # Expects the date range validator error.
        AdModel(  # Attempts to create an invalid ad.
            store_ref=ObjectId(),  # Provides a fake store reference.
            start_date=start_date,  # Uses the generated start date.
            end_date=end_date,  # Uses the generated invalid end date.
            source_type="generated-test",  # Provides a valid source type.
            items=[],  # Provides an empty item list.
        )


@given(
    percent_off=percent_strategy
)  # Generates valid percentage values from 0 through 100.
@settings(max_examples=50)  # Limits generated examples for speed and readability.
def test_generated_percent_off_accepts_valid_percentage(
    percent_off: Decimal,
) -> None:  # Verifies valid percent-off values are accepted.
    ad_item = AdItem(  # Creates a generated percent-off ad item.
        item_name="Generated Percent Deal",  # Provides a stable item name.
        sale_price=Decimal("0.00"),  # Provides a valid non-negative sale price.
        deal_type=DealType.PERCENT_OFF,  # Uses the percent-off deal type.
        percent_off=percent_off,  # Uses the generated valid percent value.
    )
    assert (
        ad_item.percent_off == percent_off
    )  # Confirms the generated percent value was stored.


@given(
    percent_off=st.decimals(
        min_value=Decimal("100.01"),
        max_value=Decimal("999.99"),
        places=2,
        allow_nan=False,
        allow_infinity=False,
    )
)  # Generates invalid percentages over 100.
@settings(max_examples=25)  # Limits generated invalid examples for speed.
def test_generated_percent_off_rejects_percentage_over_100(
    percent_off: Decimal,
) -> None:  # Verifies percentages over 100 are rejected.
    with pytest.raises(
        ValueError
    ):  # Expects Pydantic to reject the invalid percentage.
        AdItem(  # Attempts to create an invalid percent-off ad item.
            item_name="Generated Invalid Percent Deal",  # Provides a stable item name.
            sale_price=Decimal("0.00"),  # Provides a valid non-negative sale price.
            deal_type=DealType.PERCENT_OFF,  # Uses the percent-off deal type.
            percent_off=percent_off,  # Uses the generated invalid percent value.
        )


@given(
    negative_price=st.decimals(
        min_value=Decimal("-999.99"),
        max_value=Decimal("-0.01"),
        places=2,
        allow_nan=False,
        allow_infinity=False,
    )
)  # Generates invalid negative prices.
@settings(max_examples=25)  # Limits generated invalid examples for speed.
def test_generated_ad_item_rejects_negative_sale_price(
    negative_price: Decimal,
) -> None:  # Verifies negative sale prices are rejected.
    with pytest.raises(
        ValueError
    ):  # Expects Pydantic to reject the invalid sale price.
        AdItem(  # Attempts to create an invalid ad item.
            item_name="Generated Invalid Price Deal",  # Provides a stable item name.
            sale_price=negative_price,  # Uses the generated invalid negative price.
            deal_type=DealType.STANDARD,  # Uses a valid deal type so only the price is invalid.
        )

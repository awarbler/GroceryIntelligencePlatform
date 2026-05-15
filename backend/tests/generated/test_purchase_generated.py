# =============================================================================
# File: test_purchase_generated.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to generate PurchaseModel validation test cases.
# Security Note: Tests use generated fake purchase data only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 purchase validation, coupon tracking, rebate tracking, and report input requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and generated test coverage.
# =============================================================================

from __future__ import annotations  # Enables forward-compatible type annotations.

from datetime import date  # Imports date for purchase_date values.
from decimal import Decimal  # Imports Decimal for exact currency values.

import pytest  # Imports pytest for validation error assertions.
from hypothesis import given  # Imports the Hypothesis decorator for generated tests.
from hypothesis import (
    strategies as st,
)  # Imports Hypothesis strategies for generated input values.
from pydantic import (
    ValidationError,
)  # Imports ValidationError for failed Pydantic validation checks.

from backend.models.purchase import (
    CouponSource,
)  # Imports the coupon source enum under test.
from backend.models.purchase import InputType  # Imports the input type enum under test.
from backend.models.purchase import (
    PurchaseModel,
)  # Imports the purchase model under test.
from backend.models.purchase import (
    RewardUsed,
)  # Imports the reward-used model under test.


money_values = st.decimals(  # Defines valid generated money values.
    min_value=Decimal("0.00"),  # Sets the smallest valid money value.
    max_value=Decimal("999.99"),  # Sets a safe maximum money value for model tests.
    places=2,  # Limits generated money values to two decimal places.
    allow_nan=False,  # Prevents NaN values because money cannot be NaN.
    allow_infinity=False,  # Prevents infinity values because money cannot be infinite.
)  # Ends the valid money strategy.

negative_money_values = st.decimals(  # Defines invalid generated negative money values.
    min_value=Decimal("-999.99"),  # Sets the smallest generated negative value.
    max_value=Decimal("-0.01"),  # Sets the largest generated negative value.
    places=2,  # Limits generated invalid money values to two decimal places.
    allow_nan=False,  # Prevents NaN values because validation should focus on negativity.
    allow_infinity=False,  # Prevents infinity values because validation should focus on negativity.
)  # Ends the negative money strategy.

confidence_values = st.floats(  # Defines valid parser confidence values.
    min_value=0.0,  # Sets the smallest valid parser confidence.
    max_value=1.0,  # Sets the largest valid parser confidence.
    allow_nan=False,  # Prevents NaN because parser confidence must be numeric.
    allow_infinity=False,  # Prevents infinity because parser confidence must be bounded.
)  # Ends the valid confidence strategy.

invalid_confidence_values = st.one_of(  # Defines invalid parser confidence values.
    st.floats(
        max_value=-0.0001, allow_nan=False, allow_infinity=False
    ),  # Generates confidence values below zero.
    st.floats(
        min_value=1.0001, allow_nan=False, allow_infinity=False
    ),  # Generates confidence values above one.
)  # Ends the invalid confidence strategy.


def generated_purchase_payload() -> dict[
    str, object
]:  # Builds a reusable valid payload for generated tests.
    return {  # Returns the valid baseline purchase payload.
        "store_ref": "507f1f77bcf86cd799439011",  # Provides a fake store ObjectId reference.
        "canonical_name": "Generated Test Item",  # Provides a normalized product name.
        "raw_name": "GENERATED ITEM",  # Provides fake receipt text.
        "category": "Generated Category",  # Provides a product category.
        "brand": "Generated Brand",  # Provides a product brand.
        "size": "1 ct",  # Provides a product size.
        "quantity": 1,  # Provides a valid purchase quantity.
        "purchase_date": date(2026, 5, 14),  # Provides a fixed purchase date.
        "shelf_price": Decimal("9.99"),  # Provides a valid shelf price.
        "sale_price": Decimal("8.99"),  # Provides a valid sale price.
        "register_price": Decimal("8.99"),  # Provides a valid register price.
        "subtotal_before_coupons": Decimal(
            "8.99"
        ),  # Provides a valid subtotal before coupons.
        "out_of_pocket": Decimal("7.99"),  # Provides a valid out-of-pocket amount.
        "coupon_used": True,  # Marks the generated item as using a coupon.
        "coupon_source": CouponSource.MANUFACTURER,  # Provides a valid coupon source.
        "coupon_amount": Decimal("1.00"),  # Provides a valid coupon amount.
        "register_rewards_used": {
            "used": False,
            "amount": Decimal("0.00"),
        },  # Provides valid Register Reward usage.
        "cvs_ecb_used": {
            "used": False,
            "amount": Decimal("0.00"),
        },  # Provides valid CVS ECB usage.
        "rebate_company": None,  # Provides no rebate company.
        "rebate_amount": Decimal("0.00"),  # Provides a valid rebate amount.
        "rebate_status": None,  # Provides no rebate status.
        "source_type": InputType.MANUAL_ENTRY,  # Provides a valid input source.
        "raw_input_ref": None,  # Provides no raw input reference.
        "parse_confidence": None,  # Provides no parser confidence by default.
        "user_corrected": False,  # Marks the record as not user corrected.
        "notes": "",  # Provides empty notes.
    }  # Ends the baseline payload dictionary.


@given(shelf_price=money_values)  # Generates valid shelf_price values.
def test_generated_purchase_accepts_valid_shelf_price(
    shelf_price: Decimal,
) -> None:  # Tests generated valid shelf prices.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["shelf_price"] = (
        shelf_price  # Replaces shelf_price with a generated valid value.
    )
    purchase = PurchaseModel(
        **payload
    )  # Creates the purchase model with generated data.
    assert (
        purchase.shelf_price == shelf_price
    )  # Confirms the generated shelf price was accepted.


@given(register_price=money_values)  # Generates valid register_price values.
def test_generated_purchase_accepts_valid_register_price(
    register_price: Decimal,
) -> None:  # Tests generated valid register prices.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["register_price"] = (
        register_price  # Replaces register_price with a generated valid value.
    )
    purchase = PurchaseModel(
        **payload
    )  # Creates the purchase model with generated data.
    assert (
        purchase.register_price == register_price
    )  # Confirms the generated register price was accepted.


@given(out_of_pocket=money_values)  # Generates valid out_of_pocket values.
def test_generated_purchase_accepts_valid_out_of_pocket(
    out_of_pocket: Decimal,
) -> None:  # Tests generated valid out-of-pocket values.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["out_of_pocket"] = (
        out_of_pocket  # Replaces out_of_pocket with a generated valid value.
    )
    purchase = PurchaseModel(
        **payload
    )  # Creates the purchase model with generated data.
    assert (
        purchase.out_of_pocket == out_of_pocket
    )  # Confirms the generated out-of-pocket value was accepted.


@given(negative_value=negative_money_values)  # Generates invalid negative money values.
def test_generated_purchase_rejects_negative_shelf_price(
    negative_value: Decimal,
) -> None:  # Tests invalid negative shelf prices.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["shelf_price"] = (
        negative_value  # Replaces shelf_price with a generated negative value.
    )
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a purchase with invalid shelf_price.


@given(negative_value=negative_money_values)  # Generates invalid negative money values.
def test_generated_purchase_rejects_negative_register_price(
    negative_value: Decimal,
) -> None:  # Tests invalid negative register prices.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["register_price"] = (
        negative_value  # Replaces register_price with a generated negative value.
    )
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a purchase with invalid register_price.


@given(negative_value=negative_money_values)  # Generates invalid negative money values.
def test_generated_purchase_rejects_negative_out_of_pocket(
    negative_value: Decimal,
) -> None:  # Tests invalid negative out-of-pocket values.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["out_of_pocket"] = (
        negative_value  # Replaces out_of_pocket with a generated negative value.
    )
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a purchase with invalid out_of_pocket.


@given(negative_value=negative_money_values)  # Generates invalid negative money values.
def test_generated_purchase_rejects_negative_coupon_amount(
    negative_value: Decimal,
) -> None:  # Tests invalid negative coupon amounts.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["coupon_amount"] = (
        negative_value  # Replaces coupon_amount with a generated negative value.
    )
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a purchase with invalid coupon_amount.


@given(negative_value=negative_money_values)  # Generates invalid negative money values.
def test_generated_purchase_rejects_negative_rebate_amount(
    negative_value: Decimal,
) -> None:  # Tests invalid negative rebate amounts.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["rebate_amount"] = (
        negative_value  # Replaces rebate_amount with a generated negative value.
    )
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a purchase with invalid rebate_amount.


@given(parse_confidence=confidence_values)  # Generates valid parser confidence values.
def test_generated_purchase_accepts_valid_parse_confidence(
    parse_confidence: float,
) -> None:  # Tests valid parser confidence values.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["parse_confidence"] = (
        parse_confidence  # Replaces parse_confidence with a generated valid value.
    )
    purchase = PurchaseModel(
        **payload
    )  # Creates the purchase model with generated data.
    assert (
        purchase.parse_confidence == parse_confidence
    )  # Confirms the generated parser confidence was accepted.


@given(
    parse_confidence=invalid_confidence_values
)  # Generates invalid parser confidence values.
def test_generated_purchase_rejects_invalid_parse_confidence(
    parse_confidence: float,
) -> None:  # Tests invalid parser confidence values.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["parse_confidence"] = (
        parse_confidence  # Replaces parse_confidence with a generated invalid value.
    )
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a purchase with invalid parse_confidence.


@given(
    quantity=st.integers(min_value=1, max_value=500)
)  # Generates valid quantity values.
def test_generated_purchase_accepts_valid_quantity(
    quantity: int,
) -> None:  # Tests valid generated quantities.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["quantity"] = quantity  # Replaces quantity with a generated valid value.
    purchase = PurchaseModel(
        **payload
    )  # Creates the purchase model with generated data.
    assert (
        purchase.quantity == quantity
    )  # Confirms the generated quantity was accepted.


@given(quantity=st.integers(max_value=0))  # Generates invalid quantity values.
def test_generated_purchase_rejects_invalid_quantity(
    quantity: int,
) -> None:  # Tests invalid generated quantities.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["quantity"] = quantity  # Replaces quantity with a generated invalid value.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(**payload)  # Attempts to create a purchase with invalid quantity.


@given(reward_amount=money_values)  # Generates valid reward amount values.
def test_generated_reward_used_accepts_valid_amount(
    reward_amount: Decimal,
) -> None:  # Tests valid RewardUsed amounts.
    reward = RewardUsed(
        used=True, amount=reward_amount
    )  # Creates a RewardUsed model with generated money.
    assert reward.used is True  # Confirms the reward used flag is stored.
    assert (
        reward.amount == reward_amount
    )  # Confirms the generated reward amount was accepted.


@given(
    negative_value=negative_money_values
)  # Generates invalid negative reward amounts.
def test_generated_reward_used_rejects_negative_amount(
    negative_value: Decimal,
) -> None:  # Tests invalid RewardUsed amounts.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        RewardUsed(
            used=True, amount=negative_value
        )  # Attempts to create a reward with a negative amount.


@given(
    optional_reward_value=money_values
)  # Generates valid optional future reward values.
def test_generated_purchase_accepts_future_optional_reward_values(
    optional_reward_value: Decimal,
) -> None:  # Tests optional future reward fields.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["walgreens_cash_redeemed"] = (
        optional_reward_value  # Adds a generated Walgreens Cash redeemed amount.
    )
    payload["walgreens_cash_earned"] = (
        optional_reward_value  # Adds a generated Walgreens Cash earned amount.
    )
    payload["rr_used_amount"] = (
        optional_reward_value  # Adds a generated Register Rewards used amount.
    )
    payload["rr_earned_amount"] = (
        optional_reward_value  # Adds a generated Register Rewards earned amount.
    )
    payload["walmart_cash_earned"] = (
        optional_reward_value  # Adds a generated Walmart Cash earned amount.
    )
    payload["walmart_cash_used"] = (
        optional_reward_value  # Adds a generated Walmart Cash used amount.
    )
    payload["ecb_earned"] = (
        optional_reward_value  # Adds a generated CVS ECB earned amount.
    )
    payload["ecb_used"] = optional_reward_value  # Adds a generated CVS ECB used amount.
    purchase = PurchaseModel(
        **payload
    )  # Creates the purchase model with generated future rewards.
    assert (
        purchase.walgreens_cash_redeemed == optional_reward_value
    )  # Confirms Walgreens Cash redeemed was accepted.
    assert (
        purchase.rr_earned_amount == optional_reward_value
    )  # Confirms Register Rewards earned was accepted.
    assert (
        purchase.walmart_cash_used == optional_reward_value
    )  # Confirms Walmart Cash used was accepted.
    assert (
        purchase.ecb_used == optional_reward_value
    )  # Confirms CVS ECB used was accepted.


@given(
    negative_value=negative_money_values
)  # Generates invalid negative optional reward values.
def test_generated_purchase_rejects_negative_future_reward_values(
    negative_value: Decimal,
) -> None:  # Tests invalid future reward values.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["walgreens_cash_redeemed"] = (
        negative_value  # Adds an invalid negative future reward value.
    )
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a purchase with an invalid future reward value.


@given(
    extra_value=st.text(min_size=1, max_size=25)
)  # Generates extra undefined field values.
def test_generated_purchase_rejects_extra_fields(
    extra_value: str,
) -> None:  # Tests that undefined fields are rejected.
    payload = generated_purchase_payload()  # Builds a valid baseline payload.
    payload["generated_extra_field"] = extra_value  # Adds an undefined model field.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(**payload)  # Attempts to create a purchase with an extra field.

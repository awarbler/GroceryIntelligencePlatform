# =============================================================================
# File: test_coupon_generated.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to generate CouponModel validation cases for dollar discounts, percent discounts, basket thresholds, and date ordering.
# Security Note: Tests use generated fake coupon data only and do not contain secrets, payment data, or personal customer information.
# SRS Traceability: Supports SRS v5.0 P1-04 generated coupon validation testing for expiration dates, discount values, basket thresholds, and coupon workflow consistency.
# SDD Traceability: Supports SDD v5.0 backend generated model testing for coupon data validation.
# =============================================================================

from datetime import date  # Imports the date type for coupon date and expiration date values.
from decimal import Decimal  # Imports Decimal for exact generated money and percent values.

import pytest  # Imports pytest for exception assertions.
from bson import ObjectId  # Imports ObjectId to create realistic MongoDB store references.
from hypothesis import given  # Imports the Hypothesis decorator that generates test inputs.
from hypothesis import settings  # Imports Hypothesis settings to control generated example count.
from hypothesis import strategies as st  # Imports Hypothesis strategies for generating input values.
from pydantic import ValidationError  # Imports ValidationError to confirm invalid generated data fails.

from backend.models.coupon import CouponModel, CouponScope, CouponType  # Imports the coupon model and enums under test.


def build_generated_coupon_data() -> dict:  # Defines a reusable valid coupon payload for generated tests.
    """Return valid base coupon data for generated test overrides."""  # Explains the helper purpose.

    return {  # Starts the valid generated coupon dictionary.
        "store_ref": ObjectId(),  # Provides a realistic MongoDB ObjectId for the related store.
        "coupon_type": CouponType.STORE_DIGITAL,  # Uses a valid store digital coupon type.
        "coupon_scope": CouponScope.ITEM,  # Uses an item-level coupon scope.
        "is_store_coupon": True,  # Marks the coupon as store-issued.
        "store_name": "H-E-B",  # Provides the store display name.
        "is_manufacturer_coupon": False,  # Marks the coupon as not manufacturer-issued.
        "coupon_date": date(2026, 5, 1),  # Provides the coupon availability date.
        "expiration_date": date(2026, 5, 31),  # Provides the required expiration date.
        "item_name": "Generated Coupon Item",  # Provides a generic generated-test item name.
        "item_size": "1 ct",  # Provides a simple item size.
        "brand": "Generated Brand",  # Provides a generic generated-test brand.
        "discount_amount": Decimal("1.00"),  # Provides a valid default dollar discount amount.
        "discount_percent": None,  # Leaves percent discount empty for dollar coupons.
        "discount_type": "dollars",  # Identifies the default coupon as a dollar discount.
        "required_purchase_quantity": 1,  # Requires one qualifying item.
        "required_purchase_amount": None,  # Leaves basket threshold empty for item coupons.
        "store_purchased": "H-E-B",  # Provides the intended purchase store.
        "description": "Generated valid coupon.",  # Provides a simple generated-test description.
        "via_rebate_flag": False,  # Marks the coupon as not rebate-based.
        "myw_exclusive": False,  # Marks the coupon as not MyWay exclusive.
        "online_only": False,  # Marks the coupon as not online-only.
        "on_card": True,  # Marks the coupon as clipped or loaded to card.
        "send_to_card": False,  # Leaves send-to-card false by default.
        "is_unlimited": False,  # Marks the coupon as not unlimited.
        "must_clip_before_checkout": True,  # Requires clipping before checkout.
        "must_scan_barcode_to_verify": True,  # Requires barcode scan verification.
        "verified_attaches_before_purchase": False,  # Marks the coupon as not verified before purchase.
        "raw_text": "Generated coupon text.",  # Stores fake source text for traceability.
        "source_type": "generated",  # Identifies the source as generated test data.
    }  # Ends the valid generated coupon dictionary.


@settings(max_examples=25)  # Limits generated examples so the test remains fast for local development.
@given(discount_amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100.00"), places=2))  # Generates valid dollar discount amounts.
def test_generated_valid_dollar_discount_amounts(discount_amount: Decimal) -> None:  # Tests many valid dollar coupon amounts.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["discount_type"] = "dollars"  # Sets the coupon discount type to dollars.
    coupon_data["discount_amount"] = discount_amount  # Uses the generated dollar discount amount.
    coupon_data["discount_percent"] = None  # Ensures dollar coupons do not include a percent discount.

    coupon = CouponModel(**coupon_data)  # Creates the coupon model from generated data.

    assert coupon.discount_type == "dollars"  # Confirms the generated coupon keeps the dollar discount type.
    assert coupon.discount_amount == discount_amount  # Confirms the generated dollar amount is stored correctly.
    assert coupon.discount_percent is None  # Confirms dollar coupons do not store a percent value.


@settings(max_examples=25)  # Limits generated examples so the test remains fast for local development.
@given(discount_percent=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100.00"), places=2))  # Generates valid percent discount values.
def test_generated_valid_percent_discount_values(discount_percent: Decimal) -> None:  # Tests many valid percent coupon values.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.MANUFACTURER  # Sets the coupon type to manufacturer.
    coupon_data["is_store_coupon"] = False  # Marks the generated coupon as not store-issued.
    coupon_data["is_manufacturer_coupon"] = True  # Marks the generated coupon as manufacturer-issued.
    coupon_data["discount_type"] = "percent"  # Sets the coupon discount type to percent.
    coupon_data["discount_amount"] = Decimal("0.00")  # Sets dollar amount to zero for percent coupons.
    coupon_data["discount_percent"] = discount_percent  # Uses the generated percent discount value.

    coupon = CouponModel(**coupon_data)  # Creates the coupon model from generated data.

    assert coupon.discount_type == "percent"  # Confirms the generated coupon keeps the percent discount type.
    assert coupon.discount_amount == Decimal("0.00")  # Confirms percent coupons do not store a dollar discount amount.
    assert coupon.discount_percent == discount_percent  # Confirms the generated percent value is stored correctly.


@settings(max_examples=25)  # Limits generated examples so the test remains fast for local development.
@given(required_purchase_amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("500.00"), places=2))  # Generates valid basket threshold amounts.
def test_generated_valid_basket_required_purchase_amounts(required_purchase_amount: Decimal) -> None:  # Tests many valid basket thresholds.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_scope"] = CouponScope.BASKET  # Sets the coupon scope to basket.
    coupon_data["item_name"] = "Generated Basket Coupon"  # Uses a basket-level item name label.
    coupon_data["required_purchase_amount"] = required_purchase_amount  # Uses the generated basket threshold.

    coupon = CouponModel(**coupon_data)  # Creates the coupon model from generated basket data.

    assert coupon.coupon_scope == CouponScope.BASKET  # Confirms the generated coupon is basket-scoped.
    assert coupon.required_purchase_amount == required_purchase_amount  # Confirms the generated basket threshold is stored correctly.


@settings(max_examples=25)  # Limits generated examples so the test remains fast for local development.
@given(required_purchase_quantity=st.integers(min_value=1, max_value=100))  # Generates valid required purchase quantities.
def test_generated_valid_required_purchase_quantities(required_purchase_quantity: int) -> None:  # Tests many valid required quantities.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["required_purchase_quantity"] = required_purchase_quantity  # Uses the generated required purchase quantity.

    coupon = CouponModel(**coupon_data)  # Creates the coupon model from generated quantity data.

    assert coupon.required_purchase_quantity == required_purchase_quantity  # Confirms the generated quantity is stored correctly.


@settings(max_examples=10)  # Limits generated examples because this test checks invalid values.
@given(required_purchase_quantity=st.integers(max_value=0))  # Generates invalid required purchase quantities.
def test_generated_rejects_invalid_required_purchase_quantities(required_purchase_quantity: int) -> None:  # Tests many invalid quantity values.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["required_purchase_quantity"] = required_purchase_quantity  # Uses the generated invalid quantity.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject invalid generated quantities.
        CouponModel(**coupon_data)  # Attempts to create a coupon with an invalid required quantity.


@settings(max_examples=10)  # Limits generated examples because this test checks invalid values.
@given(discount_amount=st.decimals(max_value=Decimal("0.00"), places=2))  # Generates invalid non-positive dollar amounts.
def test_generated_rejects_non_positive_dollar_discount_amounts(discount_amount: Decimal) -> None:  # Tests many invalid dollar amounts.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["discount_type"] = "dollars"  # Sets the coupon discount type to dollars.
    coupon_data["discount_amount"] = discount_amount  # Uses the generated invalid dollar amount.
    coupon_data["discount_percent"] = None  # Keeps percent discount empty for dollar coupons.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject non-positive dollar discount amounts.
        CouponModel(**coupon_data)  # Attempts to create a coupon with an invalid dollar amount.


@settings(max_examples=10)  # Limits generated examples because this test checks invalid values.
@given(discount_percent=st.one_of(st.decimals(max_value=Decimal("0.00"), places=2), st.decimals(min_value=Decimal("100.01"), max_value=Decimal("500.00"), places=2)))  # Generates invalid percent values.
def test_generated_rejects_invalid_percent_discount_values(discount_percent: Decimal) -> None:  # Tests many invalid percent values.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.MANUFACTURER  # Sets the coupon type to manufacturer.
    coupon_data["is_store_coupon"] = False  # Marks the generated coupon as not store-issued.
    coupon_data["is_manufacturer_coupon"] = True  # Marks the generated coupon as manufacturer-issued.
    coupon_data["discount_type"] = "percent"  # Sets the coupon discount type to percent.
    coupon_data["discount_amount"] = Decimal("0.00")  # Sets dollar amount to zero for percent coupons.
    coupon_data["discount_percent"] = discount_percent  # Uses the generated invalid percent value.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject invalid generated percent values.
        CouponModel(**coupon_data)  # Attempts to create a percent coupon with an invalid percent value.


def test_generated_rejects_expiration_date_before_coupon_date() -> None:  # Tests generated-file coverage for invalid date order.
    coupon_data = build_generated_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_date"] = date(2026, 6, 1)  # Sets the coupon start date after the expiration date.
    coupon_data["expiration_date"] = date(2026, 5, 31)  # Sets the expiration date before the coupon start date.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject invalid date ordering.
        CouponModel(**coupon_data)  # Attempts to create a coupon with invalid date order.
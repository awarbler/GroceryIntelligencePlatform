# =============================================================================
# File: test_purchase.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests PurchaseModel validation, financial field separation, and deal scenarios.
# Security Note: Tests use fake purchase data only and do not contain credentials or real payment data.
# SRS Traceability: Supports SRS v5.0 purchase tracking, coupon tracking, rebate tracking, and report input validation.
# SDD Traceability: Supports SDD v5.0 backend model validation and purchase document schema checks.
# =============================================================================

from __future__ import annotations  # Enables forward-compatible type annotations.

from datetime import date  # Imports date for fixed purchase test dates.
from decimal import Decimal  # Imports Decimal for exact money assertions.

import pytest  # Imports pytest for test assertions and exception checks.
from pydantic import (
    ValidationError,
)  # Imports ValidationError for model validation failure tests.

from backend.models.purchase import (
    CouponSource,
)  # Imports the coupon source enum under test.
from backend.models.purchase import InputType  # Imports the input type enum under test.
from backend.models.purchase import (
    PurchaseModel,
)  # Imports the purchase model under test.
from backend.models.rebate import (
    RebateStatus,
)  # Imports the rebate status enum used by purchases.


def valid_purchase_payload() -> dict[
    str, object
]:  # Builds a reusable valid Phase 1 purchase payload.
    return {  # Returns the baseline dictionary used by multiple tests.
        "store_ref": "507f1f77bcf86cd799439011",  # Provides a fake store ObjectId reference.
        "canonical_name": "Dove Body Wash",  # Provides a normalized product name.
        "raw_name": "DOVE BW 20OZ",  # Provides receipt item text.
        "category": "Personal Care",  # Provides the product category.
        "brand": "Dove",  # Provides the product brand.
        "size": "20 oz",  # Provides the product size.
        "quantity": 1,  # Provides the purchased quantity.
        "purchase_date": date(2026, 5, 14),  # Provides a fixed purchase date.
        "shelf_price": Decimal("8.99"),  # Provides the regular shelf price.
        "sale_price": Decimal("7.99"),  # Provides the sale price.
        "register_price": Decimal(
            "7.99"
        ),  # Provides the register price before register coupons.
        "subtotal_before_coupons": Decimal(
            "15.98"
        ),  # Provides a basket subtotal before coupons.
        "out_of_pocket": Decimal(
            "5.49"
        ),  # Provides the actual register payment after coupons.
        "coupon_used": True,  # Marks that a coupon was used.
        "coupon_source": CouponSource.HEB_DIGITAL,  # Provides the coupon source.
        "coupon_amount": Decimal("2.50"),  # Provides the coupon amount.
        "register_rewards_used": {
            "used": False,
            "amount": Decimal("0.00"),
        },  # Provides default Register Reward usage.
        "cvs_ecb_used": {
            "used": False,
            "amount": Decimal("0.00"),
        },  # Provides default CVS ECB usage.
        "rebate_company": None,  # Provides no rebate company for this baseline case.
        "rebate_amount": Decimal(
            "0.00"
        ),  # Provides no rebate amount for this baseline case.
        "rebate_status": None,  # Provides no rebate status for this baseline case.
        "source_type": InputType.MANUAL_ENTRY,  # Provides the input source type.
        "raw_input_ref": None,  # Provides no raw input reference for this baseline case.
        "parse_confidence": None,  # Provides no parser confidence for manual entry.
        "user_corrected": False,  # Marks that the user did not correct this record.
        "notes": "",  # Provides empty notes.
    }


def test_purchase_model_valid_phase1_payload() -> (
    None
):  # Verifies that the required Phase 1 payload is valid.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    purchase = PurchaseModel(**payload)  # Creates a PurchaseModel from the payload.
    assert (
        purchase.canonical_name == "Dove Body Wash"
    )  # Confirms the canonical name is stored.
    assert (
        purchase.source_type == InputType.MANUAL_ENTRY
    )  # Confirms the source type is stored.
    assert purchase.out_of_pocket == Decimal(
        "5.49"
    )  # Confirms the out-of-pocket amount is stored separately.


def test_purchase_has_separate_financial_fields() -> (
    None
):  # Verifies that key financial fields remain separate.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    purchase = PurchaseModel(**payload)  # Creates a PurchaseModel from the payload.
    assert purchase.shelf_price == Decimal(
        "8.99"
    )  # Confirms shelf price is stored separately.
    assert purchase.sale_price == Decimal(
        "7.99"
    )  # Confirms sale price is stored separately.
    assert purchase.register_price == Decimal(
        "7.99"
    )  # Confirms register price is stored separately.
    assert purchase.out_of_pocket == Decimal(
        "5.49"
    )  # Confirms out-of-pocket is stored separately.


def test_purchase_rejects_combined_financial_field() -> (
    None
):  # Verifies that final cost after rebates is not stored.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    payload["final_cost_after_rebates"] = Decimal(
        "0.49"
    )  # Adds a forbidden report-level calculated field.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a PurchaseModel with an extra field.


def test_purchase_future_reward_fields_optional() -> (
    None
):  # Verifies that future reward fields are not required in Phase 1.
    payload = (
        valid_purchase_payload()
    )  # Builds a valid purchase payload without future reward fields.
    purchase = PurchaseModel(
        **payload
    )  # Creates a PurchaseModel from the Phase 1 payload.
    assert (
        purchase.walgreens_cash_redeemed is None
    )  # Confirms Walgreens Cash redeemed is optional.
    assert (
        purchase.walmart_cash_earned is None
    )  # Confirms Walmart Cash earned is optional.
    assert purchase.ecb_earned is None  # Confirms CVS ECB earned is optional.


def test_purchase_future_reward_fields_accept_values() -> (
    None
):  # Verifies that future reward fields accept valid values.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    payload["walgreens_cash_redeemed"] = Decimal(
        "5.00"
    )  # Adds Walgreens Cash redeemed.
    payload["walgreens_cash_earned"] = Decimal("3.00")  # Adds Walgreens Cash earned.
    payload["rr_used_amount"] = Decimal("4.00")  # Adds Register Rewards used amount.
    payload["rr_earned_amount"] = Decimal(
        "5.00"
    )  # Adds Register Rewards earned amount.
    payload["walmart_cash_earned"] = Decimal("1.25")  # Adds Walmart Cash earned.
    payload["walmart_cash_used"] = Decimal("2.00")  # Adds Walmart Cash used.
    payload["ecb_earned"] = Decimal("6.00")  # Adds CVS ECB earned.
    payload["ecb_used"] = Decimal("4.00")  # Adds CVS ECB used.
    purchase = PurchaseModel(
        **payload
    )  # Creates a PurchaseModel with optional reward values.
    assert purchase.walgreens_cash_redeemed == Decimal(
        "5.00"
    )  # Confirms Walgreens Cash redeemed is stored.
    assert purchase.rr_earned_amount == Decimal(
        "5.00"
    )  # Confirms Register Rewards earned amount is stored.
    assert purchase.ecb_used == Decimal("4.00")  # Confirms CVS ECB used is stored.


def test_purchase_missing_shelf_price_fails() -> (
    None
):  # Verifies that shelf_price is required.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    del payload["shelf_price"]  # Removes the required shelf price.
    with pytest.raises(ValidationError):  # Expects validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a PurchaseModel without shelf_price.


def test_purchase_missing_register_price_fails() -> (
    None
):  # Verifies that register_price is required.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    del payload["register_price"]  # Removes the required register price.
    with pytest.raises(ValidationError):  # Expects validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a PurchaseModel without register_price.


def test_purchase_missing_out_of_pocket_fails() -> (
    None
):  # Verifies that out_of_pocket is required.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    del payload["out_of_pocket"]  # Removes the required out-of-pocket value.
    with pytest.raises(ValidationError):  # Expects validation to fail.
        PurchaseModel(
            **payload
        )  # Attempts to create a PurchaseModel without out_of_pocket.


def test_claritin_deal_scenario() -> (
    None
):  # Verifies rebate amount does not change out-of-pocket amount.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    payload["canonical_name"] = "Claritin Allergy Tablets"  # Sets the deal item name.
    payload["raw_name"] = "CLARITIN 10CT"  # Sets the receipt text.
    payload["category"] = "Medicine"  # Sets the product category.
    payload["brand"] = "Claritin"  # Sets the product brand.
    payload["size"] = "10 ct"  # Sets the product size.
    payload["shelf_price"] = Decimal("12.97")  # Sets the regular shelf price.
    payload["sale_price"] = Decimal("9.97")  # Sets the sale price.
    payload["register_price"] = Decimal(
        "9.97"
    )  # Sets the register price before register coupons.
    payload["subtotal_before_coupons"] = Decimal(
        "9.97"
    )  # Sets the subtotal before coupons.
    payload["out_of_pocket"] = Decimal("9.97")  # Sets the actual register payment.
    payload["coupon_used"] = False  # Marks that no coupon was used.
    payload["coupon_source"] = None  # Clears the coupon source.
    payload["coupon_amount"] = Decimal("0.00")  # Clears the coupon amount.
    payload["rebate_company"] = "Ibotta"  # Sets the rebate company.
    payload["rebate_amount"] = Decimal("5.00")  # Sets the rebate amount.
    payload["rebate_status"] = RebateStatus.PENDING  # Sets the rebate status.
    purchase = PurchaseModel(**payload)  # Creates the Claritin purchase model.
    assert purchase.out_of_pocket == Decimal(
        "9.97"
    )  # Confirms register payment stays 9.97.
    assert purchase.rebate_amount == Decimal(
        "5.00"
    )  # Confirms the rebate is stored separately.
    assert purchase.out_of_pocket != Decimal(
        "4.97"
    )  # Confirms out-of-pocket is not reduced by rebate.


def test_dove_basket_coupon_scenario() -> (
    None
):  # Verifies basket subtotal supports a basket coupon scenario.
    payload = valid_purchase_payload()  # Builds a valid purchase payload.
    payload["canonical_name"] = "Dove Body Wash Bundle"  # Sets the deal item name.
    payload["raw_name"] = "DOVE BODY WASH MULTI"  # Sets the receipt text.
    payload["category"] = "Personal Care"  # Sets the product category.
    payload["brand"] = "Dove"  # Sets the product brand.
    payload["size"] = "2 items"  # Sets the deal size description.
    payload["quantity"] = 2  # Sets the quantity to two items.
    payload["shelf_price"] = Decimal("17.98")  # Sets the regular shelf total.
    payload["sale_price"] = Decimal("15.98")  # Sets the sale total.
    payload["register_price"] = Decimal(
        "15.98"
    )  # Sets the register total before register coupons.
    payload["subtotal_before_coupons"] = Decimal(
        "15.98"
    )  # Sets the basket subtotal before coupons.
    payload["out_of_pocket"] = Decimal(
        "10.98"
    )  # Sets the payment after a five-dollar basket coupon.
    payload["coupon_used"] = True  # Marks that a coupon was used.
    payload["coupon_source"] = CouponSource.HEB_DIGITAL  # Sets the coupon source.
    payload["coupon_amount"] = Decimal("5.00")  # Sets the basket coupon amount.
    purchase = PurchaseModel(
        **payload
    )  # Creates the Dove basket coupon purchase model.
    assert purchase.subtotal_before_coupons >= Decimal(
        "15.00"
    )  # Confirms basket threshold is met.
    assert purchase.coupon_amount == Decimal(
        "5.00"
    )  # Confirms the basket coupon value is stored.
    assert purchase.out_of_pocket == Decimal(
        "10.98"
    )  # Confirms out-of-pocket is after register coupons.

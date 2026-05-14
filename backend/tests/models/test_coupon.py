# =============================================================================
# File: test_coupon.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests the CouponModel validation rules using fixed examples for item, basket, percent, unlimited, and workflow coupon cases.
# Security Note: Tests use generated fake coupon values only and do not contain secrets, payment data, or personal customer information.
# SRS Traceability: Supports SRS v5.0 P1-04 coupon model validation, required expiration dates, coupon flags, and H-E-B coupon workflow fields.
# SDD Traceability: Supports SDD v5.0 backend model validation and automated test coverage for coupon data models.
# =============================================================================

from datetime import date  # Imports the date type for coupon dates and expiration dates.
from decimal import Decimal  # Imports Decimal for exact coupon dollar and percentage values.

import pytest  # Imports pytest for assertions and exception testing.
from bson import ObjectId  # Imports ObjectId to create realistic MongoDB store references.
from pydantic import ValidationError  # Imports ValidationError to confirm invalid coupon data fails.

from backend.models.coupon import CouponModel, CouponScope, CouponType  # Imports the coupon model and enums being tested.


def build_valid_coupon_data() -> dict:  # Defines a reusable valid coupon payload for the test cases.
    """Return valid base coupon data that individual tests can override."""  # Explains the helper purpose.

    return {  # Starts the valid coupon dictionary.
        "store_ref": ObjectId(),  # Provides a realistic MongoDB ObjectId for the related store.
        "coupon_type": CouponType.STORE_DIGITAL,  # Uses a valid store digital coupon type.
        "coupon_scope": CouponScope.ITEM,  # Uses an item-level coupon scope.
        "is_store_coupon": True,  # Marks the coupon as store-issued.
        "store_name": "H-E-B",  # Provides the store display name.
        "is_manufacturer_coupon": False,  # Marks the coupon as not manufacturer-issued.
        "coupon_date": date(2026, 5, 1),  # Provides the coupon availability date.
        "expiration_date": date(2026, 5, 31),  # Provides the required expiration date.
        "item_name": "H-E-B Greek Yogurt",  # Provides the qualifying item name.
        "item_size": "5.3 oz",  # Provides the qualifying item size.
        "brand": "H-E-B",  # Provides the qualifying brand.
        "discount_amount": Decimal("1.00"),  # Provides a one-dollar discount amount.
        "discount_percent": None,  # Leaves percent discount empty for a dollar coupon.
        "discount_type": "dollars",  # Identifies the coupon as a dollar discount.
        "required_purchase_quantity": 1,  # Requires one qualifying item.
        "required_purchase_amount": None,  # Leaves basket threshold empty for an item coupon.
        "store_purchased": "H-E-B",  # Provides the intended purchase store.
        "description": "Save $1.00 on one H-E-B Greek Yogurt.",  # Provides a readable coupon description.
        "via_rebate_flag": False,  # Marks the coupon as not rebate-based.
        "myw_exclusive": False,  # Marks the coupon as not MyWay exclusive.
        "online_only": False,  # Marks the coupon as not online-only.
        "on_card": True,  # Marks the coupon as clipped or loaded to card.
        "send_to_card": False,  # Keeps send-to-card false because the coupon is already represented as on card.
        "is_unlimited": False,  # Marks the coupon as not unlimited.
        "must_clip_before_checkout": True,  # Requires clipping before checkout.
        "must_scan_barcode_to_verify": True,  # Requires barcode scan verification.
        "verified_attaches_before_purchase": False,  # Marks the coupon as not yet verified before purchase.
        "raw_text": "Save $1.00 on one H-E-B Greek Yogurt 5.3 oz.",  # Stores the original coupon text.
        "source_type": "app",  # Identifies the coupon source as app data.
    }  # Ends the valid coupon dictionary.


def test_coupon_model_valid() -> None:  # Tests that a complete valid coupon can be created.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.

    coupon = CouponModel(**coupon_data)  # Creates the coupon model from the valid payload.

    assert coupon.coupon_type == CouponType.STORE_DIGITAL  # Confirms the coupon type is stored correctly.
    assert coupon.coupon_scope == CouponScope.ITEM  # Confirms the coupon scope is stored correctly.
    assert coupon.expiration_date == date(2026, 5, 31)  # Confirms the required expiration date is stored correctly.
    assert coupon.item_name == "H-E-B Greek Yogurt"  # Confirms the item name is stored correctly.
    assert coupon.discount_amount == Decimal("1.00")  # Confirms the dollar discount is stored correctly.


def test_coupon_requires_expiration_date() -> None:  # Tests that missing expiration_date fails validation.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data.pop("expiration_date")  # Removes the required expiration date field.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject the missing required field.
        CouponModel(**coupon_data)  # Attempts to create an invalid coupon without an expiration date.


def test_coupon_rejects_none_expiration_date() -> None:  # Tests that expiration_date cannot be None.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["expiration_date"] = None  # Sets the required expiration date to an invalid None value.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject None for a required date field.
        CouponModel(**coupon_data)  # Attempts to create an invalid coupon with a None expiration date.


def test_coupon_basket_scope_valid() -> None:  # Tests that a basket coupon can store a required purchase amount.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_scope"] = CouponScope.BASKET  # Changes the coupon to basket scope.
    coupon_data["item_name"] = "Basket Coupon"  # Uses a basket-level item name label.
    coupon_data["discount_amount"] = Decimal("5.00")  # Sets a five-dollar basket discount.
    coupon_data["required_purchase_quantity"] = 1  # Keeps quantity requirement at one basket or order.
    coupon_data["required_purchase_amount"] = Decimal("30.00")  # Requires a thirty-dollar basket threshold.
    coupon_data["description"] = "Save $5.00 on your basket when you spend $30.00."  # Describes the basket coupon.

    coupon = CouponModel(**coupon_data)  # Creates the basket coupon model.

    assert coupon.coupon_scope == CouponScope.BASKET  # Confirms the coupon is basket-scoped.
    assert coupon.required_purchase_amount == Decimal("30.00")  # Confirms the basket threshold is stored correctly.
    assert coupon.discount_amount == Decimal("5.00")  # Confirms the basket discount amount is stored correctly.


def test_coupon_percent_discount_valid() -> None:  # Tests that a percent discount coupon can be created.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.MANUFACTURER  # Changes the coupon to a manufacturer coupon.
    coupon_data["is_store_coupon"] = False  # Marks the coupon as not store-issued.
    coupon_data["is_manufacturer_coupon"] = True  # Marks the coupon as manufacturer-issued.
    coupon_data["item_name"] = "Blue Buffalo Dog Food"  # Uses the Blue Buffalo item name.
    coupon_data["brand"] = "Blue Buffalo"  # Uses the Blue Buffalo brand.
    coupon_data["discount_amount"] = Decimal("0.00")  # Uses zero dollar discount because the discount is percentage-based.
    coupon_data["discount_percent"] = Decimal("20")  # Sets the percent discount to twenty percent.
    coupon_data["discount_type"] = "percent"  # Identifies the coupon as a percent discount.
    coupon_data["description"] = "Save 20% on Blue Buffalo Dog Food."  # Describes the percent discount coupon.

    coupon = CouponModel(**coupon_data)  # Creates the percent discount coupon model.

    assert coupon.coupon_type == CouponType.MANUFACTURER  # Confirms the manufacturer coupon type is stored correctly.
    assert coupon.is_manufacturer_coupon is True  # Confirms the manufacturer flag is true.
    assert coupon.discount_percent == Decimal("20")  # Confirms the percent discount is stored correctly.
    assert coupon.discount_type == "percent"  # Confirms the discount type is stored correctly.


def test_coupon_unlimited_flag_valid() -> None:  # Tests that an unlimited coupon can be represented.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.APP_ONLY  # Changes the coupon to an app-only coupon.
    coupon_data["item_name"] = "Bic Razors"  # Uses a Bic-style item example.
    coupon_data["brand"] = "Bic"  # Uses Bic as the brand.
    coupon_data["online_only"] = True  # Marks the app-only coupon as online or app restricted.
    coupon_data["is_unlimited"] = True  # Marks the coupon as unlimited.
    coupon_data["description"] = "App-only unlimited Bic coupon."  # Describes the unlimited coupon.

    coupon = CouponModel(**coupon_data)  # Creates the unlimited coupon model.

    assert coupon.coupon_type == CouponType.APP_ONLY  # Confirms the app-only coupon type is stored correctly.
    assert coupon.online_only is True  # Confirms the online-only flag is stored correctly.
    assert coupon.is_unlimited is True  # Confirms the unlimited flag is stored correctly.
    assert coupon.brand == "Bic"  # Confirms the brand is stored correctly.


def test_coupon_workflow_fields_valid() -> None:  # Tests H-E-B-style clip, scan, and verification workflow fields.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["must_clip_before_checkout"] = True  # Requires the coupon to be clipped before checkout.
    coupon_data["must_scan_barcode_to_verify"] = True  # Requires barcode scanning for verification.
    coupon_data["verified_attaches_before_purchase"] = True  # Marks the coupon as verified before purchase.
    coupon_data["on_card"] = True  # Marks the coupon as already clipped or loaded.
    coupon_data["send_to_card"] = True  # Marks the coupon as supporting send-to-card behavior.
    coupon_data["source_type"] = "manual"  # Marks the test coupon as manually entered.

    coupon = CouponModel(**coupon_data)  # Creates the workflow coupon model.

    assert coupon.must_clip_before_checkout is True  # Confirms clip-before-checkout behavior is stored correctly.
    assert coupon.must_scan_barcode_to_verify is True  # Confirms barcode verification behavior is stored correctly.
    assert coupon.verified_attaches_before_purchase is True  # Confirms pre-purchase verification is stored correctly.
    assert coupon.on_card is True  # Confirms on-card status is stored correctly.
    assert coupon.send_to_card is True  # Confirms send-to-card support is stored correctly.


def test_coupon_rejects_expiration_before_coupon_date() -> None:  # Tests that coupons cannot expire before they become available.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_date"] = date(2026, 6, 1)  # Sets the coupon availability date after the expiration date.
    coupon_data["expiration_date"] = date(2026, 5, 31)  # Sets the expiration date before the coupon date.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject the invalid date order.
        CouponModel(**coupon_data)  # Attempts to create a coupon with an expiration date before the coupon date.


def test_coupon_rejects_invalid_discount_type() -> None:  # Tests that unsupported discount_type values fail validation.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["discount_type"] = "free"  # Sets an invalid discount type.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject the invalid discount type.
        CouponModel(**coupon_data)  # Attempts to create a coupon with an unsupported discount type.


def test_coupon_rejects_percent_discount_without_percent_value() -> None:  # Tests that percent coupons require discount_percent.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["discount_type"] = "percent"  # Sets the coupon discount type to percent.
    coupon_data["discount_amount"] = Decimal("0.00")  # Sets the dollar discount amount to zero for a percent coupon.
    coupon_data["discount_percent"] = None  # Removes the required percent value.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject a percent coupon without a percent value.
        CouponModel(**coupon_data)  # Attempts to create an invalid percent coupon.


def test_coupon_rejects_percent_discount_with_dollar_amount() -> None:  # Tests that percent coupons cannot also include a dollar discount amount.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["discount_type"] = "percent"  # Sets the coupon discount type to percent.
    coupon_data["discount_amount"] = Decimal("1.00")  # Sets an invalid dollar amount on a percent coupon.
    coupon_data["discount_percent"] = Decimal("20")  # Provides a valid percent value.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject mixed percent and dollar data.
        CouponModel(**coupon_data)  # Attempts to create an invalid mixed discount coupon.


def test_coupon_rejects_dollar_discount_with_percent_value() -> None:  # Tests that dollar coupons cannot also include a percent discount value.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["discount_type"] = "dollars"  # Sets the coupon discount type to dollars.
    coupon_data["discount_amount"] = Decimal("1.00")  # Provides a valid dollar discount amount.
    coupon_data["discount_percent"] = Decimal("10")  # Adds an invalid percent value to a dollar coupon.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject mixed dollar and percent data.
        CouponModel(**coupon_data)  # Attempts to create an invalid mixed discount coupon.


def test_coupon_rejects_basket_scope_without_required_purchase_amount() -> None:  # Tests that basket coupons require a spending threshold.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_scope"] = CouponScope.BASKET  # Sets the coupon scope to basket.
    coupon_data["required_purchase_amount"] = None  # Removes the required basket purchase amount.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject a basket coupon without a basket amount.
        CouponModel(**coupon_data)  # Attempts to create an invalid basket coupon.


def test_coupon_rejects_non_positive_required_purchase_amount() -> None:  # Tests that required purchase amount must be greater than zero when provided.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_scope"] = CouponScope.BASKET  # Sets the coupon scope to basket.
    coupon_data["required_purchase_amount"] = Decimal("0.00")  # Sets an invalid zero-dollar basket threshold.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject the non-positive basket amount.
        CouponModel(**coupon_data)  # Attempts to create an invalid basket coupon.


def test_coupon_rejects_manufacturer_type_with_store_flags() -> None:  # Tests that manufacturer coupon flags must match the manufacturer coupon type.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.MANUFACTURER  # Sets the coupon type to manufacturer.
    coupon_data["is_store_coupon"] = True  # Leaves the store coupon flag incorrectly set to true.
    coupon_data["is_manufacturer_coupon"] = False  # Leaves the manufacturer coupon flag incorrectly set to false.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject conflicting coupon source flags.
        CouponModel(**coupon_data)  # Attempts to create an invalid manufacturer coupon.


def test_coupon_rejects_store_digital_type_with_manufacturer_flag() -> None:  # Tests that store digital coupons cannot be marked as manufacturer coupons.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.STORE_DIGITAL  # Sets the coupon type to store digital.
    coupon_data["is_store_coupon"] = True  # Keeps the store coupon flag true.
    coupon_data["is_manufacturer_coupon"] = True  # Incorrectly marks the coupon as manufacturer-issued.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject conflicting source flags.
        CouponModel(**coupon_data)  # Attempts to create an invalid store digital coupon.


def test_coupon_myw_exclusive_type_requires_myw_flag() -> None:  # Tests that MYW_EXCLUSIVE type requires the myw_exclusive flag.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.MYW_EXCLUSIVE  # Sets the coupon type to MYW_EXCLUSIVE.
    coupon_data["myw_exclusive"] = False  # Leaves the MyWay flag incorrectly false.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject inconsistent MyWay data.
        CouponModel(**coupon_data)  # Attempts to create an invalid MyWay exclusive coupon.


def test_coupon_app_only_type_requires_online_only_flag() -> None:  # Tests that APP_ONLY type requires the online_only flag.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.APP_ONLY  # Sets the coupon type to APP_ONLY.
    coupon_data["online_only"] = False  # Leaves the online-only flag incorrectly false.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject inconsistent app-only data.
        CouponModel(**coupon_data)  # Attempts to create an invalid app-only coupon.


def test_coupon_paper_type_requires_barcode_verification() -> None:  # Tests that paper coupons require barcode verification.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_type"] = CouponType.PAPER  # Sets the coupon type to paper.
    coupon_data["must_scan_barcode_to_verify"] = False  # Incorrectly disables barcode verification.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject paper coupons without barcode verification.
        CouponModel(**coupon_data)  # Attempts to create an invalid paper coupon.


def test_coupon_rebate_scope_requires_rebate_flag() -> None:  # Tests that rebate scope requires the rebate workflow flag.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["coupon_scope"] = CouponScope.REBATE  # Sets the coupon scope to rebate.
    coupon_data["via_rebate_flag"] = False  # Leaves the rebate workflow flag incorrectly false.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject inconsistent rebate data.
        CouponModel(**coupon_data)  # Attempts to create an invalid rebate-scope coupon.


def test_coupon_rejects_verified_attachment_without_on_card() -> None:  # Tests that verified attachment requires the coupon to be on card.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["verified_attaches_before_purchase"] = True  # Marks the coupon as verified before purchase.
    coupon_data["on_card"] = False  # Creates an invalid state where the coupon is verified but not on card.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject the invalid workflow state.
        CouponModel(**coupon_data)  # Attempts to create an invalid workflow coupon.


def test_coupon_rejects_send_to_card_without_on_card() -> None:  # Tests that send_to_card requires the coupon to be on card.
    coupon_data = build_valid_coupon_data()  # Builds a valid coupon payload.
    coupon_data["send_to_card"] = True  # Marks the coupon as sent to card.
    coupon_data["on_card"] = False  # Creates an invalid state where the coupon is sent but not on card.

    with pytest.raises(ValidationError):  # Expects Pydantic to reject the invalid send-to-card state.
        CouponModel(**coupon_data)  # Attempts to create an invalid send-to-card coupon.
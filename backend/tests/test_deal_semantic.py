# =============================================================================
# File: backend/tests/test_deal_semantic.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Tests deal semantic classification for H-E-B weekly ad text.
# Security Note: Tests use synthetic ad text only and contain no personal data.
# SRS Traceability: Supports SRS v5.0 Section 7 AD-001 through AD-010.
# SDD Traceability: Supports SDD v5.0 parser testability and ads collection design.
# =============================================================================

from backend.models.ad import DealType  # Imports expected enum values for assertions.
from backend.parsers.deal_semantic import classify_deal_type  # Imports the classifier under test.
from backend.parsers.deal_semantic import normalize_deal_text  # Imports text normalization helper.


def test_normalize_deal_text_handles_none() -> None:  # Tests safe handling of missing input.
    result: str = normalize_deal_text(None)  # Calls normalizer with None.
    assert result == ""  # Verifies missing text becomes an empty string.


def test_normalize_deal_text_lowercases_and_collapses_spaces() -> None:  # Tests text cleanup behavior.
    result: str = normalize_deal_text("  Save   $2   OFF  ")  # Calls normalizer with mixed spacing and case.
    assert result == "save $2 off"  # Verifies lowercase normalized output.


def test_classify_empty_text_as_standard() -> None:  # Tests default behavior for empty input.
    result: DealType = classify_deal_type("")  # Classifies empty text.
    assert result == DealType.STANDARD  # Verifies safe default classification.


def test_classify_standard_sale_text() -> None:  # Tests ordinary weekly ad sale text.
    result: DealType = classify_deal_type("H-E-B Grapes Sale $1.67 lb")  # Classifies normal sale wording.
    assert result == DealType.STANDARD  # Verifies ordinary sale maps to STANDARD.


def test_classify_coupon_marker_as_digital_coupon() -> None:  # Tests H-E-B coupon marker wording.
    result: DealType = classify_deal_type("Coupon")  # Classifies standalone coupon marker.
    assert result == DealType.DIGITAL_COUPON  # Verifies Coupon maps to DIGITAL_COUPON.


def test_classify_digital_coupon_text() -> None:  # Tests explicit digital coupon wording.
    result: DealType = classify_deal_type("Clip digital coupon for this item")  # Classifies digital coupon wording.
    assert result == DealType.DIGITAL_COUPON  # Verifies digital coupon classification.


def test_classify_bogo_text() -> None:  # Tests direct BOGO wording.
    result: DealType = classify_deal_type("Buy 1 get 1 free")  # Classifies numeric BOGO wording.
    assert result == DealType.BOGO  # Verifies BOGO classification.


def test_classify_buy_x_get_y_text() -> None:  # Tests numeric buy-X-get-Y wording.
    result: DealType = classify_deal_type("Buy 4 get 4 free")  # Classifies buy-X-get-Y wording.
    assert result == DealType.BUY_X_GET_Y  # Verifies Buy X Get Y classification.


def test_classify_combo_loco_text() -> None:  # Tests H-E-B Combo Loco wording.
    result: DealType = classify_deal_type("Combo Loco buy fajitas get tortillas free")  # Classifies Combo Loco wording.
    assert result == DealType.COMBO_LOCO  # Verifies Combo Loco classification.


def test_classify_percent_off_text() -> None:  # Tests percentage discount wording.
    result: DealType = classify_deal_type("Save 25% off select items")  # Classifies percent-off wording.
    assert result == DealType.PERCENT_OFF  # Verifies percent-off classification.


def test_classify_price_off_text() -> None:  # Tests fixed dollar discount wording.
    result: DealType = classify_deal_type("Save $2 on this item")  # Classifies fixed-dollar savings wording.
    assert result == DealType.PRICE_OFF  # Verifies price-off classification.


def test_classify_basket_coupon_text() -> None:  # Tests basket threshold coupon wording.
    result: DealType = classify_deal_type("$2 off $12 select items")  # Classifies basket threshold wording.
    assert result == DealType.BASKET_COUPON  # Verifies basket coupon classification.


def test_basket_coupon_takes_priority_over_price_off() -> None:  # Tests classification priority order.
    result: DealType = classify_deal_type("$2 off $12 H-E-B Texas Tough Bags")  # Classifies text containing both "$ off" and threshold.
    assert result == DealType.BASKET_COUPON  # Verifies threshold coupon wins over PRICE_OFF.


def test_combo_loco_takes_priority_over_free_item() -> None:  # Tests Combo Loco priority order.
    result: DealType = classify_deal_type("Combo Loco get tortillas free")  # Classifies text containing Combo Loco and free wording.
    assert result == DealType.COMBO_LOCO  # Verifies Combo Loco wins over FREE_ITEM.
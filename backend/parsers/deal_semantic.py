# =============================================================================
# File: backend/parsers/deal_semantic.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Classify grocery ad text into supported deal semantic categories.
# Security Note: This file processes public ad text only and must not store secrets.
# SRS Traceability: Supports SRS v5.0 Section 7 AD-001 through AD-010.
# SDD Traceability: Supports SDD v5.0 Section 5.1 parser design and Section 7.5 ads collection.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations without runtime forward-reference issues.

import re  # Provides regular expression matching for deal text patterns.

from backend.models.ad import DealType  # Imports the shared approved deal type enum.

def normalize_deal_text(text: str) -> str:
    """Return lower case searchable deal text"""
    # handle missing text 
    if text is None: 
        return ""
    return " ".join(text.lower().split())
    
def classify_deal_type(text: str | None) -> DealType:
    """ Classify a grocery ad line or block into a dealType value"""
    normalized_text = normalize_deal_text(text)
    
    if not normalized_text:
        return DealType.STANDARD
    
    # checks basket level threshold coupon wording
    if _matches_basket_coupon(normalized_text):
        return DealType.BASKET_COUPON
    # check heb combo loco wording 
    if _matches_combo_loco(normalized_text):
        return DealType.COMBO_LOCO
    # checks buy one get one wording 
    if _matches_bogo(normalized_text):
        return DealType.BOGO
    # check buy x get y wording 
    if _matches_buy_x_get_y(normalized_text):
        return DealType.BUY_X_GET_Y
    # checks percentage discount wording
    if _matches_percent_off(normalized_text):
        return DealType.PERCENT_OFF
    # checks fixed dollar discount wording
    if _matches_price_off(normalized_text):
        return DealType.PRICE_OFF
    # check free item wording after bogo and by x get y to avoid misclassifying those as free item deals
    if _matches_free_item(normalized_text):
        return DealType.FREE_ITEM
    # checks heb coupon marker wording 
    if _matches_digital_coupon(normalized_text):
        return DealType.DIGITAL_COUPON
    return DealType.STANDARD

def _matches_basket_coupon(text: str) -> bool:  # Defines basket coupon pattern detection.
    return bool(  # Converts regex match result into a boolean.
        re.search(  # Searches for threshold-style basket coupon language.
            r"\$\d+(?:\.\d{2})?\s+off\s+\$\d+(?:\.\d{2})?",  # Matches wording like "$2 off $12".
            text,  # Searches the normalized text.
        )  # Ends regex search.
    )  # Returns whether the basket coupon pattern matched.

def _matches_combo_loco(text: str) -> bool:  # Defines Combo Loco pattern detection.
    return "combo loco" in text  # Detects H-E-B Combo Loco wording.


def _matches_bogo(text: str) -> bool:  # Defines BOGO pattern detection.
    return bool(  # Converts any matching condition into a boolean.
        "bogo" in text  # Detects direct BOGO wording.
        or "buy one get one" in text  # Detects spelled-out BOGO wording.
        or "buy 1 get 1" in text  # Detects numeric BOGO wording.
    )  # Returns whether BOGO wording matched.


def _matches_buy_x_get_y(text: str) -> bool:  # Defines Buy X Get Y pattern detection.
    return bool(  # Converts regex match result into a boolean.
        re.search(  # Searches for numeric buy/get wording.
            r"buy\s+\d+\s+get\s+\d+",  # Matches wording like "buy 4 get 4".
            text,  # Searches the normalized text.
        )  # Ends regex search.
    )  # Returns whether Buy X Get Y wording matched.


def _matches_percent_off(text: str) -> bool:  # Defines percent-off pattern detection.
    return bool(  # Converts regex match result into a boolean.
        re.search(  # Searches for percentage discount language.
            r"\d+(?:\.\d+)?\s*%\s*off",  # Matches wording like "25% off".
            text,  # Searches the normalized text.
        )  # Ends regex search.
    )  # Returns whether percent-off wording matched.


def _matches_price_off(text: str) -> bool:  # Defines fixed-price discount pattern detection.
    return bool(  # Converts any matching condition into a boolean.
        re.search(  # Searches for fixed dollar off language.
            r"\$\d+(?:\.\d{2})?\s+off",  # Matches wording like "$2 off".
            text,  # Searches the normalized text.
        )  # Ends regex search.
        or re.search(  # Searches for save dollar language.
            r"save\s+\$\d+(?:\.\d{2})?",  # Matches wording like "save $2".
            text,  # Searches the normalized text.
        )  # Ends regex search.
    )  # Returns whether fixed-price discount wording matched.


def _matches_free_item(text: str) -> bool:  # Defines free-item pattern detection.
    return bool(  # Converts any matching condition into a boolean.
        "free item" in text  # Detects direct free item wording.
        or "free items" in text  # Detects plural free items wording.
        or re.search(  # Searches for general get-free wording.
            r"get\s+.+\s+free",  # Matches wording like "get tortillas free".
            text,  # Searches the normalized text.
        )  # Ends regex search.
    )  # Returns whether free-item wording matched.


def _matches_digital_coupon(text: str) -> bool:  # Defines digital coupon pattern detection.
    return bool(  # Converts any matching condition into a boolean.
        text == "coupon"  # Detects a standalone H-E-B coupon marker.
        or "digital coupon" in text  # Detects explicit digital coupon wording.
        or "coupon" in text  # Detects coupon wording inside an ad block.
    )  # Returns whether coupon wording matched.
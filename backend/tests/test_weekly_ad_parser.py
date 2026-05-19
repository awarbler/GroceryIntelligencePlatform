# =============================================================================
# File: backend/tests/test_weekly_ad_parser.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Tests H-E-B weekly ad parser behavior.
# Security Note: Tests use synthetic public-style ad text only.
# SRS Traceability: Supports SRS v5.0 Section 7 AD-001 through AD-010.
# SDD Traceability: Supports SDD v5.0 parser testability.
# =============================================================================

from datetime import date  # Supports expected date assertions.
from decimal import Decimal  # Supports money assertions.

from backend.models.ad import DealType  # Imports expected deal type enum.
from backend.parsers.heb.weekly_ad_parser import parse_heb_weekly_ad  # Imports parser under test.


def test_parse_weekly_ad_sale_item() -> None:  # Tests standard sale item parsing.
    raw_lines: list[str] = [  # Creates synthetic H-E-B ad block.
        "H-E-B Red Seedless Grapes",  # Item name.
        "Sale",  # Sale marker.
        "$2.98",  # Regular price.
        "$1.67",  # Sale price.
        "lb",  # Unit.
        "H-E-B Red Seedless Grapes, per lb",  # Size line.
        "Add to cart, H-E-B Red Seedless Grapes",  # Block sentinel.
    ]
    result = parse_heb_weekly_ad(raw_lines, "heb_weekly_ad", "HEB", date(2026, 5, 13), date(2026, 5, 19))  # Parses ad text.
    assert len(result.items) == 1  # Verifies one item parsed.
    assert result.items[0].item_name == "H-E-B Red Seedless Grapes"  # Verifies item name.
    assert result.items[0].sale_price == Decimal("1.67")  # Verifies sale price.
    assert result.items[0].regular_price == Decimal("2.98")  # Verifies regular price.
    assert result.items[0].deal_type == DealType.STANDARD  # Verifies sale classification.


def test_parse_weekly_ad_coupon_item() -> None:  # Tests coupon marker parsing.
    raw_lines: list[str] = [  # Creates coupon ad block.
        "Cheez-It Original Cheese Crackers",  # Item name.
        "Coupon",  # Coupon marker.
        "$5.97",  # Sale price.
        "each",  # Unit.
        "Add to cart, Cheez-It Original Cheese Crackers",  # Block sentinel.
    ]
    result = parse_heb_weekly_ad(raw_lines, "heb_weekly_ad", "HEB", date(2026, 5, 13), date(2026, 5, 19))  # Parses ad text.
    assert result.items[0].deal_type == DealType.DIGITAL_COUPON  # Verifies coupon maps to digital coupon.


def test_parse_weekly_ad_multi_unit_price() -> None:  # Tests 2-for pricing.
    raw_lines: list[str] = [  # Creates multi-unit ad block.
        "H-E-B Premium Pork Breakfast Sausage",  # Item name.
        "Sale",  # Sale marker.
        "$3.99",  # Regular price.
        "2 for 7.00",  # Multi-unit price.
        "Add to cart, H-E-B Premium Pork Breakfast Sausage",  # Block sentinel.
    ]
    result = parse_heb_weekly_ad(raw_lines, "heb_weekly_ad", "HEB", date(2026, 5, 13), date(2026, 5, 19))  # Parses ad text.
    assert result.items[0].sale_price == Decimal("3.50")  # Verifies unit price from 2 for 7.00.


def test_parse_weekly_ad_date_range_from_text() -> None:  # Tests date extraction from text.
    raw_lines: list[str] = [  # Creates text with date range.
        "Weekly Ad",  # Header.
        "May 13th - May 19th 2026",  # Date range.
        "H-E-B Pork Butt Country Style Ribs",  # Item name.
        "$1.79",  # Price.
        "lb",  # Unit.
        "Add to cart, H-E-B Pork Butt Country Style Ribs",  # Block sentinel.
    ]
    result = parse_heb_weekly_ad(raw_lines, "heb_weekly_ad", "HEB")  # Parses without supplied dates.
    assert result.start_date == date(2026, 5, 13)  # Verifies start date parsed.
    assert result.end_date == date(2026, 5, 19)  # Verifies end date parsed.
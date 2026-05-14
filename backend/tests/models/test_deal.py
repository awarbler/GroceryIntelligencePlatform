# =============================================================================
# File: test_deal.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests DealModel and DealMatchItem validation using fixed examples.
# Security Note: Tests use generated fake ObjectIds only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 deal matching and report validation requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation requirements.
# =============================================================================

from datetime import date  # Imports date for week_of test values.
from decimal import Decimal  # Imports Decimal for exact currency test values.

import pytest  # Imports pytest for validation error assertions.
from bson import ObjectId  # Imports ObjectId for fake MongoDB-style references.
from pydantic import ValidationError  # Imports ValidationError for rejected model input tests.

from backend.models.ad import DealType  # Imports the shared DealType enum used by DealMatchItem.
from backend.models.deal import DealMatchItem, DealModel  # Imports the models being tested.


def make_valid_deal_match_item() -> DealMatchItem:  # Creates one reusable valid DealMatchItem test object.
    return DealMatchItem(  # Builds a valid nested deal match model.
        product_ref=ObjectId(),  # Provides a fake product reference id.
        store_ref=ObjectId(),  # Provides a fake store reference id.
        deal_ref=ObjectId(),  # Provides a fake ad or deal reference id.
        coupon_refs=[ObjectId()],  # Provides one fake coupon reference id.
        rebate_refs=[ObjectId()],  # Provides one fake rebate reference id.
        shelf_price=Decimal("5.99"),  # Provides a shelf price before sale/coupons.
        register_price=Decimal("3.99"),  # Provides a register price after store/coupon changes.
        oop=Decimal("2.99"),  # Provides the out-of-pocket amount.
        rr_earned=Decimal("1.00"),  # Provides Walgreens Register Rewards earned.
        ecb_earned=Decimal("0.00"),  # Provides CVS ExtraBucks earned.
        total_rebates_back=Decimal("1.50"),  # Provides total rebate amount expected back.
        deal_type=DealType.STANDARD,  # Provides a valid shared deal type from ad.py.
        is_money_maker=True,  # Marks this fixed example as a money maker.
        matched_as_substitute=False,  # Marks this fixed example as a direct match.
    )  # Ends the valid DealMatchItem construction.


def test_deal_model_valid() -> None:  # Tests that a valid weekly deal model validates.
    item = make_valid_deal_match_item()  # Creates a valid nested deal match item.

    deal = DealModel(  # Builds a valid weekly deal model.
        week_of=date(2026, 5, 11),  # Provides a valid shopping week date.
        matches=[item],  # Provides a typed DealMatchItem inside the matches list.
    )  # Ends the valid DealModel construction.

    assert deal.week_of == date(2026, 5, 11)  # Confirms the week date was stored correctly.
    assert len(deal.matches) == 1  # Confirms one match was stored.
    assert isinstance(deal.matches[0], DealMatchItem)  # Confirms the match is a DealMatchItem model.
    assert deal.matches[0].product_ref == item.product_ref  # Confirms the nested product reference was preserved.
    assert deal.matches[0].deal_type == DealType.STANDARD  # Confirms the imported DealType value was preserved.
    assert deal.generated_at is not None  # Confirms generated_at received a default timestamp.


def test_deal_match_items_are_models_not_dicts() -> None:  # Tests that nested matches are stored as models instead of dict blobs.
    item = make_valid_deal_match_item()  # Creates a valid nested deal match item.

    deal = DealModel(  # Builds a valid DealModel with one nested item.
        week_of=date(2026, 5, 11),  # Provides a valid shopping week date.
        matches=[item],  # Provides the nested item as a typed model.
    )  # Ends the valid DealModel construction.

    assert isinstance(deal.matches[0], DealMatchItem)  # Confirms the nested item is a DealMatchItem instance.
    assert not isinstance(deal.matches[0], dict)  # Confirms the nested item is not stored as a plain dictionary.


def test_deal_rejects_extra_field() -> None:  # Tests that unknown fields are rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic to reject the extra field.
        DealModel(  # Attempts to build an invalid DealModel.
            week_of=date(2026, 5, 11),  # Provides a valid shopping week date.
            matches=[],  # Provides an empty matches list.
            unexpected_field="not allowed",  # Provides an invalid extra field.
        )  # Ends the invalid DealModel construction.
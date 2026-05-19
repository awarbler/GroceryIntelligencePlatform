# =============================================================================
# File: backend/tests/test_reward_offer_model.py
# Project: Grocery Intelligence Platform
# Purpose: Tests provider-neutral reward offer validation.
# =============================================================================

from datetime import date  # Imports date for expiration fields.
from decimal import Decimal  # Imports Decimal for money-safe values.

import pytest  # Imports pytest for exception assertions.
from pydantic import ValidationError  # Imports Pydantic validation error type.

from backend.models.reward_offer import RewardCurrencyType  # Imports reward currency enum.
from backend.models.reward_offer import RewardOfferModel  # Imports reward offer model.
from backend.models.reward_offer import RewardProvider  # Imports provider enum.
from backend.models.reward_offer import RewardSourceType  # Imports source enum.
from backend.models.reward_offer import RewardType  # Imports reward type enum.


def test_reward_offer_valid_ibotta_cash_back() -> None:  # Verifies valid Ibotta cash-back offer.
    offer = RewardOfferModel(  # Creates a valid reward offer instance.
        reward_provider=RewardProvider.IBOTTA,  # Sets provider to Ibotta.
        reward_type=RewardType.CASH_BACK,  # Sets reward type to cash back.
        reward_currency_type=RewardCurrencyType.USD,  # Sets original reward unit to dollars.
        reward_value=Decimal("3.00"),  # Stores original provider value.
        estimated_cash_value=Decimal("3.00"),  # Stores report-ready cash estimate.
        retailer="H-E-B",  # Stores retailer.
        offer_title="$3 back on eligible item",  # Stores title.
        qualifying_products=["Example Product"],  # Stores qualifying product.
        expiration_date=date(2026, 12, 31),  # Stores expiration date.
        source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
    )  # Ends model construction.

    assert offer.reward_provider == RewardProvider.IBOTTA  # Confirms provider was stored.
    assert offer.estimated_cash_value == Decimal("3.00")  # Confirms estimated cash value was stored.


def test_reward_offer_valid_fetch_points() -> None:  # Verifies valid Fetch points offer.
    offer = RewardOfferModel(  # Creates a valid Fetch offer.
        reward_provider=RewardProvider.FETCH,  # Sets provider to Fetch.
        reward_type=RewardType.POINTS_BACK,  # Sets reward type to points back.
        reward_currency_type=RewardCurrencyType.POINTS,  # Sets original reward unit to points.
        reward_value=Decimal("2500"),  # Stores original points value.
        estimated_cash_value=Decimal("2.50"),  # Stores estimated cash value.
        retailer="H-E-B",  # Stores retailer.
        spend_requirement=Decimal("15.00"),  # Stores spend threshold.
        source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
    )  # Ends model construction.

    assert offer.reward_value == Decimal("2500")  # Confirms original provider value is preserved.
    assert offer.estimated_cash_value == Decimal("2.50")  # Confirms cash estimate is separate.


def test_reward_offer_valid_swagbucks_sb() -> None:  # Verifies valid Swagbucks SB offer.
    offer = RewardOfferModel(  # Creates a valid Swagbucks offer.
        reward_provider=RewardProvider.SWAGBUCKS,  # Sets provider to Swagbucks.
        reward_type=RewardType.POINTS_BACK,  # Sets reward type to points back.
        reward_currency_type=RewardCurrencyType.SB,  # Sets original reward unit to SB.
        reward_value=Decimal("500"),  # Stores original SB value.
        estimated_cash_value=Decimal("5.00"),  # Stores estimated cash value.
        receipt_submission_required=True,  # Marks receipt submission as required.
        source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
    )  # Ends model construction.

    assert offer.receipt_submission_required is True  # Confirms receipt flag was stored.


def test_reward_offer_valid_checkout_51_receipt_cash_back() -> None:  # Verifies valid Checkout 51 offer.
    offer = RewardOfferModel(  # Creates a valid Checkout 51 offer.
        reward_provider=RewardProvider.CHECKOUT_51,  # Sets provider to Checkout 51.
        reward_type=RewardType.CASH_BACK,  # Sets reward type to cash back.
        reward_currency_type=RewardCurrencyType.USD,  # Sets original reward unit to dollars.
        reward_value=Decimal("1.50"),  # Stores original cash value.
        estimated_cash_value=Decimal("1.50"),  # Stores estimated cash value.
        quantity_requirement=2,  # Stores quantity requirement.
        receipt_submission_required=True,  # Marks receipt submission as required.
        source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
    )  # Ends model construction.

    assert offer.quantity_requirement == 2  # Confirms quantity requirement was stored.


def test_reward_offer_valid_aisle_claim_free_item() -> None:  # Verifies valid Aisle claim/free item offer.
    offer = RewardOfferModel(  # Creates a valid Aisle offer.
        reward_provider=RewardProvider.AISLE,  # Sets provider to Aisle.
        reward_type=RewardType.CLAIM_REIMBURSEMENT,  # Sets reward type to claim reimbursement.
        reward_currency_type=RewardCurrencyType.FREE_ITEM,  # Sets original reward unit to free item.
        reward_value=Decimal("1"),  # Stores original free-item quantity style value.
        estimated_cash_value=Decimal("4.99"),  # Stores estimated cash value.
        claim_required=True,  # Marks claim as required.
        phone_number_required=True,  # Marks phone number as required.
        receipt_submission_required=True,  # Marks receipt submission as required.
        free_item_quantity=1,  # Stores free item quantity.
        source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
    )  # Ends model construction.

    assert offer.claim_required is True  # Confirms claim flag was stored.
    assert offer.free_item_quantity == 1  # Confirms free item quantity was stored.


def test_reward_offer_rejects_negative_estimated_cash_value() -> None:  # Verifies negative cash estimate is rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        RewardOfferModel(  # Attempts to create invalid reward offer.
            reward_provider=RewardProvider.IBOTTA,  # Sets provider.
            reward_type=RewardType.CASH_BACK,  # Sets reward type.
            reward_currency_type=RewardCurrencyType.USD,  # Sets currency type.
            reward_value=Decimal("1.00"),  # Stores valid original value.
            estimated_cash_value=Decimal("-1.00"),  # Stores invalid negative estimate.
            source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
        )  # Ends invalid model construction.


def test_reward_offer_rejects_negative_reward_value() -> None:  # Verifies negative provider value is rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        RewardOfferModel(  # Attempts to create invalid reward offer.
            reward_provider=RewardProvider.FETCH,  # Sets provider.
            reward_type=RewardType.POINTS_BACK,  # Sets reward type.
            reward_currency_type=RewardCurrencyType.POINTS,  # Sets currency type.
            reward_value=Decimal("-100"),  # Stores invalid negative provider value.
            estimated_cash_value=Decimal("1.00"),  # Stores valid estimate.
            source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
        )  # Ends invalid model construction.


def test_reward_offer_rejects_negative_quantity_requirement() -> None:  # Verifies invalid quantity is rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        RewardOfferModel(  # Attempts to create invalid reward offer.
            reward_provider=RewardProvider.CHECKOUT_51,  # Sets provider.
            reward_type=RewardType.CASH_BACK,  # Sets reward type.
            reward_currency_type=RewardCurrencyType.USD,  # Sets currency type.
            reward_value=Decimal("1.00"),  # Stores valid original value.
            estimated_cash_value=Decimal("1.00"),  # Stores valid estimate.
            quantity_requirement=-1,  # Stores invalid quantity requirement.
            source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
        )  # Ends invalid model construction.


def test_reward_offer_rejects_extra_fields() -> None:  # Verifies unexpected fields are rejected.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        RewardOfferModel(  # Attempts to create invalid reward offer.
            reward_provider=RewardProvider.IBOTTA,  # Sets provider.
            reward_type=RewardType.CASH_BACK,  # Sets reward type.
            reward_currency_type=RewardCurrencyType.USD,  # Sets currency type.
            reward_value=Decimal("1.00"),  # Stores valid original value.
            estimated_cash_value=Decimal("1.00"),  # Stores valid estimate.
            source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
            unknown_field="not allowed",  # Adds invalid extra field.
        )  # Ends invalid model construction.


def test_reward_offer_is_active_defaults_true() -> None:  # Verifies active default.
    offer = RewardOfferModel(  # Creates a minimal valid reward offer.
        reward_provider=RewardProvider.SHOPKICK,  # Sets provider to Shopkick.
        reward_type=RewardType.POINTS_BACK,  # Sets reward type.
        reward_currency_type=RewardCurrencyType.KICKS,  # Sets original reward unit.
        reward_value=Decimal("250"),  # Stores original kicks value.
        estimated_cash_value=Decimal("1.00"),  # Stores estimated cash value.
        source_type=RewardSourceType.MANUAL_ENTRY,  # Stores source type.
    )  # Ends model construction.

    assert offer.is_active is True  # Confirms default active value.
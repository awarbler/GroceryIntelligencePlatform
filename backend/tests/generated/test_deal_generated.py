# =============================================================================
# File: test_deal_generated.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to generate DealModel and DealMatchItem validation cases.
# Security Note: Tests use generated fake ObjectIds only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 deal matching, coupon matching, rebate matching, and report validation requirements.
# SDD Traceability: Supports SDD v5.0 backend generated-test coverage requirements.
# =============================================================================

from datetime import (
    UTC,
    date,
    datetime,
)  # Imports date and timezone-aware datetime support.
from decimal import Decimal  # Imports Decimal for exact generated currency values.

from bson import (
    ObjectId,
)  # Imports ObjectId for generated fake MongoDB-style references.
from hypothesis import (
    given,
    settings,
)  # Imports Hypothesis decorators for generated tests.
from hypothesis import (
    strategies as st,
)  # Imports Hypothesis strategies for generated values.

from backend.models.ad import (
    DealType,
)  # Imports the shared DealType enum used by the deal model.
from backend.models.deal import (
    DealMatchItem,
    DealModel,
)  # Imports the models being tested.


object_id_strategy = st.builds(ObjectId)  # Generates valid fake MongoDB ObjectIds.

money_strategy = st.decimals(  # Generates safe Decimal currency values.
    min_value=Decimal("0.00"),  # Sets the smallest generated money value.
    max_value=Decimal("500.00"),  # Sets the largest generated money value.
    places=2,  # Limits generated values to two decimal places.
    allow_nan=False,  # Prevents generated NaN values.
    allow_infinity=False,  # Prevents generated infinity values.
)  # Ends the Decimal money strategy definition.

deal_type_strategy = st.sampled_from(
    list(DealType)
)  # Generates valid DealType enum values from ad.py.

deal_match_item_strategy = st.builds(  # Generates complete valid DealMatchItem objects.
    DealMatchItem,  # Builds the nested deal match model.
    product_ref=object_id_strategy,  # Generates a valid product reference id.
    store_ref=object_id_strategy,  # Generates a valid store reference id.
    deal_ref=st.one_of(
        st.none(), object_id_strategy
    ),  # Generates either no deal reference or a valid deal reference id.
    coupon_refs=st.lists(
        object_id_strategy, max_size=3
    ),  # Generates a short list of coupon reference ids.
    rebate_refs=st.lists(
        object_id_strategy, max_size=3
    ),  # Generates a short list of rebate reference ids.
    shelf_price=money_strategy,  # Generates a valid shelf price.
    register_price=money_strategy,  # Generates a valid register price.
    oop=money_strategy,  # Generates a valid out-of-pocket amount.
    rr_earned=money_strategy,  # Generates a valid Walgreens Register Rewards amount.
    ecb_earned=money_strategy,  # Generates a valid CVS ExtraBucks amount.
    total_rebates_back=money_strategy,  # Generates a valid total rebate amount.
    deal_type=deal_type_strategy,  # Generates a valid imported deal type.
    is_money_maker=st.booleans(),  # Generates a true or false money-maker flag.
    matched_as_substitute=st.booleans(),  # Generates a true or false substitute-match flag.
)  # Ends the DealMatchItem generated strategy definition.


@given(item=deal_match_item_strategy)  # Generates many valid DealMatchItem examples.
@settings(
    max_examples=50
)  # Limits the generated test run to 50 examples for fast local feedback.
def test_generated_deal_match_item_valid(
    item: DealMatchItem,
) -> None:  # Tests generated DealMatchItem validation.
    assert isinstance(
        item, DealMatchItem
    )  # Confirms Hypothesis generated a valid DealMatchItem model.
    assert isinstance(
        item.deal_type, DealType
    )  # Confirms deal_type always comes from the imported DealType enum.
    assert item.shelf_price >= Decimal(
        "0.00"
    )  # Confirms generated shelf price stays nonnegative.
    assert item.register_price >= Decimal(
        "0.00"
    )  # Confirms generated register price stays nonnegative.
    assert item.oop >= Decimal(
        "0.00"
    )  # Confirms generated out-of-pocket amount stays nonnegative.


@given(
    matches=st.lists(deal_match_item_strategy, max_size=5)
)  # Generates lists of valid DealMatchItem models.
@settings(
    max_examples=50
)  # Limits the generated test run to 50 examples for fast local feedback.
def test_generated_deal_model_valid(
    matches: list[DealMatchItem],
) -> None:  # Tests generated DealModel validation.
    deal = DealModel(  # Builds a valid DealModel from generated match items.
        week_of=date(2026, 5, 11),  # Provides a fixed valid week date.
        generated_at=datetime.now(
            UTC
        ),  # Provides a timezone-aware generated timestamp.
        matches=matches,  # Provides generated typed DealMatchItem models.
    )  # Ends the generated DealModel construction.

    assert isinstance(
        deal, DealModel
    )  # Confirms the generated weekly deal report validates.
    assert all(
        isinstance(item, DealMatchItem) for item in deal.matches
    )  # Confirms all nested matches are typed models.
    assert not any(
        isinstance(item, dict) for item in deal.matches
    )  # Confirms nested matches are not stored as dict blobs.

# =============================================================================
# File: test_rebate_hypothesis.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to generate rebate validation test inputs automatically.
# Security Note: Tests use generated fake data only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 generated validation and regression testing.
# SDD Traceability: Supports SDD v5.0 model-layer testability and edge-case validation.
# =============================================================================

from datetime import (
    date,
)  # Imports date so generated tests can create valid expiration dates.
from decimal import Decimal  # Imports Decimal so generated money values stay precise.

from hypothesis import (
    given,
)  # Imports the decorator that tells Hypothesis to generate test inputs.
from hypothesis import (
    strategies as st,
)  # Imports Hypothesis strategies used to generate input values.

from backend.models.rebate import RebateModel  # Imports the rebate model being tested.
from backend.models.rebate import (
    RebateStatus,
)  # Imports the valid rebate lifecycle statuses.


@given(  # Starts a Hypothesis-generated test configuration.
    rebate_amount=st.decimals(
        min_value=Decimal("0.01"), max_value=Decimal("100.00"), places=2
    ),  # Generates valid cash rebate amounts.
)
def test_generated_positive_rebate_amounts_are_accepted(
    rebate_amount: Decimal,
) -> None:  # Tests many valid rebate amounts automatically.
    rebate = RebateModel(  # Creates a RebateModel using the generated rebate amount.
        company="Ibotta",  # Sets a valid rebate company.
        item_name="Generated rebate item",  # Sets a valid item name.
        rebate_amount=rebate_amount,  # Uses the generated valid rebate amount.
        dollar_equivalent=rebate_amount,  # Uses the same amount as the dollar equivalent.
        expiration_date=date(2026, 12, 31),  # Sets a valid expiration date.
        status=RebateStatus.PENDING,  # Sets a valid lifecycle status.
    )
    assert (
        rebate.rebate_amount == rebate_amount
    )  # Verifies the generated rebate amount was accepted.
    assert (
        rebate.dollar_equivalent == rebate_amount
    )  # Verifies the generated dollar equivalent was accepted.

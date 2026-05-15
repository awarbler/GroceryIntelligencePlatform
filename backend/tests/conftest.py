# =============================================================================
# File: conftest.py  # Identifies this shared pytest configuration file.
# Project: Grocery Intelligence Platform  # Identifies the project this test file supports.
# Author: Anita Woodford  # Identifies the project author.
# Description: Provides reusable pytest fixtures for backend model tests.  # Explains the purpose of this file.
# Security Note: Test fixtures use fake rebate data only and do not contain secrets.  # Notes that no sensitive data belongs here.
# SRS Traceability: Supports SRS v5.0 backend validation and regression testing.  # Connects this test file to SRS validation requirements.
# SDD Traceability: Supports SDD v5.0 model-layer testability and data validation.  # Connects this test file to SDD testability requirements.
# =============================================================================

from datetime import date  # Imports date so test fixtures can create expiration dates.
from decimal import Decimal  # Imports Decimal so money values are tested accurately.

import pytest  # Imports pytest so reusable fixtures can be declared.

from backend.models.rebate import (
    RebateStatus,
)  # Imports the approved rebate status enum.


@pytest.fixture  # Registers this function as a reusable pytest fixture.
def valid_ibotta_rebate_data() -> (
    dict
):  # Defines reusable valid Ibotta rebate input data.
    return {  # Returns a dictionary that can be unpacked into RebateModel.
        "company": "Ibotta",  # Sets the rebate company name.
        "item_name": "Children's Claritin liquid",  # Sets the rebate item name.
        "rebate_amount": Decimal("5.00"),  # Sets the cash rebate amount.
        "dollar_equivalent": Decimal("5.00"),  # Sets the dollar value of the rebate.
        "expiration_date": date(2026, 12, 31),  # Sets the rebate expiration date.
        "status": RebateStatus.PENDING,  # Sets a valid lifecycle status.
        "must_unlock_before_purchase": True,  # Records that the rebate must be unlocked before purchase.
        "unlocked_before_purchase": True,  # Records that the rebate was unlocked before purchase.
        "barcode_scan_required": True,  # Records that barcode scanning may be required.
    }  # Ends the valid Ibotta rebate dictionary.


@pytest.fixture  # Registers this function as a reusable pytest fixture.
def valid_fetch_rebate_data() -> (
    dict
):  # Defines reusable valid Fetch rebate input data.
    return {  # Returns a dictionary that can be unpacked into RebateModel.
        "company": "Fetch",  # Sets the rebate company name.
        "item_name": "Dove body wash",  # Sets the rebate item name.
        "points_amount": 4000,  # Sets the Fetch points amount.
        "dollar_equivalent": Decimal(
            "4.00"
        ),  # Sets the expected dollar equivalent for 4000 points.
        "expiration_date": date(2026, 12, 31),  # Sets the rebate expiration date.
    }  # Ends the valid Fetch rebate dictionary.

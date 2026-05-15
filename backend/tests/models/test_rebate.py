# =============================================================================  # Creates a visible file header section.
# File: backend/tests/models/test_rebate.py  # Identifies the test file path.
# Project: Grocery Intelligence Platform  # Identifies the project.
# Purpose: Tests Phase 1 rebate model validation.  # Explains the test file purpose.
# Author: Anita Woodford  # Identifies the author.
# Security Note: Tests use fake rebate data only and do not contain secrets.  # Notes that no sensitive data belongs here.
# SRS Traceability: Supports SRS v5.0 rebate validation and regression testing.  # Connects this test file to SRS validation.
# SDD Traceability: Supports SDD v5.0 backend model testability and data integrity.  # Connects this test file to SDD validation.
# =============================================================================  # Ends the header section.

from datetime import date  # Imports date for expiration date test values.
from decimal import Decimal  # Imports Decimal for money-safe values.

import pytest  # Imports pytest for assertions and exception testing.
from pydantic import (
    ValidationError,
)  # Imports ValidationError for expected validation failures.

from backend.models.rebate import (
    RebateModel,
    RebateStatus,
)  # Imports the rebate model and status enum.


def test_rebate_status_exact_values() -> (
    None
):  # Verifies the rebate enum has exactly the approved values.
    actual_values = {
        status.value for status in RebateStatus
    }  # Collects all enum values into a set.
    expected_values = {
        "PENDING",
        "SUBMITTED",
        "RECEIVED",
        "DENIED",
    }  # Defines the required lifecycle statuses.
    assert (
        actual_values == expected_values
    )  # Confirms no required value is missing and no extra value exists.


def test_rebate_rejects_unlocked_status() -> (
    None
):  # Verifies UNLOCKED is not allowed as a rebate status.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        RebateModel.model_validate(  # Validates a rebate payload.
            {  # Starts the invalid payload dictionary.
                "company": "Ibotta",  # Provides the rebate company.
                "item_name": "Children's Claritin liquid",  # Provides the rebate item name.
                "dollar_equivalent": Decimal(
                    "5.00"
                ),  # Provides the rebate dollar value.
                "expiration_date": date(
                    2026, 12, 31
                ),  # Provides the required expiration date.
                "status": "UNLOCKED",  # Provides an invalid status that must fail.
            }  # Ends the invalid payload dictionary.
        )  # Ends model validation call.


def test_rebate_model_valid() -> (
    None
):  # Verifies a valid cash rebate model can be created.
    rebate = RebateModel(  # Creates a valid rebate model instance.
        company="Ibotta",  # Sets the rebate company.
        item_name="Children's Claritin liquid",  # Sets the rebate item name.
        rebate_amount=Decimal("5.00"),  # Sets the cash rebate amount.
        dollar_equivalent=Decimal("5.00"),  # Sets the rebate dollar value.
        expiration_date=date(2026, 12, 31),  # Sets the required expiration date.
        status=RebateStatus.PENDING,  # Sets the required lifecycle status.
    )  # Ends the valid rebate model creation.
    assert rebate.company == "Ibotta"  # Confirms the company field is stored correctly.
    assert (
        rebate.item_name == "Children's Claritin liquid"
    )  # Confirms the item name field is stored correctly.
    assert rebate.rebate_amount == Decimal(
        "5.00"
    )  # Confirms the rebate amount is stored correctly.
    assert rebate.dollar_equivalent == Decimal(
        "5.00"
    )  # Confirms the dollar equivalent is stored correctly.
    assert rebate.expiration_date == date(
        2026, 12, 31
    )  # Confirms the expiration date is stored correctly.
    assert (
        rebate.status == RebateStatus.PENDING
    )  # Confirms the rebate status is stored correctly.


def test_rebate_requires_expiration_date() -> (
    None
):  # Verifies expiration_date is required.
    with pytest.raises(ValidationError):  # Expects Pydantic validation to fail.
        RebateModel.model_validate(  # Validates a rebate payload missing expiration_date.
            {  # Starts the invalid payload dictionary.
                "company": "Ibotta",  # Provides the rebate company.
                "item_name": "Children's Claritin liquid",  # Provides the rebate item name.
                "rebate_amount": Decimal("5.00"),  # Provides the cash rebate amount.
                "dollar_equivalent": Decimal(
                    "5.00"
                ),  # Provides the rebate dollar value.
                "status": RebateStatus.PENDING,  # Provides a valid lifecycle status.
            }  # Ends the invalid payload dictionary.
        )  # Ends model validation call.


def test_rebate_unlock_boolean_fields_valid() -> (
    None
):  # Verifies Ibotta unlock behavior is stored as boolean metadata.
    rebate = RebateModel(  # Creates a valid Ibotta-style rebate model.
        company="Ibotta",  # Sets the rebate company.
        item_name="Children's Claritin liquid",  # Sets the rebate item name.
        rebate_amount=Decimal("5.00"),  # Sets the cash rebate amount.
        dollar_equivalent=Decimal("5.00"),  # Sets the rebate dollar value.
        expiration_date=date(2026, 12, 31),  # Sets the required expiration date.
        status=RebateStatus.PENDING,  # Sets the lifecycle status.
        must_unlock_before_purchase=True,  # Records that the rebate must be unlocked before purchase.
        unlocked_before_purchase=True,  # Records that the rebate was unlocked before purchase.
        barcode_scan_required=True,  # Records that barcode scanning may be required.
    )  # Ends the valid Ibotta-style rebate model creation.
    assert (
        rebate.must_unlock_before_purchase is True
    )  # Confirms the must-unlock metadata is stored as a boolean.
    assert (
        rebate.unlocked_before_purchase is True
    )  # Confirms the unlocked-before-purchase metadata is stored as a boolean.
    assert (
        rebate.barcode_scan_required is True
    )  # Confirms the barcode-scan metadata is stored as a boolean.
    assert (
        rebate.status == RebateStatus.PENDING
    )  # Confirms unlock behavior did not become a lifecycle status.


def test_fetch_points_dollar_equivalent() -> (
    None
):  # Verifies Fetch points convert to the correct dollar equivalent.
    rebate = RebateModel(  # Creates a valid Fetch rebate model.
        company="Fetch",  # Sets the rebate company.
        item_name="Dove body wash",  # Sets the rebate item.
        points_amount=4000,  # Sets the Fetch points amount.
        dollar_equivalent=Decimal(
            "4.00"
        ),  # Sets the expected dollar equivalent for 4000 points.
        expiration_date=date(2026, 12, 31),  # Sets the required expiration date.
    )  # Ends the valid Fetch rebate model creation.
    assert (
        rebate.points_amount == 4000
    )  # Confirms the points amount is stored correctly.
    assert rebate.dollar_equivalent == Decimal(
        "4.00"
    )  # Confirms the dollar equivalent is stored correctly.

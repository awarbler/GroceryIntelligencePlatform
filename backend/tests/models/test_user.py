# =============================================================================
# File: test_user.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests UserModel validation rules using fixed example payloads.
# Security Note: Tests use fake user data only and do not contain real passwords or secrets.
# SRS Traceability: Supports SRS v5.0 user preference and report configuration validation.
# SDD Traceability: Supports SDD v5.0 backend model validation and automated test coverage.
# =============================================================================

from decimal import Decimal  # Imports Decimal for exact reward conversion test values.

import pytest  # Imports pytest for validation failure assertions.

from pydantic import ValidationError  # Imports ValidationError to verify invalid model payloads.

from backend.models.user import ReportFormat, UserModel  # Imports the model and enum under test.


def test_user_model_valid() -> None:  # Tests that a complete valid user payload creates a UserModel.
    user = UserModel(  # Creates a valid user model instance.
        username="aj",  # Provides the required username field.
        password_hash="fake_hash_for_testing_only",  # Provides the required password hash field.
        preferred_stores=["HEB", "CVS", "WALGREENS"],  # Provides preferred store settings.
        report_format=ReportFormat.PDF,  # Provides a valid report format enum value.
        ocr_threshold_review=0.70,  # Provides a valid OCR review threshold.
        ocr_threshold_accept=0.95,  # Provides a valid OCR auto-accept threshold.
        fetch_points_per_dollar=Decimal("1000.00"),  # Provides a valid Fetch point conversion rate.
    ) 

    assert user.username == "aj"  # Confirms the username was stored correctly.
    assert user.password_hash == "fake_hash_for_testing_only"  # Confirms the password hash was stored correctly.
    assert user.preferred_stores == ["HEB", "CVS", "WALGREENS"]  # Confirms preferred stores were stored correctly.
    assert user.report_format == ReportFormat.PDF  # Confirms the report format was stored as an enum.
    assert user.ocr_threshold_review == 0.70  # Confirms the OCR review threshold was stored correctly.
    assert user.ocr_threshold_accept == 0.95  # Confirms the OCR accept threshold was stored correctly.
    assert user.fetch_points_per_dollar == Decimal("1000.00")  # Confirms the Fetch conversion value was stored correctly.


def test_user_requires_password_hash() -> None:  # Tests that password_hash is required.
    with pytest.raises(ValidationError):  # Expects Pydantic to reject the missing password_hash field.
        UserModel(  # Attempts to create an invalid user model instance.
            username="aj",  # Provides the required username field.
            preferred_stores=["HEB"],  # Provides preferred stores.
            report_format=ReportFormat.PDF,  # Provides a valid report format.
            ocr_threshold_review=0.75,  # Provides a valid OCR review threshold.
            ocr_threshold_accept=0.95,  # Provides a valid OCR accept threshold.
            fetch_points_per_dollar=Decimal("1000.00"),  # Provides a valid Fetch conversion value.
        ) 


def test_user_rejects_extra_field() -> None:  # Tests that UserModel rejects fields not defined in the schema.
    with pytest.raises(ValidationError):  # Expects Pydantic to reject the unknown field.
        UserModel(  # Attempts to create a user model with an extra field.
            username="aj",  # Provides the required username field.
            password_hash="fake_hash_for_testing_only",  # Provides the required password hash field.
            preferred_stores=["HEB"],  # Provides preferred stores.
            report_format=ReportFormat.PDF,  # Provides a valid report format.
            ocr_threshold_review=0.75,  # Provides a valid OCR review threshold.
            ocr_threshold_accept=0.95,  # Provides a valid OCR accept threshold.
            fetch_points_per_dollar=Decimal("1000.00"),  # Provides a valid Fetch conversion value.
            plaintext_password="do_not_store_this",  # Provides an invalid extra field that should be rejected.
        )  
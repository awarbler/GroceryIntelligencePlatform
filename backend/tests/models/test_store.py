# =============================================================================
# File: test_store.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests StoreModel validation rules using fixed example payloads.
# Security Note: Tests use fake store configuration data only and do not contain credentials.
# SRS Traceability: Supports SRS v5.0 store-specific parser configuration validation.
# SDD Traceability: Supports SDD v5.0 backend model validation and store configuration design.
# =============================================================================

import pytest  # Imports pytest for validation failure assertions.

from pydantic import (
    ValidationError,
)  # Imports ValidationError to verify invalid payloads.

from backend.models.store import StoreModel  # Imports the store model under test.


def test_store_model_valid() -> (
    None
):  # Tests that a valid store payload creates a StoreModel.
    store = StoreModel(  # Creates a valid store model instance.
        store_id="heb",  # Provides the required internal store identifier.
        display_name="H-E-B",  # Provides the required display name.
        parser_module="backend.parsers.heb_online_receipt",  # Provides the parser module path.
        active=True,  # Marks the store as active.
        session_file="sessions/heb_session.json",  # Provides a fake session file path.
        login_url="https://www.heb.com/login",  # Provides the store login URL.
        abbreviation_table_ref=None,  # Leaves abbreviation mapping unset for this test.
    )

    assert store.store_id == "heb"  # Confirms the store identifier was stored.
    assert store.display_name == "H-E-B"  # Confirms the display name was stored.
    assert (
        store.parser_module == "backend.parsers.heb_online_receipt"
    )  # Confirms the parser module was stored.
    assert store.active is True  # Confirms the active flag was stored.
    assert (
        store.session_file == "sessions/heb_session.json"
    )  # Confirms the session file reference was stored.
    assert (
        store.login_url == "https://www.heb.com/login"
    )  # Confirms the login URL was stored.
    assert (
        store.abbreviation_table_ref is None
    )  # Confirms the abbreviation table reference can be empty.


def test_store_rejects_extra_field() -> None:  # Tests that unknown fields are rejected.
    with pytest.raises(ValidationError):  # Expects validation to fail.
        StoreModel(  # Attempts to create a store with an extra field.
            store_id="heb",  # Provides the required internal store identifier.
            display_name="H-E-B",  # Provides the required display name.
            parser_module="backend.parsers.heb_online_receipt",  # Provides the parser module path.
            active=True,  # Marks the store as active.
            session_file="sessions/heb_session.json",  # Provides a fake session file path.
            login_url="https://www.heb.com/login",  # Provides the store login URL.
            abbreviation_table_ref=None,  # Leaves abbreviation mapping unset for this test.
            password="do_not_store_credentials_here",  # Provides an invalid extra field.
        )

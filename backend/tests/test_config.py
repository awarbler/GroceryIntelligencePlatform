# =============================================================================
# File: Test_config.py
# Project: Grocery Intelligence Platform
# Created Date: 2024-06-15
# Author: Anita Woodford
# Purpose: Unit tests for configuration management
# Description: This file contains unit tests for the configuration management
# of the backend application. It tests loading environment variables, handling
# missing variables, and validating configuration values.
# Testing Scope: These test use pytest monkeypatch to create temp env. var.
# without changing the real local .env file
# security note: test secrets are fake values only and must never be replaced
# with the real production secrets or real acct credentials.
# =============================================================================
import pytest
from backend.config import Settings, get_settings


def set_require_env(monkeypatch):
    """
    Set all valid environment variables required by the setting class
    This helper prevents repeated setup code in each test
    It uses pytest monkeypatch fixture so the values exist only during the test
    it does not modify the real .env file and does not expose real info

    Args:
        monkeypatch (_type_): _description_
    """

    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017/")
    monkeypatch.setenv("MONGO_DB", "grocery_intelligence")
    monkeypatch.setenv("TEST_MONGO_DB", "grocery_intelligence_test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
    monkeypatch.setenv(
        "CREDENTIAL_ENCRYPTION_KEY", "test-secret-key-that-is-at-least-32-chars"
    )
    monkeypatch.setenv("OCR_CONFIDENCE_THRESHOLD_REVIEW", "0.70")
    monkeypatch.setenv("OCR_CONFIDENCE_THRESHOLD_ACCEPT", "0.85")
    monkeypatch.setenv("FETCH_POINTS_PER_DOLLAR", "1000")
    monkeypatch.setenv("SWAGBUCKS_POINTS_PER_DOLLAR", "100")


def test_load_settings(monkeypatch):  # defines test that verifies setting loads
    """Confirm that the settings reads the required env. var. and converts
    them correctly.

    This test checks the main success path
    It proves that the numeric config. values are parsed into float and int fields
    """

    set_require_env(monkeypatch)  # set the env. var. for this test
    settings = Settings()  # create settings instance which should read the env. var.

    assert settings.mongo_uri == "mongodb://localhost:27017/"  # confirms uri loaded
    # confirm the main mongodb database name loaded
    assert settings.mongo_db == "grocery_intelligence"
    # confirm the test database name loaded correctly
    assert settings.test_mongo_db == "grocery_intelligence_test"
    # confirm the secret key loaded correctly
    assert (
        settings.secret_key.get_secret_value()
        == "test-secret-key-that-is-at-least-32-chars"
    )
    # confirm the encryption key loaded correctly
    assert (
        settings.credential_encryption_key.get_secret_value()
        == "test-secret-key-that-is-at-least-32-chars"
    )
    # confirms ocr review threshold loaded and converted to float
    assert settings.ocr_confidence_threshold_review == 0.70
    # confirms ocr accept threshold loaded and converted to float
    assert settings.ocr_confidence_threshold_accept == 0.85
    # confirms points per dollar loaded and converted to int
    assert settings.fetch_points_per_dollar == 1000
    # confirms swagbucks points per dollar loaded and converted to int
    assert settings.swagbucks_points_per_dollar == 100


# defines a test that verifies get settings is caching
def test_get_settings_caching(monkeypatch):
    """Confirm that the get_settings function is caching the settings instance
    This test calls get_settings multiple times and confirms it returns the same instance

    Confirm get_settings returns the same cached Settings object on repeated calls.

    This test verifies the lru_cache behavior used by backend modules.
    Caching prevents the application from rebuilding Settings every time config is needed.
    The cache is cleared before and after the test so other tests stay independent.
    """

    # explains the caching behavior and why cache clean up maters

    get_settings.cache_clear()  # clear cache before test to ensure clean state

    set_require_env(monkeypatch)  # set the env. var. for this test

    settings_one = get_settings()  # first call to get settings
    settings_two = get_settings()  # second call to get settings

    assert settings_one is settings_two  # confirms both calls return the same instance

    get_settings.cache_clear()  # clear cache after test to prevent side effects on other tests


# defines a test for weak secret key rejection
""" Confirm Settings rejects a SECRET_KEY that is shorter than the required length.
This test checks a validation failure path.
It proves the application will fail fast when a weak secret key is configured.
A fast startup failure is safer than allowing the app to run with bad security 
settings."""


def test_weak_secret_key(monkeypatch):
    set_require_env(monkeypatch)  # set the env. var. for this test
    monkeypatch.setenv("SECRET_KEY", "short")  # set a weak secret key that is too short
    with pytest.raises(
        ValueError, match="SECRET_KEY must be at least 32 characters long"
    ):
        Settings()  # attempt to create settings which should raise a ValueError due to weak secret key


# defines a test for invalid ocr threshold rejection
def test_invalid_ocr_threshold(monkeypatch):
    """
    Confirm Settings rejects OCR confidence thresholds outside the valid probability range.

    This test checks another validation failure path.
    OCR thresholds should be decimal probability values between 0.0 and 1.0.
    Rejecting invalid thresholds prevents confusing parser behavior later in the ETL pipeline.
    """

    set_require_env(monkeypatch)  # Prepares valid defaults first.
    monkeypatch.setenv(
        "OCR_CONFIDENCE_THRESHOLD_ACCEPT", "1.25"
    )  # Overrides the OCR accept threshold with an invalid value.

    with pytest.raises(
        ValueError
    ):  # Expects Pydantic validation to raise a ValueError.
        Settings()  # Attempts to create Settings with the invalid OCR threshold.

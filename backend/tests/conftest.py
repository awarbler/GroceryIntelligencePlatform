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

from backend.models.rebate import RebateStatus # Imports the approved rebate status enum.
import os  # Reads environment variables for test database isolation.
from pathlib import Path  # Builds safe fixture paths.

import pytest_asyncio  # Supports async pytest fixtures.
from fastapi.testclient import TestClient  # Provides FastAPI route test client.
from motor.motor_asyncio import AsyncIOMotorClient  # Provides async MongoDB test client.

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
def valid_fetch_rebate_data() -> (dict):  # Defines reusable valid Fetch rebate input data.
    return {  # Returns a dictionary that can be unpacked into RebateModel.
        "company": "Fetch",  # Sets the rebate company name.
        "item_name": "Dove body wash",  # Sets the rebate item name.
        "points_amount": 4000,  # Sets the Fetch points amount.
        "dollar_equivalent": Decimal(
            "4.00"
        ),  # Sets the expected dollar equivalent for 4000 points.
        "expiration_date": date(2026, 12, 31),  # Sets the rebate expiration date.
    }  # Ends the valid Fetch rebate dictionary.

@pytest.fixture(scope="session")  # Creates one API client for the test session.
def test_client() -> TestClient:  # Provides FastAPI TestClient to route tests.
    from backend.main import app  # Imports app inside fixture to reduce import-side effects.
    return TestClient(app, raise_server_exceptions=False)  # Returns client while preserving HTTP error responses.


@pytest_asyncio.fixture  # Registers an async fixture for database tests.
async def test_db():  # Provides isolated test database access.
    test_db_name = os.environ.get("TEST_MONGO_DB")  # Reads the required test database name.
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")  # Reads MongoDB connection URI.

    if not test_db_name:  # Checks that test DB is explicitly configured.
        raise RuntimeError("TEST_MONGO_DB must be set before running database tests.")  # Stops unsafe test setup.

    if "test" not in test_db_name.lower():  # Checks that database name is clearly a test database.
        raise RuntimeError("TEST_MONGO_DB must include 'test' in its name for safety.")  # Prevents accidental cleanup of dev data.

    client = AsyncIOMotorClient(mongo_uri)  # Creates MongoDB client.
    database = client[test_db_name]  # Selects only the configured test database.

    try:  # Ensures cleanup runs even when a test fails.
        yield database  # Gives the database to the test.
    finally:  # Runs cleanup after each test.
        collection_names = await database.list_collection_names()  # Lists all collections created by the test.
        for collection_name in collection_names:  # Loops through test-created collections.
            await database[collection_name].drop()  # Drops each collection from the test database.
        client.close()  # Closes the MongoDB client.


@pytest.fixture  # Registers sanitized H-E-B text fixture.
def sample_heb_text() -> str:  # Loads sample receipt text for parser/pipeline tests.
    fixture_path = Path(__file__).parent / "fixtures" / "heb" / "sample_receipt_01.txt"  # Builds fixture path.
    return fixture_path.read_text(encoding="utf-8")  # Reads fixture text.

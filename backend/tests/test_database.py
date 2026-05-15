# =============================================================================  # Starts the file header block.
# File: test_database.py  # Identifies the test file name.
# Project: Grocery Intelligence Platform  # Identifies the project name.
# Author: Anita Woodford  # Identifies the project author.
# Purpose: Unit tests for the MongoDB database connection layer.  # Explains the file purpose.
# Description: These tests verify collection constants, database helper behavior,  # Describes what the tests check.
# index creation, connection setup, and shutdown cleanup without requiring a live DB.  # Explains the test isolation strategy.
# Security Note: These tests use fake settings and mocks only, never real secrets.  # Explains the test security rule.
# =============================================================================  # Ends the file header block.

"""Unit tests for backend.database."""  # Provides the module docstring.

from unittest.mock import AsyncMock  # Imports AsyncMock for async Motor calls.
from unittest.mock import (
    MagicMock,
)  # Imports MagicMock for fake database and client objects.
from unittest.mock import (
    patch,
)  # Imports patch for replacing module dependencies during tests.

import pytest  # Imports pytest for assertions and async test support.

from backend import database  # Imports the database module under test.


def test_all_collection_constants_are_defined() -> (
    None
):  # Defines a test for approved collection constants.
    expected_collections = {  # Creates the expected set of approved MongoDB collections.
        "users",  # Requires the users collection.
        "stores",  # Requires the stores collection.
        "products",  # Requires the products collection.
        "purchases",  # Requires the purchases collection.
        "ads",  # Requires the ads collection.
        "coupons",  # Requires the coupons collection.
        "rebates",  # Requires the rebates collection.
        "reward_accounts",  # Requires the reward accounts collection.
        "reward_transactions",  # Requires the reward transactions collection.
        "deal_matches",  # Requires the deal matches collection.
        "raw_inputs",  # Requires the raw inputs collection.
    }  # Ends the expected collection set.

    assert (
        set(database.ALL_COLLECTIONS) == expected_collections
    )  # Confirms the module exposes exactly the approved collections.
    assert (
        len(database.ALL_COLLECTIONS) == 11
    )  # Confirms there are exactly 11 approved collections.


def test_get_database_raises_when_disconnected() -> (
    None
):  # Defines a test for disconnected database access.
    with patch.object(
        database, "_db", None
    ):  # Temporarily forces the database reference to be disconnected.
        with pytest.raises(
            RuntimeError, match="Database not connected"
        ):  # Expects a clear runtime error.
            database.get_db()  # Attempts to access the database before startup.


def test_get_collection_raises_when_disconnected() -> (
    None
):  # Defines a test for disconnected collection access.
    with patch.object(
        database, "_db", None
    ):  # Temporarily forces the database reference to be disconnected.
        with pytest.raises(
            RuntimeError, match="Database not connected. Call connect_to_mongodb first."
        ):  # Expects a clear runtime error.
            database.get_collection(
                database.USERS_COLLECTION
            )  # Attempts to access a collection before startup.


def test_get_collection_rejects_unknown_collection_name() -> (
    None
):  # Defines a test for collection-name validation.
    mock_db = MagicMock()  # Creates a fake MongoDB database object.

    with patch.object(
        database, "_db", mock_db
    ):  # Temporarily injects the fake database into the module.
        with pytest.raises(
            ValueError, match="Invalid collection name"
        ):  # Expects invalid collection names to be rejected.
            database.get_collection(
                "Invalid collection name:"
            )  # Attempts to access a collection outside the approved schema.


def test_get_collection_returns_known_collection() -> (
    None
):  # Defines a test for valid collection access.
    mock_db = MagicMock()  # Creates a fake MongoDB database object.
    mock_collection = MagicMock()  # Creates a fake MongoDB collection object.
    mock_db.__getitem__.return_value = (
        mock_collection  # Makes db[name] return the fake collection.
    )

    with patch.object(
        database, "_db", mock_db
    ):  # Temporarily injects the fake database into the module.
        result = database.get_collection(
            database.USERS_COLLECTION
        )  # Requests an approved collection.

    assert (
        result == mock_collection
    )  # Confirms the helper returned the requested collection.
    mock_db.__getitem__.assert_called_once_with(
        database.USERS_COLLECTION
    )  # Confirms the correct collection name was requested.


@pytest.mark.asyncio  # Marks this test as an async pytest test.
async def test_create_indexes_creates_expected_indexes() -> (
    None
):  # Defines a test for MongoDB index creation.
    mock_db = MagicMock()  # Creates a fake MongoDB database object.
    mock_collections = {}  # Creates a dictionary to store fake collections by name.

    for (
        collection_name
    ) in database.ALL_COLLECTIONS:  # Iterates over every approved collection name.
        mock_collection = (
            MagicMock()
        )  # Creates a fake collection for this collection name.
        mock_collection.create_index = (
            AsyncMock()
        )  # Adds an async create_index method to the fake collection.
        mock_collections[collection_name] = (
            mock_collection  # Stores the fake collection by name.
        )

    mock_db.__getitem__.side_effect = lambda name: mock_collections[
        name
    ]  # Makes db[name] return the matching fake collection.

    with patch.object(
        database, "_db", mock_db
    ):  # Temporarily injects the fake database into the module.
        await database.create_indexes()  # Runs the index creation function.

    mock_collections[database.PURCHASES_COLLECTION].create_index.assert_any_await(
        "store_ref"
    )  # Verifies the purchase store index.
    mock_collections[database.PURCHASES_COLLECTION].create_index.assert_any_await(
        "purchase_date"
    )  # Verifies the purchase date index.
    mock_collections[database.COUPONS_COLLECTION].create_index.assert_awaited_once_with(
        "expiration_date"
    )  # Verifies the coupon expiration index.
    mock_collections[database.REBATES_COLLECTION].create_index.assert_awaited_once_with(
        "status"
    )  # Verifies the rebate status index.
    mock_collections[database.PRODUCTS_COLLECTION].create_index.assert_any_await(
        "canonical_name"
    )  # Verifies the canonical product index.
    mock_collections[database.PRODUCTS_COLLECTION].create_index.assert_any_await(
        "normalized_name"
    )  # Verifies the normalized product index.
    mock_collections[
        database.DEAL_MATCHES_COLLECTION
    ].create_index.assert_awaited_once_with(
        "store_ref"
    )  # Verifies the deal match store index.
    mock_collections[
        database.RAW_INPUTS_COLLECTION
    ].create_index.assert_awaited_once_with(
        "timestamp"
    )  # Verifies the raw input timestamp index.


@pytest.mark.asyncio  # Marks this test as an async pytest test.
async def test_create_indexes_raises_when_disconnected() -> (
    None
):  # Defines a test for index creation without a database.
    with patch.object(
        database, "_db", None
    ):  # Temporarily forces the database reference to be disconnected.
        with pytest.raises(
            RuntimeError, match="Database not connected"
        ):  # Expects a clear runtime error.
            await (
                database.create_indexes()
            )  # Attempts to create indexes without a database connection.


@pytest.mark.asyncio  # Marks this test as an async pytest test.
async def test_connect_to_mongo_creates_client_pings_and_indexes() -> (
    None
):  # Defines a test for connection startup behavior.
    mock_settings = MagicMock()  # Creates fake settings.
    mock_settings.mongo_uri = "mongodb://localhost:27017"  # Sets a fake MongoDB URI.
    mock_settings.mongo_db = (
        "grocery_intelligence_test"  # Sets a fake MongoDB database name.
    )

    mock_client = MagicMock()  # Creates a fake Motor client.
    mock_client.admin.command = AsyncMock(
        return_value={"ok": 1}
    )  # Makes client.admin.command async and successful.
    mock_db = MagicMock()  # Creates a fake MongoDB database object.
    mock_client.__getitem__.return_value = (
        mock_db  # Makes client[database_name] return the fake database.
    )

    with patch.object(
        database, "get_settings", return_value=mock_settings
    ):  # Replaces get_settings with fake settings.
        with patch.object(
            database, "AsyncIOMotorClient", return_value=mock_client
        ) as mock_client_class:  # Replaces the Motor client constructor.
            with patch.object(
                database, "create_indexes", new_callable=AsyncMock
            ) as mock_create_indexes:  # Replaces index creation with an async mock.
                await (
                    database.connect_to_mongodb()
                )  # Runs the connection startup function.

    mock_client_class.assert_called_once_with(  # Verifies the Motor client was created with the expected options.
        mock_settings.mongo_uri,  # Confirms the configured MongoDB URI was used.
        serverSelectionTimeoutMS=5000,  # Confirms the timeout option was used.
        maxPoolSize=50,  # Confirms the pool size option was used.
    )  # Ends the client constructor assertion.
    mock_client.admin.command.assert_awaited_once_with(
        "ping"
    )  # Confirms startup verifies the MongoDB connection.
    mock_client.__getitem__.assert_called_once_with(
        mock_settings.mongo_db
    )  # Confirms the configured database name was selected.
    mock_create_indexes.assert_awaited_once()  # Confirms indexes are created during startup.


@pytest.mark.asyncio  # Marks this test as an async pytest test.
async def test_disconnect_from_mongo_closes_client_and_clears_references() -> (
    None
):  # Defines a test for shutdown cleanup.
    mock_client = MagicMock()  # Creates a fake MongoDB client.
    mock_db = MagicMock()  # Creates a fake MongoDB database.

    database._client = mock_client  # Directly sets the module-level client so the shutdown function can clear it.
    database._db = mock_db  # Directly sets the module-level database so the shutdown function can clear it.

    await database.disconnect_from_mongodb()  # Runs the shutdown function.

    mock_client.close.assert_called_once()  # Confirms the MongoDB client was closed.
    assert database._client is None  # Confirms the client reference was cleared.
    assert database._db is None  # Confirms the database reference was cleared.

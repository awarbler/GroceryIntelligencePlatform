# =============================================================================
# File: test_collection_data_access.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests collection-specific Data Access Layer helper methods.
# Security Note: Tests use fake in-memory data only and do not use secrets.
# SRS Traceability: Supports SRS v5.0 Section 19 database schema.
# SDD Traceability: Supports SDD v5.0 database design and backend modular architecture.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without runtime forward-reference issues.

# from typing import Any  # Imports Any because fake MongoDB documents contain mixed field types.

import pytest  # Imports pytest for async test markers.

from backend.data_access.ads import AdsDataAccess  # Imports ad data access.
from backend.data_access.coupons import CouponsDataAccess  # Imports coupon data access.
from backend.data_access.deal_matches import (
    DealMatchesDataAccess,
)  # Imports deal match data access.
from backend.data_access.products import (
    ProductsDataAccess,
)  # Imports product data access.
from backend.data_access.purchases import (
    PurchasesDataAccess,
)  # Imports purchase data access.
from backend.data_access.raw_inputs import (
    RawInputsDataAccess,
)  # Imports raw input data access.
from backend.data_access.rebates import RebatesDataAccess  # Imports rebate data access.
from backend.data_access.reward_accounts import (
    RewardAccountsDataAccess,
)  # Imports reward account data access.
from backend.data_access.reward_transactions import (
    RewardTransactionsDataAccess,
)  # Imports reward transaction access.
from backend.data_access.stores import StoresDataAccess  # Imports store data access.
from backend.data_access.users import UsersDataAccess  # Imports user data access.
from backend.database import ADS_COLLECTION  # Imports the ads collection name.
from backend.database import COUPONS_COLLECTION  # Imports the coupons collection name.
from backend.database import (
    DEAL_MATCHES_COLLECTION,
)  # Imports the deal matches collection name.
from backend.database import (
    PRODUCTS_COLLECTION,
)  # Imports the products collection name.
from backend.database import (
    PURCHASES_COLLECTION,
)  # Imports the purchases collection name.
from backend.database import (
    RAW_INPUTS_COLLECTION,
)  # Imports the raw inputs collection name.
from backend.database import REBATES_COLLECTION  # Imports the rebates collection name.
from backend.database import (
    REWARD_ACCOUNTS_COLLECTION,
)  # Imports the reward accounts collection name.
from backend.database import (
    REWARD_TRANSACTIONS_COLLECTION,
)  # Imports the reward transactions collection name.
from backend.database import STORES_COLLECTION  # Imports the stores collection name.
from backend.database import USERS_COLLECTION  # Imports the users collection name.
from backend.tests.data_access.test_base_data_access import (
    FakeCollection,
)  # Reuses the fake collection.


class FakeDatabase:  # Defines a fake MongoDB database.
    def __init__(self) -> None:  # Initializes fake database state.
        self.collections: dict[
            str, FakeCollection
        ] = {}  # Stores fake collections by collection name.

    def __getitem__(
        self, collection_name: str
    ) -> FakeCollection:  # Simulates database[collection_name].
        if (
            collection_name not in self.collections
        ):  # Checks whether the fake collection exists.
            self.collections[collection_name] = (
                FakeCollection()
            )  # Creates a fake collection when missing.
        return self.collections[collection_name]  # Returns the fake collection.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_users_find_by_username() -> None:  # Tests the users helper method.
    database = FakeDatabase()  # Creates a fake database.
    data_access = UsersDataAccess(database)  # Creates users data access.
    await data_access.create_one(
        {"username": "anita", "password_hash": "hashed"}
    )  # Inserts a fake user.
    result = await data_access.find_by_username(
        "anita"
    )  # Finds the fake user by username.
    assert result is not None  # Verifies a user was found.
    assert result["username"] == "anita"  # Verifies the username is correct.
    assert (
        USERS_COLLECTION in database.collections
    )  # Verifies the users collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_stores_find_by_store_id_and_list_active() -> (
    None
):  # Tests store helper methods.
    database = FakeDatabase()  # Creates a fake database.
    data_access = StoresDataAccess(database)  # Creates stores data access.
    await data_access.create_one(
        {"store_id": "heb", "active": True}
    )  # Inserts an active store.
    await data_access.create_one(
        {"store_id": "old", "active": False}
    )  # Inserts an inactive store.
    found_store = await data_access.find_by_store_id(
        "heb"
    )  # Finds the active store by store_id.
    active_stores = await data_access.list_active()  # Lists active stores.
    assert found_store is not None  # Verifies the store was found.
    assert found_store["store_id"] == "heb"  # Verifies the store_id is correct.
    assert len(active_stores) == 1  # Verifies only one active store was returned.
    assert (
        STORES_COLLECTION in database.collections
    )  # Verifies the stores collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_products_find_by_canonical_name_and_list_by_category() -> (
    None
):  # Tests product helper methods.
    database = FakeDatabase()  # Creates a fake database.
    data_access = ProductsDataAccess(database)  # Creates products data access.
    await data_access.create_one(
        {"canonical_name": "Tide Pods", "category": "Laundry"}
    )  # Inserts a laundry product.
    await data_access.create_one(
        {"canonical_name": "Febreze Spray", "category": "Air Care"}
    )  # Inserts an air care product.
    found_product = await data_access.find_by_canonical_name(
        "Tide Pods"
    )  # Finds the product by canonical name.
    laundry_products = await data_access.list_by_category(
        "Laundry"
    )  # Lists products by category.
    assert found_product is not None  # Verifies the product was found.
    assert (
        found_product["canonical_name"] == "Tide Pods"
    )  # Verifies the canonical name is correct.
    assert len(laundry_products) == 1  # Verifies only one laundry product was returned.
    assert (
        PRODUCTS_COLLECTION in database.collections
    )  # Verifies the products collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_purchases_list_by_filters() -> None:  # Tests purchase filtering.
    database = FakeDatabase()  # Creates a fake database.
    data_access = PurchasesDataAccess(database)  # Creates purchases data access.
    await data_access.create_one(
        {"store_ref": "heb", "category": "Food", "rebate_status": "PENDING"}
    )  # Inserts a match.
    await data_access.create_one(
        {"store_ref": "cvs", "category": "Personal Care", "rebate_status": "RECEIVED"}
    )  # Inserts non match.
    results = await data_access.list_by_filters(
        store_ref="heb", category="Food"
    )  # Lists filtered purchases.
    assert len(results) == 1  # Verifies one purchase matched.
    assert results[0]["store_ref"] == "heb"  # Verifies the store filter worked.
    assert (
        PURCHASES_COLLECTION in database.collections
    )  # Verifies the purchases collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_ads_list_valid_ads() -> None:  # Tests valid ad filtering.
    database = FakeDatabase()  # Creates a fake database.
    data_access = AdsDataAccess(database)  # Creates ads data access.
    await data_access.create_one(
        {"store_ref": "heb", "start_date": "2026-05-01", "end_date": "2026-05-31"}
    )  # Inserts valid ad.
    await data_access.create_one(
        {"store_ref": "heb", "start_date": "2026-04-01", "end_date": "2026-04-30"}
    )  # Inserts expired ad.
    results = await data_access.list_valid_ads(
        as_of_date="2026-05-14", store_ref="heb"
    )  # Lists valid ads.
    assert len(results) == 1  # Verifies one ad matched.
    assert results[0]["end_date"] == "2026-05-31"  # Verifies the valid ad was returned.
    assert (
        ADS_COLLECTION in database.collections
    )  # Verifies the ads collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_coupons_list_by_filters_excludes_expired() -> (
    None
):  # Tests coupon expiration filtering.
    database = FakeDatabase()  # Creates a fake database.
    data_access = CouponsDataAccess(database)  # Creates coupons data access.
    await data_access.create_one(
        {"item_name": "Active", "store_ref": "heb", "expiration_date": "2026-12-31"}
    )  # Inserts active coupon.
    await data_access.create_one(
        {"item_name": "Expired", "store_ref": "heb", "expiration_date": "2025-01-01"}
    )  # Inserts expired coupon.
    results = await data_access.list_by_filters(
        store_ref="heb", as_of_date="2026-05-14"
    )  # Lists active coupons.
    assert len(results) == 1  # Verifies one coupon matched.
    assert (
        results[0]["item_name"] == "Active"
    )  # Verifies the active coupon was returned.
    assert (
        COUPONS_COLLECTION in database.collections
    )  # Verifies the coupons collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_rebates_list_by_filters_and_update_status() -> (
    None
):  # Tests rebate helpers.
    database = FakeDatabase()  # Creates a fake database.
    data_access = RebatesDataAccess(database)  # Creates rebates data access.
    inserted_id = await data_access.create_one(
        {"company": "ibotta", "status": "PENDING"}
    )  # Inserts pending rebate.
    filtered_results = await data_access.list_by_filters(
        company="ibotta", status="PENDING"
    )  # Lists matching rebates.
    was_updated = await data_access.update_status(
        inserted_id, "SUBMITTED"
    )  # Updates rebate status.
    updated_document = await data_access.find_one_by_id(
        inserted_id
    )  # Reads updated rebate.
    assert len(filtered_results) == 1  # Verifies one rebate matched.
    assert was_updated is True  # Verifies the status update succeeded.
    assert updated_document is not None  # Verifies the updated rebate still exists.
    assert updated_document["status"] == "SUBMITTED"  # Verifies the status changed.
    assert (
        REBATES_COLLECTION in database.collections
    )  # Verifies the rebates collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_reward_accounts_find_by_program() -> (
    None
):  # Tests reward account helper.
    database = FakeDatabase()  # Creates a fake database.
    data_access = RewardAccountsDataAccess(
        database
    )  # Creates reward accounts data access.
    await data_access.create_one(
        {"program": "fetch", "balance": 1000}
    )  # Inserts fake reward account.
    result = await data_access.find_by_program(
        "fetch"
    )  # Finds reward account by program.
    assert result is not None  # Verifies the reward account was found.
    assert result["program"] == "fetch"  # Verifies the program is correct.
    assert (
        REWARD_ACCOUNTS_COLLECTION in database.collections
    )  # Verifies the reward accounts collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_reward_transactions_list_by_program() -> (
    None
):  # Tests reward transaction helper.
    database = FakeDatabase()  # Creates a fake database.
    data_access = RewardTransactionsDataAccess(
        database
    )  # Creates reward transactions data access.
    await data_access.create_one(
        {"program_ref": "fetch-id", "amount": 1000}
    )  # Inserts matching transaction.
    await data_access.create_one(
        {"program_ref": "ibotta-id", "amount": 1}
    )  # Inserts non matching transaction.
    results = await data_access.list_by_program(
        "fetch-id"
    )  # Lists transactions by program.
    assert len(results) == 1  # Verifies one transaction matched.
    assert (
        results[0]["program_ref"] == "fetch-id"
    )  # Verifies the program filter worked.
    assert (
        REWARD_TRANSACTIONS_COLLECTION in database.collections
    )  # Verifies reward transactions collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_deal_matches_find_by_week() -> None:  # Tests deal match helper.
    database = FakeDatabase()  # Creates a fake database.
    data_access = DealMatchesDataAccess(database)  # Creates deal matches data access.
    await data_access.create_one(
        {"week_of": "2026-05-04", "matches": []}
    )  # Inserts fake weekly match.
    result = await data_access.find_by_week("2026-05-04")  # Finds match by week.
    assert result is not None  # Verifies the weekly deal match was found.
    assert result["week_of"] == "2026-05-04"  # Verifies the week is correct.
    assert (
        DEAL_MATCHES_COLLECTION in database.collections
    )  # Verifies the deal matches collection was used.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_raw_inputs_list_by_store() -> None:  # Tests raw input helper.
    database = FakeDatabase()  # Creates a fake database.
    data_access = RawInputsDataAccess(database)  # Creates raw inputs data access.
    await data_access.create_one(
        {"store_ref": "heb", "raw_lines": ["line 1"]}
    )  # Inserts matching raw input.
    await data_access.create_one(
        {"store_ref": "cvs", "raw_lines": ["line 2"]}
    )  # Inserts non matching raw input.
    results = await data_access.list_by_store("heb")  # Lists raw inputs by store.
    assert len(results) == 1  # Verifies one raw input matched.
    assert results[0]["store_ref"] == "heb"  # Verifies the store filter worked.
    assert (
        RAW_INPUTS_COLLECTION in database.collections
    )  # Verifies the raw inputs collection was used.

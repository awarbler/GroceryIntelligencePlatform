# ==============================================================================
# File: database.py
# Project: GroceryIntelligence Platform
# Author: Anita Woodford
# Description: This file creates one shared async MongoDB client, exposes
# collection constants, creates, required indexes, and provides database helpers
# Security Note: This file never hardcodes database credentials or secrets.abs
# SRS Traceability Supports SRS v.5 section 25, RD-001, RD-002, RD-003, SE-004
# SDD traceability supports SDD v.5 database design and backend structure
# ==============================================================================

"""mongoDb database connection layer for Grocery intelligence platform
This module creates a shared async MongoDB client, exposes collection constants,
creates required indexes, and provides database helpers."""

# imports final for constants that should not be reassigned
from typing import Final

# imports the async mongo client for motor
from motor.motor_asyncio import AsyncIOMotorClient

# imports the async mongodb collection type
from motor.motor_asyncio import AsyncIOMotorCollection

# imports the async mongodb database type
from motor.motor_asyncio import AsyncIOMotorDatabase

# import the cache centralized settings getter
from backend.config import get_settings

# Collections for mongoDB
USERS_COLLECTION: Final[str] = "users"
STORES_COLLECTION: Final[str] = "stores"
PRODUCTS_COLLECTION: Final[str] = "products"
PURCHASES_COLLECTION: Final[str] = "purchases"
ADS_COLLECTION: Final[str] = "ads"
COUPONS_COLLECTION: Final[str] = "coupons"
REBATES_COLLECTION: Final[str] = "rebates"
REWARD_ACCOUNTS_COLLECTION: Final[str] = "reward_accounts"
REWARD_TRANSACTIONS_COLLECTION: Final[str] = "reward_transactions"
DEAL_MATCHES_COLLECTION: Final[str] = "deal_matches"
RAW_INPUTS_COLLECTION: Final[str] = "raw_inputs"

# define the approved MongoDB Collection names as a set for validation purposes
ALL_COLLECTIONS: Final[tuple[str, ...]] = (
    USERS_COLLECTION,
    STORES_COLLECTION,
    PRODUCTS_COLLECTION,
    PURCHASES_COLLECTION,
    ADS_COLLECTION,
    COUPONS_COLLECTION,
    REBATES_COLLECTION,
    REWARD_ACCOUNTS_COLLECTION,
    REWARD_TRANSACTIONS_COLLECTION,
    DEAL_MATCHES_COLLECTION,
    RAW_INPUTS_COLLECTION,
)

# startup code to create a shared async MongoDB client and database instance
_client: AsyncIOMotorClient | None = None  # stores the shared MongoDB client instance
_db: AsyncIOMotorDatabase | None = None  # stores the shared MongoDB database instance


# function to startup Mongodb
async def connect_to_mongodb() -> None:
    """Initializes the MongoDB client and database connection. Creates the shared
    client, verify the connection, and creates indexes."""
    global _client  # allows the function to assign the module level client
    global _db  # allows the function to assign the module level database instance

    if _client is not None and _db is not None:
        return  # Already connected

    settings = get_settings()  # load the cached env setting from backend config

    _client = AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000,  # 5 second timeout for server selection
        maxPoolSize=50,  # maximum number of connections in the pool)
    )

    # verifies mongodb is reachable during startup
    await _client.admin.command("ping")
    # select the configure application database
    _db = _client[settings.mongo_db]
    # creates the required indexes after the database is selected
    await create_indexes()


# define shutdown function to close the MongoDB client connection
async def disconnect_from_mongodb() -> None:
    """Closes the MongoDB client connection and clear the database reference."""
    global _client  # allows the function to access the module level client
    global _db  # allows the function to access the module level database instance
    if _client is not None:  # checks if a client exists before attempting to close
        _client.close()  # closes the MongoDB client connection
    _client = None  # clear the client reference
    _db = None  # clear the database reference


# define the database dependency helper functions
def get_db() -> AsyncIOMotorDatabase:
    """Returns the shared MongoDB database instance. Raises an error if not connected."""
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_to_mongodb first.")
    return _db


# define the approved collection helper
def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """Returns the specified collection from the MongoDB database. Validates the collection name."""
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_to_mongodb first.")

    # collection name outside of schema
    if collection_name not in ALL_COLLECTIONS:
        raise ValueError(
            f"Invalid collection name: {collection_name}. Must be one of {ALL_COLLECTIONS}"
        )

    return _db[collection_name]  # return the requested collection


# define startup index creation function
async def create_indexes() -> None:
    """Creates the required indexes for the MongoDB collections. This function is called during startup."""
    if _db is None:  # check if mongodb is connected
        raise RuntimeError("Database not connected. Call connect_to_mongodb first.")

    # create indexes for users collection
    # await _db[USERS_COLLECTION].create_index("email", unique=True) # unique index on email for user lookup
    # await _db[USERS_COLLECTION].create_index("created_at") # index on created_at for sorting and querying

    # create indexes for products collection
    # await _db[PRODUCTS_COLLECTION].create_index("upc", unique=True) # unique index on upc for product lookup
    # await _db[PRODUCTS_COLLECTION].create_index("name") # index on name for search

    # create indexes for purchases collection
    # await _db[PURCHASES_COLLECTION].create_index("user_id") # index on user_id for purchase history lookup
    await _db[PURCHASES_COLLECTION].create_index(
        "store_ref"
    )  # index on product_id for purchase history lookup
    await _db[PURCHASES_COLLECTION].create_index(
        "purchase_date"
    )  # index on purchase_date for sorting and querying
    await _db[COUPONS_COLLECTION].create_index(
        "expiration_date"
    )  # index on expiration_date for sorting and querying
    await _db[REBATES_COLLECTION].create_index(
        "status"
    )  # index on status for sorting and querying
    await _db[PRODUCTS_COLLECTION].create_index(
        "canonical_name"
    )  # index on canonical_name for product lookup and search
    await _db[PRODUCTS_COLLECTION].create_index(
        "normalized_name"
    )  # index on normalized_name for product lookup by store
    await _db[DEAL_MATCHES_COLLECTION].create_index(
        "store_ref"
    )  # index on match_date for sorting and querying
    await _db[RAW_INPUTS_COLLECTION].create_index(
        "timestamp"
    )  # index on timestamp for sorting and querying
    # create indexes for ads collection
    # await _db[AD_COLLECTION].create_index("product_id") # index on product_id for ad lookup
    # await _db[AD_COLLECTION].create_index("store_id") # index on store_id for ad lookup

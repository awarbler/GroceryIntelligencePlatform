# =============================================================================
# File: test_base_data_access.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests shared Data Access Layer CRUD behavior with fake async MongoDB objects.
# Security Note: Tests use fake in-memory data only and do not use secrets.
# SRS Traceability: Supports SRS v5.0 SE-009, PL-032, PL-033, CP-018, and Section 19.
# SDD Traceability: Supports SDD v5.0 database design and backend modular architecture.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables modern type hints without runtime forward-reference issues.

from typing import (
    Any,
)  # Imports Any because fake MongoDB documents contain mixed field types.

import pytest  # Imports pytest for assertions and async test markers.
from bson import ObjectId  # Imports ObjectId for fake MongoDB document IDs.

from backend.data_access.base import (
    MongoDataAccess,
)  # Imports the shared Data Access Layer helper.
from backend.data_access.base import (
    normalize_object_id,
)  # Imports the ObjectId validation helper.


class FakeInsertResult:  # Defines a fake Motor insert result.
    def __init__(self, inserted_id: ObjectId) -> None:  # Receives the fake inserted ID.
        self.inserted_id = inserted_id  # Stores the fake inserted ID.


class FakeUpdateResult:  # Defines a fake Motor update result.
    def __init__(
        self, modified_count: int
    ) -> None:  # Receives the fake modified count.
        self.modified_count = modified_count  # Stores the fake modified count.


class FakeDeleteResult:  # Defines a fake Motor delete result.
    def __init__(self, deleted_count: int) -> None:  # Receives the fake deleted count.
        self.deleted_count = deleted_count  # Stores the fake deleted count.


class FakeCursor:  # Defines a fake async MongoDB cursor.
    def __init__(
        self, documents: list[dict[str, Any]]
    ) -> None:  # Receives fake result documents.
        self.documents = documents  # Stores fake result documents.

    def skip(self, skip_count: int) -> FakeCursor:  # Simulates Motor cursor skip.
        self.documents = self.documents[skip_count:]  # Removes skipped documents.
        return self  # Returns self for chained cursor calls.

    def limit(self, limit_count: int) -> FakeCursor:  # Simulates Motor cursor limit.
        self.documents = self.documents[:limit_count]  # Applies the requested limit.
        return self  # Returns self for chained cursor calls.

    async def to_list(
        self, length: int
    ) -> list[dict[str, Any]]:  # Simulates async cursor materialization.
        return self.documents[:length]  # Returns the requested number of documents.


class FakeCollection:  # Defines a fake async MongoDB collection.
    def __init__(self) -> None:  # Initializes fake collection state.
        self.documents: dict[
            ObjectId, dict[str, Any]
        ] = {}  # Stores fake documents by ObjectId.

    async def insert_one(
        self, document: dict[str, Any]
    ) -> FakeInsertResult:  # Simulates insert_one.
        object_id = ObjectId()  # Creates a fake MongoDB ObjectId.
        stored_document = dict(document)  # Copies the inserted document.
        stored_document["_id"] = object_id  # Adds the fake MongoDB ID.
        self.documents[object_id] = stored_document  # Stores the fake document.
        return FakeInsertResult(object_id)  # Returns the fake insert result.

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents.values():
            if self._matches_query(document, query):
                return document
        return None

    def _matches_query(self, document: dict[str, Any], query: dict[str, Any]) -> bool:

        for key, expected in query.items():
            actual = document.get(key)

            if isinstance(expected, dict):
                if actual is None:
                    return False

                for operator, bound in expected.items():
                    if operator == "$gte":
                        if not (actual >= bound):
                            return False
                    elif operator == "$lte":
                        if not (actual <= bound):
                            return False
                    elif operator == "$gt":
                        if not (actual > bound):
                            return False
                    elif operator == "$lt":
                        if not (actual < bound):
                            return False
                    else:
                        return False  # Unsupported operator
            else:
                if actual != expected:
                    return False
        return True

    def find(self, filters: dict[str, Any]) -> FakeCursor:  # Simulates find.
        if not filters:  # Checks whether no filters were supplied.
            return FakeCursor(
                list(self.documents.values())
            )  # Returns all fake documents.

        matches = [  # Builds a list of matching fake documents.
            document  # Keeps the current document when it matches.
            for document in self.documents.values()  # Iterates through stored fake documents.
            if self._matches_query(
                document, filters
            )  # Uses the same query matching logic as find_one.
            # if all(document.get(key) == value for key, value in filters.items())  # Requires all filters to match.
        ]  # Ends the matching document list.
        return FakeCursor(matches)  # Returns the fake cursor.

    async def update_one(
        self, query: dict[str, Any], update: dict[str, Any]
    ) -> FakeUpdateResult:  # Simulates update_one.
        object_id = query["_id"]  # Reads the requested ObjectId.
        if object_id not in self.documents:  # Checks whether the document exists.
            return FakeUpdateResult(0)  # Reports that no document was modified.
        self.documents[object_id].update(update["$set"])  # Applies the fake update.
        return FakeUpdateResult(1)  # Reports that one document was modified.

    async def delete_one(
        self, query: dict[str, Any]
    ) -> FakeDeleteResult:  # Simulates delete_one.
        object_id = query["_id"]  # Reads the requested ObjectId.
        if object_id not in self.documents:  # Checks whether the document exists.
            return FakeDeleteResult(0)  # Reports that no document was deleted.

        del self.documents[object_id]  # Deletes the fake document.
        return FakeDeleteResult(1)  # Reports that one document was deleted.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_create_one_and_find_one_by_id() -> (
    None
):  # Tests create and read behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    inserted_id = await data_access.create_one(
        {"name": "HEB", "active": True}
    )  # Inserts one fake document.
    found_document = await data_access.find_one_by_id(
        inserted_id
    )  # Reads the inserted fake document.
    assert found_document is not None  # Verifies a document was found.
    assert found_document["name"] == "HEB"  # Verifies the stored name is correct.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_find_one_by_id_returns_none_for_missing_id() -> (
    None
):  # Tests missing ID behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    result = await data_access.find_one_by_id(
        "000000000000000000000001"
    )  # Looks up a valid but missing ID.
    assert result is None  # Verifies missing documents return None.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_find_one_by_id_returns_none_for_invalid_id() -> (
    None
):  # Tests invalid ID behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    result = await data_access.find_one_by_id(
        "not-valid"
    )  # Looks up an invalid ObjectId string.
    assert result is None  # Verifies invalid IDs return None.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_list_records_no_filter_returns_all_documents() -> (
    None
):  # Tests unfiltered list behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    await data_access.create_one({"store": "heb"})  # Inserts the first fake document.
    await data_access.create_one({"store": "cvs"})  # Inserts the second fake document.
    results = await data_access.list_records()  # Lists all fake documents.
    assert len(results) == 2  # Verifies both documents are returned.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_list_records_with_filter_returns_matching_documents() -> (
    None
):  # Tests filtered list behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    await data_access.create_one(
        {"store": "heb", "active": True}
    )  # Inserts a matching fake document.
    await data_access.create_one(
        {"store": "cvs", "active": True}
    )  # Inserts a non matching fake document.
    results = await data_access.list_records(
        {"store": "heb"}
    )  # Lists fake documents matching the store.
    assert len(results) == 1  # Verifies only one document matched.
    assert results[0]["store"] == "heb"  # Verifies the matching document is correct.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_update_one_by_id_modifies_document() -> None:  # Tests update behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    inserted_id = await data_access.create_one(
        {"status": "PENDING"}
    )  # Inserts one fake document.
    was_updated = await data_access.update_one_by_id(
        inserted_id, {"status": "RECEIVED"}
    )  # Updates the document.
    found_document = await data_access.find_one_by_id(
        inserted_id
    )  # Reads the updated document.
    assert was_updated is True  # Verifies the update returned True.
    assert found_document is not None  # Verifies the document still exists.
    assert found_document["status"] == "RECEIVED"  # Verifies the update was applied.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_update_one_by_id_returns_false_for_missing_id() -> (
    None
):  # Tests missing update behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    result = await data_access.update_one_by_id(
        "000000000000000000000001", {"x": 1}
    )  # Updates a missing ID.
    assert result is False  # Verifies missing documents return False.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_update_one_by_id_strips_id_from_updates() -> (
    None
):  # Tests `_id` update protection.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    inserted_id = await data_access.create_one(
        {"name": "original"}
    )  # Inserts one fake document.
    was_updated = await data_access.update_one_by_id(
        inserted_id, {"name": "changed", "_id": "bad"}
    )  # Updates safely.
    found_document = await data_access.find_one_by_id(
        inserted_id
    )  # Reads the updated fake document.
    assert was_updated is True  # Verifies the safe update returned True.
    assert found_document is not None  # Verifies the document still exists.
    assert found_document["name"] == "changed"  # Verifies the allowed field changed.
    assert isinstance(
        found_document["_id"], ObjectId
    )  # Verifies the ObjectId was not overwritten.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_update_one_by_id_returns_false_when_only_id_is_supplied() -> (
    None
):  # Tests empty safe update behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    inserted_id = await data_access.create_one(
        {"name": "original"}
    )  # Inserts one fake document.
    result = await data_access.update_one_by_id(
        inserted_id, {"_id": "bad"}
    )  # Attempts an unsafe-only update.
    assert result is False  # Verifies no update occurs when only `_id` is supplied.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_delete_one_by_id_removes_document() -> None:  # Tests delete behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    inserted_id = await data_access.create_one(
        {"name": "delete me"}
    )  # Inserts one fake document.
    was_deleted = await data_access.delete_one_by_id(
        inserted_id
    )  # Deletes the fake document.
    found_document = await data_access.find_one_by_id(
        inserted_id
    )  # Attempts to read the deleted document.
    assert was_deleted is True  # Verifies the delete returned True.
    assert found_document is None  # Verifies the document no longer exists.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_delete_one_by_id_returns_false_for_missing_id() -> (
    None
):  # Tests missing delete behavior.
    data_access = MongoDataAccess(
        FakeCollection()
    )  # Creates the data access helper with a fake collection.
    result = await data_access.delete_one_by_id(
        "000000000000000000000001"
    )  # Deletes a missing ID.
    assert result is False  # Verifies missing documents return False.


def test_normalize_object_id_accepts_valid_string() -> (
    None
):  # Tests valid string ObjectId behavior.
    object_id_string = str(ObjectId())  # Creates a valid ObjectId string.
    result = normalize_object_id(
        object_id_string
    )  # Normalizes the valid ObjectId string.
    assert isinstance(result, ObjectId)  # Verifies the result is an ObjectId.


def test_normalize_object_id_accepts_object_id_instance() -> (
    None
):  # Tests ObjectId passthrough behavior.
    object_id = ObjectId()  # Creates an ObjectId instance.
    result = normalize_object_id(object_id)  # Normalizes the ObjectId instance.
    assert result is object_id  # Verifies the same ObjectId instance is returned.


def test_normalize_object_id_rejects_invalid_string() -> (
    None
):  # Tests invalid ObjectId behavior.
    with pytest.raises(
        ValueError
    ):  # Expects invalid ObjectId strings to raise ValueError.
        normalize_object_id(
            "not-a-valid-id"
        )  # Attempts to normalize an invalid string.

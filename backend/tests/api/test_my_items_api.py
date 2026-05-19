# =============================================================================
# File: test_my_items_api.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests P1-15 My Items CRUD API routes and service behavior.
# Security Note: Tests use synthetic data only.
# SRS Traceability: Supports SRS v5.0 Section 18 MI-001 through MI-004.
# SDD Traceability: Supports SDD v5.0 Section 7.3 products and Section 8 API Endpoint Design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints.

from decimal import Decimal  # Imports Decimal for average price test values.
from pathlib import Path  # Imports Path for architecture boundary source-code checks.
from unittest.mock import AsyncMock  # Imports AsyncMock for async service and DAL mocks.
from unittest.mock import MagicMock  # Imports MagicMock for service and DAL test doubles.

import pytest  # Imports pytest for async test support.
from fastapi.testclient import TestClient  # Imports FastAPI test client.

from backend.api.my_items import get_my_items_service  # Imports dependency override target.
from backend.main import app  # Imports FastAPI app for endpoint tests.
from backend.services.my_items_service import MyItemNotFoundError  # Imports service not-found error.
from backend.services.my_items_service import MyItemService  # Imports service class under test.


def _make_client_with_service(service: MyItemService) -> TestClient:  # Creates a test client with overridden service dependency.
    app.dependency_overrides[get_my_items_service] = lambda: service  # Overrides real service dependency with fake service.
    return TestClient(app)  # Returns configured FastAPI test client.


def _clear_overrides() -> None:  # Clears FastAPI dependency overrides after each test.
    app.dependency_overrides.clear()  # Removes dependency overrides to avoid leaking state between tests.


def _fake_service() -> MagicMock:  # Builds a fake MyItemService for route tests.
    service = MagicMock(spec=MyItemService)  # Creates a mock that matches MyItemService methods.
    service.list_my_items = AsyncMock(return_value=[])  # Adds default async list behavior.
    service.create_my_item = AsyncMock(return_value={"id": "item-1", "is_my_item": True})  # Adds default async create behavior.
    service.update_my_item = AsyncMock(return_value={"id": "item-1", "preferred_stores": ["heb"]})  # Adds default async update behavior.
    service.delete_my_item = AsyncMock(return_value={"deleted": True})  # Adds default async delete behavior.
    service.update_avg_price_after_purchase = AsyncMock(return_value=True)  # Adds default async average update behavior.
    return service  # Returns fake service.


def _valid_create_payload() -> dict[str, object]:  # Builds a valid create request payload.
    return {  # Starts valid request body.
        "item_name": "Milk",  # Provides owner-facing item name.
        "canonical_name": "H-E-B Whole Milk",  # Provides normalized item name.
        "category": "dairy",  # Provides product category.
        "brand": "H-E-B",  # Provides optional brand.
        "size": "1 gallon",  # Provides optional package size.
        "avg_price": "3.48",  # Provides optional average price as JSON-safe string.
        "acceptable_substitutes": [],  # Provides substitutes as a list.
        "preferred_stores": ["heb"],  # Provides preferred stores as a list.
        "notes": "weekly item",  # Provides optional notes.
    }  # Ends valid request body.


def test_list_my_items_returns_success_response() -> None:  # Tests GET /api/v1/my-items.
    service = _fake_service()  # Creates fake service.
    service.list_my_items = AsyncMock(return_value=[{"id": "item-1", "is_my_item": True}])  # Configures list result.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.get("/api/v1/my-items")  # Calls list endpoint.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 200  # Verifies successful HTTP status.
    assert response.json()["success"] is True  # Verifies standard success wrapper.
    assert response.json()["meta"]["count"] == 1  # Verifies count metadata.
    service.list_my_items.assert_awaited_once_with(skip=0, limit=100)  # Verifies pagination defaults are passed.


def test_list_my_items_passes_skip_and_limit() -> None:  # Tests GET pagination parameters.
    service = _fake_service()  # Creates fake service.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.get("/api/v1/my-items?skip=5&limit=10")  # Calls endpoint with pagination.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 200  # Verifies successful HTTP status.
    service.list_my_items.assert_awaited_once_with(skip=5, limit=10)  # Verifies pagination values are passed.


def test_create_my_item_returns_created_item() -> None:  # Tests POST /api/v1/my-items.
    service = _fake_service()  # Creates fake service.
    service.create_my_item = AsyncMock(return_value={"id": "item-1", "item_name": "Milk", "is_my_item": True})  # Configures create result.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.post("/api/v1/my-items", json=_valid_create_payload())  # Calls create endpoint.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 201  # Verifies created HTTP status.
    assert response.json()["data"]["is_my_item"] is True  # Verifies response contains My Item flag.
    sent_payload = service.create_my_item.await_args.args[0]  # Reads payload sent to service.
    assert isinstance(sent_payload["acceptable_substitutes"], list)  # Verifies substitutes remain a list.
    assert isinstance(sent_payload["preferred_stores"], list)  # Verifies preferred stores remain a list.


def test_create_my_item_rejects_missing_item_name() -> None:  # Tests create validation.
    service = _fake_service()  # Creates fake service.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.post("/api/v1/my-items", json={"canonical_name": "Milk"})  # Sends incomplete payload.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 422  # Verifies validation failure.
    service.create_my_item.assert_not_called()  # Verifies service was not called.


def test_update_my_item_returns_updated_item() -> None:  # Tests PATCH /api/v1/my-items/{item_id}.
    service = _fake_service()  # Creates fake service.
    service.update_my_item = AsyncMock(return_value={"id": "item-1", "preferred_stores": ["heb", "walmart"]})  # Configures update result.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.patch("/api/v1/my-items/item-1", json={"preferred_stores": ["heb", "walmart"]})  # Calls update endpoint.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 200  # Verifies successful HTTP status.
    assert response.json()["data"]["preferred_stores"] == ["heb", "walmart"]  # Verifies updated field.
    service.update_my_item.assert_awaited_once_with("item-1", {"preferred_stores": ["heb", "walmart"]})  # Verifies service call.


def test_update_my_item_returns_404_when_missing() -> None:  # Tests update not-found behavior.
    service = _fake_service()  # Creates fake service.
    service.update_my_item = AsyncMock(side_effect=MyItemNotFoundError("item-404"))  # Configures not-found error.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.patch("/api/v1/my-items/item-404", json={"notes": "missing"})  # Calls update endpoint.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 404  # Verifies not-found HTTP status.


def test_delete_my_item_returns_deleted_flag() -> None:  # Tests DELETE /api/v1/my-items/{item_id}.
    service = _fake_service()  # Creates fake service.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.delete("/api/v1/my-items/item-1")  # Calls delete endpoint.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 200  # Verifies successful HTTP status.
    assert response.json()["data"]["deleted"] is True  # Verifies delete flag.
    service.delete_my_item.assert_awaited_once_with("item-1")  # Verifies service call.


def test_delete_my_item_returns_404_when_missing() -> None:  # Tests delete not-found behavior.
    service = _fake_service()  # Creates fake service.
    service.delete_my_item = AsyncMock(side_effect=MyItemNotFoundError("item-404"))  # Configures not-found error.
    client = _make_client_with_service(service)  # Creates client using fake service.
    response = client.delete("/api/v1/my-items/item-404")  # Calls delete endpoint.
    _clear_overrides()  # Clears dependency overrides.
    assert response.status_code == 404  # Verifies not-found HTTP status.


@pytest.mark.asyncio  # Marks test as async.
async def test_service_create_forces_is_my_item_true() -> None:  # Tests service create behavior.
    dal = MagicMock()  # Creates fake products DAL.
    dal.create_my_item = AsyncMock(return_value="item-1")  # Configures create result.
    dal.find_my_item_by_id = AsyncMock(return_value={"_id": "item-1", "item_name": "Milk", "is_my_item": True})  # Configures lookup result.
    service = MyItemService(dal)  # Creates service with fake DAL.
    result = await service.create_my_item(_valid_create_payload())  # Calls service create.
    created_document = dal.create_my_item.await_args.args[0]  # Reads document sent to DAL.
    assert created_document["is_my_item"] is True  # Verifies service forces My Item flag.
    assert result["id"] == "item-1"  # Verifies serialized id.


@pytest.mark.asyncio  # Marks test as async.
async def test_service_update_removes_immutable_fields() -> None:  # Tests safe update behavior.
    dal = MagicMock()  # Creates fake products DAL.
    dal.update_my_item = AsyncMock(return_value=True)  # Configures update result.
    dal.find_my_item_by_id = AsyncMock(return_value={"_id": "item-1", "is_my_item": True})  # Configures lookup result.
    service = MyItemService(dal)  # Creates service with fake DAL.
    await service.update_my_item("item-1", {"is_my_item": False, "created_at": "bad", "notes": "ok"})  # Calls update.
    updates = dal.update_my_item.await_args.args[1]  # Reads updates sent to DAL.
    assert "is_my_item" not in updates  # Verifies immutable flag was removed.
    assert "created_at" not in updates  # Verifies created timestamp was removed.
    assert updates["notes"] == "ok"  # Verifies editable field remains.


@pytest.mark.asyncio  # Marks test as async.
async def test_service_updates_avg_price_after_purchase() -> None:  # Tests average price delegation.
    dal = MagicMock()  # Creates fake products DAL.
    dal.update_my_item_avg_price = AsyncMock(return_value=True)  # Configures average update result.
    service = MyItemService(dal)  # Creates service with fake DAL.
    result = await service.update_avg_price_after_purchase("H-E-B Whole Milk", Decimal("3.48"))  # Calls average update.
    assert result is True  # Verifies successful result.
    dal.update_my_item_avg_price.assert_awaited_once_with("H-E-B Whole Milk", Decimal("3.48"))  # Verifies DAL call.


def test_route_file_has_no_direct_mongo_calls() -> None:  # Tests route architecture boundary.
    source = Path("backend/api/my_items.py").read_text(encoding="utf-8")  # Reads route source.
    assert "find_one(" not in source  # Verifies no direct Mongo find call.
    assert "insert_one(" not in source  # Verifies no direct Mongo insert call.
    assert "update_one(" not in source  # Verifies no direct Mongo update call.
    assert "delete_one(" not in source  # Verifies no direct Mongo delete call.
    assert "pymongo" not in source  # Verifies no pymongo import.
    assert "motor.motor_asyncio" not in source  # Verifies no Motor import in route file.


def test_service_file_has_no_direct_mongo_calls() -> None:  # Tests service architecture boundary.
    source = Path("backend/services/my_items_service.py").read_text(encoding="utf-8")  # Reads service source.
    assert "find_one(" not in source  # Verifies no direct Mongo find call.
    assert "insert_one(" not in source  # Verifies no direct Mongo insert call.
    assert "update_one(" not in source  # Verifies no direct Mongo update call.
    assert "delete_one(" not in source  # Verifies no direct Mongo delete call.
    assert "pymongo" not in source  # Verifies no pymongo import.
    assert "motor.motor_asyncio" not in source  # Verifies no Motor import in service file.
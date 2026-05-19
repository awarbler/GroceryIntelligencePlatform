# =============================================================================  # Starts the file header.
# File: tests/api/test_coupons_api.py  # Identifies the test file.
# Project: Grocery Intelligence Platform  # Identifies the project.
# Description: Tests manual H-E-B coupon CRUD API endpoints without using real MongoDB.  # Explains the file purpose.
# =============================================================================  # Ends the file header.

from collections.abc import Generator  # Imports Generator for the pytest fixture return type.

import pytest  # Imports pytest for fixtures and monkeypatch support.
from fastapi.testclient import TestClient  # Imports FastAPI's synchronous test client.

from backend.api import coupons as coupons_api  # Imports the coupon API module so its get_db dependency can be overridden.
from backend.main import app  # Imports the FastAPI app under test.
from backend.services import coupon_service  # Imports coupon service functions so tests can monkeypatch them.


class FakeCollection:  # Defines a fake MongoDB collection object for DAL construction.
    """Fake collection used only so CouponsDataAccess can be constructed."""  # Explains the fake class purpose.

    pass  # No collection methods are needed because service calls are monkeypatched.


class FakeDatabase:  # Defines a fake database object for dependency override.
    """Fake database that supports database[collection_name] access."""  # Explains the fake database purpose.

    def __getitem__(self, collection_name: str) -> FakeCollection:  # Supports Mongo-style database["collection"] access.
        return FakeCollection()  # Returns a fake collection for the DAL constructor.


def override_get_db() -> FakeDatabase:  # Defines the replacement database dependency.
    return FakeDatabase()  # Returns the fake database instead of real MongoDB.


@pytest.fixture(autouse=True)  # Runs this fixture automatically for every test in this file.
def override_database_dependency() -> Generator[None]:  # Defines a fixture that installs and removes the dependency override.
    app.dependency_overrides[coupons_api.get_db] = override_get_db  # Replaces the route's real database dependency.
    yield  # Runs the test while the dependency override is active.
    app.dependency_overrides.clear()  # Clears overrides so this test file does not affect other tests.


client = TestClient(app)  # Creates the FastAPI test client.


VALID_COUPON = {  # Defines one valid manual H-E-B coupon payload.
    "store_ref": "507f1f77bcf86cd799439011",  # Provides a valid ObjectId-shaped store reference.
    "coupon_type": "STORE_DIGITAL",  # Uses a valid CouponType enum value.
    "coupon_scope": "ITEM",  # Uses an item-level coupon scope.
    "is_store_coupon": True,  # Marks the coupon as store-issued.
    "is_manufacturer_coupon": False,  # Marks the coupon as not manufacturer-issued.
    "expiration_date": "2026-06-01",  # Provides the required expiration date.
    "item_name": "H-E-B Trail Mix",  # Provides the qualifying item name.
    "discount_amount": "1.00",  # Provides a dollar discount amount.
    "discount_type": "dollars",  # Tells the model this is a dollar-value coupon.
}  # Ends the valid coupon payload.


def test_create_coupon_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:  # Tests successful coupon creation.
    async def fake_create_coupon(dal: object, coupon: object) -> str:  # Defines a fake async create service.
        return "507f1f77bcf86cd799439012"  # Returns a stable fake coupon id.

    monkeypatch.setattr(coupon_service, "create_coupon", fake_create_coupon)  # Replaces the real service create function.

    response = client.post(  # Sends a POST request to the coupon endpoint.
        "/api/v1/coupons",  # Uses the coupon creation route.
        json=VALID_COUPON,  # Sends the valid coupon JSON body.
    )  # Ends the POST request.

    assert response.status_code == 200  # Verifies the endpoint accepted the coupon.

    body = response.json()  # Reads the JSON response body.

    assert body["coupon_id"] == "507f1f77bcf86cd799439012"  # Verifies the returned coupon id.


def test_create_coupon_requires_expiration_date() -> None:  # Tests required expiration validation.
    invalid_coupon = VALID_COUPON.copy()  # Copies the valid payload so the original stays unchanged.

    invalid_coupon.pop("expiration_date")  # Removes the required expiration date.

    response = client.post(  # Sends a POST request with invalid coupon data.
        "/api/v1/coupons",  # Uses the coupon creation route.
        json=invalid_coupon,  # Sends the invalid coupon JSON body.
    )  # Ends the POST request.

    assert response.status_code == 422  # Verifies Pydantic rejects the missing required field.


def test_get_coupons_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:  # Tests coupon listing response format.
    async def fake_list_coupons(  # Defines a fake async list service.
        dal: object,  # Accepts the DAL argument from the route.
        include_expired: bool = False,  # Accepts the include_expired value.
        store_ref: str | None = None,  # Accepts the optional store filter.
        skip: int = 0,  # Accepts the pagination skip value.
        limit: int = 100,  # Accepts the pagination limit value.
    ) -> list[dict[str, str]]:  # Returns fake coupon records.
        return [{"item_name": "H-E-B Trail Mix"}]  # Returns one fake active coupon.

    monkeypatch.setattr(coupon_service, "list_coupons", fake_list_coupons)  # Replaces real service call.

    response = client.get("/api/v1/coupons")  # Sends GET request.

    assert response.status_code == 200  # Verifies successful response.

    body = response.json()  # Reads response JSON.

    assert body["success"] is True  # Verifies standard success flag.

    assert body["data"][0]["item_name"] == "H-E-B Trail Mix"  # Verifies coupon data.

    assert body["meta"]["count"] == 1  # Verifies response metadata count.

def test_delete_coupon_returns_deleted_flag(monkeypatch: pytest.MonkeyPatch) -> None:  # Tests coupon deletion.
    async def fake_delete_coupon(dal: object, coupon_id: str) -> bool:  # Defines a fake async delete service.
        return True  # Simulates a successful deletion.

    monkeypatch.setattr(coupon_service, "delete_coupon", fake_delete_coupon)  # Replaces the real service delete function.

    response = client.delete(  # Sends a DELETE request to the coupon endpoint.
        "/api/v1/coupons/507f1f77bcf86cd799439012"  # Uses a fake valid ObjectId-shaped coupon id.
    )  # Ends the DELETE request.

    assert response.status_code == 200  # Verifies the endpoint responds successfully.

    assert response.json()["deleted"] is True  # Verifies the response reports deletion.
    
def test_get_coupons_excludes_expired_by_default(monkeypatch: pytest.MonkeyPatch) -> None:  # Tests default expired coupon filtering.
    captured_include_expired = {}  # Stores the include_expired value passed to the service.

    async def fake_list_coupons(  # Defines a fake async list service.
        dal: object,  # Accepts the DAL argument from the route.
        include_expired: bool = False,  # Accepts the include_expired query value.
        store_ref: str | None = None,  # Accepts the optional store filter.
        skip: int = 0,  # Accepts pagination skip.
        limit: int = 100,  # Accepts pagination limit.
    ) -> list[dict[str, str]]:  # Returns fake filtered coupon records.
        captured_include_expired["value"] = include_expired  # Records whether expired coupons were requested.
        return [{"item_name": "Active Coupon", "expiration_date": "2026-06-01"}]  # Returns only active coupon.

    monkeypatch.setattr(coupon_service, "list_coupons", fake_list_coupons)  # Replaces real service call.

    response = client.get("/api/v1/coupons")  # Calls endpoint without include_expired.

    assert response.status_code == 200  # Verifies successful response.

    assert captured_include_expired["value"] is False  # Verifies expired coupons are excluded by default.

    assert response.json()["data"][0]["item_name"] == "Active Coupon"  # Verifies active coupon data returned.
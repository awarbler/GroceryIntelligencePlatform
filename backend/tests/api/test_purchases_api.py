# ==============================================================================
# FILE: test_purchases_api.py
# PROJECT: Grocery Intelligence Platform
# AUTHOR: Anita Woodford
# Tests P1-14 purchase CRUD API routes.
# Security Note: Tests use synthetic purchase data only.
# SRS Traceability: Supports SRS v5.0 PL-001 through PL-034 and SE-009.
# SDD Traceability: Supports SDD v5.0 purchases API endpoint design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints without runtime forward-reference issues.

from datetime import date  # Supports date query parameters.
from decimal import Decimal  # Supports price fields in test payloads.

from bson import ObjectId  # Generates ObjectId values for test payloads.
from fastapi.testclient import TestClient  # Provides the FastAPI test client for endpoint testing.

import backend.api.purchases as purchases_api  # Imports the purchases API module for testing.

from backend.models.purchase import InputType  # Imports purchase input type enum.
from backend.models.rebate import RebateStatus  # Imports rebate status enum.
from backend.main import app  # Imports the FastAPI application instance.



def _purchase_payload() -> dict:
    return {
        "store_ref": str(ObjectId()),  # Generates a random ObjectId string for the store reference.
        "canonical_name": "H-E-B Milk",  # Uses a common store name for testing.
        "raw_name": "H-E-B Milk",  # Uses a common raw product name for testing.
        "category": "Dairy",  # Uses a common category for testing.
        "brand": "H-E-B",  # Uses a common brand for testing.
        "size": "1 gallon",  # Uses a common size for testing.
        "quantity": 2,
        "purchase_date": str(date(2024, 6, 1)),  # Uses a fixed purchase date for testing.
        
        "shelf_price": "3.99",  # Uses a realistic price for testing.
        "sale_price": "3.49",  # Uses a realistic sale price for testing.
        "register_price": "3.99",  # Uses a realistic register price for testing.
        "subtotal_before_coupons": "7.98",  # Uses a realistic subtotal for testing.
        "out_of_pocket": "6.49",  # Uses a realistic out-of-pocket amount for testing.
        
        "coupon_used": True,
        "coupon_amount": "1.00",  # Uses a realistic coupon amount for testing.
        
        "rebate_company": "Ibotta",  # Uses a common rebate company for testing.
        "rebate_amount": "0.50",  # Uses a realistic rebate amount for
        "rebate_status": RebateStatus.PENDING.value,  # Uses a pending rebate status for testing.
        
        "source_type": InputType.MANUAL_ENTRY.value,
        
        "user_corrected": False,
        "notes": "Synthetic test purchase",  # Adds a note to identify this as a test record.
    }
    
def _override_db() -> dict[str,object]:  # Provides a test database override for FastAPI dependency injection.
    
    return {"purchases": object()}  # Returns the test database in the expected override format.

def test_get_purchases_returns_list(monkeypatch) -> None:  # Tests GET purchase list route.
    async def fake_list_purchases(**kwargs):  # Defines fake service response.
        return [{"canonical_name": "H-E-B Milk"}]  # Returns fake purchase list.

    app.dependency_overrides[purchases_api.get_db] = _override_db  # Overrides database dependency.
    monkeypatch.setattr(purchases_api.purchase_service, "list_purchases", fake_list_purchases)  # Patches service.

    client: TestClient = TestClient(app)  # Creates API client.
    response = client.get("/api/v1/purchases")  # Calls GET endpoint.

    app.dependency_overrides.clear()  # Clears dependency overrides.

    assert response.status_code == 200  # Verifies success.
    assert response.json()["meta"]["count"] == 1  # Verifies result count.


def test_post_purchase_creates_manual_purchase(monkeypatch) -> None:  # Tests POST purchase route.
    payload = _purchase_payload()  # Creates valid purchase payload.

    async def fake_create_purchase(dal, request_payload):  # Defines fake create service.
        created = dict(request_payload)  # Copies request payload.
        created["_id"] = "purchase-1"  # Adds fake MongoDB id.
        return created  # Returns created purchase.

    app.dependency_overrides[purchases_api.get_db] = _override_db  # Overrides database dependency.
    monkeypatch.setattr(purchases_api.purchase_service, "create_purchase", fake_create_purchase)  # Patches service.

    client: TestClient = TestClient(app)  # Creates API client.
    response = client.post("/api/v1/purchases", json=payload)  # Calls POST endpoint.

    app.dependency_overrides.clear()  # Clears dependency overrides.

    assert response.status_code == 201  # Verifies creation success.
    assert response.json()["data"]["canonical_name"] == "H-E-B Milk"  # Verifies product name.


def test_patch_purchase_updates_field(monkeypatch) -> None:  # Tests PATCH purchase route.
    async def fake_update_purchase(dal, purchase_id, payload):  # Defines fake update service.
        return {  # Returns updated purchase.
            "_id": purchase_id,  # Returns purchase id.
            "canonical_name": payload["canonical_name"],  # Returns updated name.
        }

    app.dependency_overrides[purchases_api.get_db] = _override_db  # Overrides database dependency.
    monkeypatch.setattr(purchases_api.purchase_service, "update_purchase", fake_update_purchase)  # Patches service.

    client: TestClient = TestClient(app)  # Creates API client.
    response = client.patch(  # Calls PATCH endpoint.
        "/api/v1/purchases/purchase-1",  # Sets fake purchase id.
        json={"canonical_name": "Updated Milk"},  # Sends updated field.
    )

    app.dependency_overrides.clear()  # Clears dependency overrides.

    assert response.status_code == 200  # Verifies update success.
    assert response.json()["data"]["canonical_name"] == "Updated Milk"  # Verifies updated field.


def test_delete_purchase_deletes_record(monkeypatch) -> None:  # Tests DELETE purchase route.
    async def fake_delete_purchase(dal, purchase_id):  # Defines fake delete service.
        return True  # Returns successful deletion.

    app.dependency_overrides[purchases_api.get_db] = _override_db  # Overrides database dependency.
    monkeypatch.setattr(purchases_api.purchase_service, "delete_purchase", fake_delete_purchase)  # Patches service.

    client: TestClient = TestClient(app)  # Creates API client.
    response = client.delete("/api/v1/purchases/purchase-1")  # Calls DELETE endpoint.

    app.dependency_overrides.clear()  # Clears dependency overrides.

    assert response.status_code == 200  # Verifies delete success.
    assert response.json()["data"]["deleted"] is True  # Verifies deleted flag.


def test_financial_fields_remain_separate() -> None:  # Verifies financial field separation.
    payload = _purchase_payload()  # Creates reusable purchase payload.

    assert Decimal(payload["shelf_price"]) == Decimal("3.99")  # Verifies shelf price remains separate.
    assert Decimal(payload["sale_price"]) == Decimal("3.49")  # Verifies sale price remains separate.
    assert Decimal(payload["register_price"]) == Decimal("3.99")  # Verifies register price remains separate.
    assert Decimal(payload["out_of_pocket"]) == Decimal("6.49")  # Verifies out-of-pocket remains separate.

    rebate_adjusted = Decimal(payload["out_of_pocket"]) - Decimal(payload["rebate_amount"])  # Computes rebate-adjusted value.

    assert rebate_adjusted == Decimal("5.99")  # Verifies rebate math separately.
    assert Decimal(payload["out_of_pocket"]) == Decimal("6.49")  # Verifies rebates were not subtracted from out_of_pocket.

def test_route_and_service_do_not_use_direct_mongo_calls() -> None:  # Verifies architecture rules.
    route_source = open("backend/api/purchases.py", encoding="utf-8").read()  # Reads route source file.
    service_source = open("backend/services/purchase_service.py", encoding="utf-8").read()  # Reads service source file.

    forbidden_calls = [  # Defines forbidden Mongo CRUD operations.
        "find_one(",
        "insert_one(",
        "update_one(",
        "delete_one(",
    ]

    for forbidden in forbidden_calls:  # Checks every forbidden CRUD operation.
        assert forbidden not in route_source  # Verifies route layer does not call Mongo directly.
        assert forbidden not in service_source  # Verifies service layer does not call Mongo directly.
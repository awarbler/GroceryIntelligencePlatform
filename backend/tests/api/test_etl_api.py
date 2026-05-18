# =============================================================================
# File: test_etl_api.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests P1-11 ETL and correction API routes.
# Security Note: Tests use synthetic receipt data and monkeypatched pipeline calls.
# SRS Traceability: Supports SRS v5.0 Section 12, Section 13, and SE-009.
# SDD Traceability: Supports SDD v5.0 API Endpoint Design.
# =============================================================================

from __future__ import annotations  # Enables modern type hint behavior.

from datetime import UTC  # Imports UTC for timezone-aware timestamps.
from datetime import datetime  # Imports datetime for response objects.
from datetime import timedelta  # Imports timedelta for expiration objects.
from decimal import Decimal  # Imports Decimal for item values.

from fastapi.testclient import TestClient  # Imports FastAPI test client.

import backend.api.etl as etl_api  # Imports API module for monkeypatching route dependencies.
from backend.main import app  # Imports FastAPI app.
from backend.models.correction import ApproveSessionResponse  # Imports approval response.
from backend.models.correction import CorrectionItem  # Imports correction item model.
from backend.models.correction import CorrectionSession  # Imports correction session model.


def _session() -> CorrectionSession:  # Builds a fake correction session.
    now: datetime = datetime.now(UTC)  # Creates current timestamp.
    item: CorrectionItem = CorrectionItem(  # Creates one correction item.
        item_id="item-1",  # Sets item ID.
        raw_name="HEB MILK",  # Sets raw name.
        parsed_name="HEB MILK",  # Sets parsed name.
        normalized_name="H-E-B Milk",  # Sets normalized name.
        quantity=Decimal("1"),  # Sets quantity.
        quantity_unit="each",  # Sets quantity unit.
        unit_price=Decimal("3.99"),  # Sets unit price.
        line_total=Decimal("3.99"),  # Sets line total.
        parser_version="heb-online-v1.0",  # Sets parser version.
        confidence=1.0,  # Sets confidence.
        auto_accepted=True,  # Sets auto accepted.
    )  # Ends item creation.
    return CorrectionSession(  # Returns fake session.
        session_id="session-1",  # Sets session ID.
        source_type="heb_online_pdf",  # Sets source type.
        store="HEB",  # Sets store.
        raw_lines=["Order # 12345"],  # Sets raw lines.
        items=[item],  # Sets items.
        parse_errors=[],  # Sets parse errors.
        source_metadata={"filename": "receipt.txt"},  # Sets metadata.
        created_at=now,  # Sets creation timestamp.
        expires_at=now + timedelta(hours=24),  # Sets expiration timestamp.
    )  # Ends session creation.


def _override_db() -> dict[str, object]:  # Builds fake database dependency.
    return {  # Returns a subscriptable fake database because DAL classes use database["collection"].
        "products": object(),  # Provides fake products collection.
        "purchases": object(),  # Provides fake purchases collection.
        "raw_inputs": object(),  # Provides fake raw_inputs collection.
    }  
def test_paste_route_returns_session_id(monkeypatch) -> None:  # Tests paste route session creation.
    async def fake_create_session_from_pasted_text(text, product_access):  # Defines fake paste pipeline.
        return _session()  # Returns fake session.

    app.dependency_overrides[etl_api.get_db] = _override_db  # Overrides database dependency.
    monkeypatch.setattr(etl_api, "create_session_from_pasted_text", fake_create_session_from_pasted_text)  # Patches pipeline.
    client: TestClient = TestClient(app)  # Creates test client.
    response = client.post("/api/v1/etl/paste", json={"text": "Order # 12345"})  # Calls paste endpoint.
    app.dependency_overrides.clear()  # Clears dependency overrides.
    assert response.status_code == 200  # Verifies success.
    assert response.json()["session_id"] == "session-1"  # Verifies session ID.


def test_get_correction_session_route_returns_raw_lines(monkeypatch) -> None:  # Tests session retrieval route.
    monkeypatch.setattr(etl_api, "get_correction_session", lambda session_id: _session())  # Patches retrieval.
    client: TestClient = TestClient(app)  # Creates test client.
    response = client.get("/api/v1/correction/session-1")  # Calls retrieval endpoint.
    assert response.status_code == 200  # Verifies success.
    assert response.json()["session"]["raw_lines"] == ["Order # 12345"]  # Verifies raw lines.


def test_patch_item_route_updates_session(monkeypatch) -> None:  # Tests item update route.
    monkeypatch.setattr(etl_api, "update_correction_item", lambda session_id, item_id, request: _session())  # Patches update.
    client: TestClient = TestClient(app)  # Creates test client.
    response = client.patch("/api/v1/correction/session-1/item/item-1", json={"normalized_name": "Corrected Milk"})  # Calls patch endpoint.
    assert response.status_code == 200  # Verifies success.
    assert response.json()["session"]["items"][0]["item_id"] == "item-1"  # Verifies item exists.


def test_normalize_route_returns_saved_alias(monkeypatch) -> None:  # Tests normalize route.
    async def fake_save_item_normalization(session_id, item_id, request, product_access):  # Defines fake normalize pipeline.
        return _session()  # Returns fake session.

    app.dependency_overrides[etl_api.get_db] = _override_db  # Overrides database dependency.
    monkeypatch.setattr(etl_api, "save_item_normalization", fake_save_item_normalization)  # Patches normalize pipeline.
    client: TestClient = TestClient(app)  # Creates test client.
    response = client.post(  # Calls normalize endpoint.
        "/api/v1/correction/session-1/item/item-1/normalize",  # Sets route.
        json={"canonical_name": "H-E-B Milk", "alias": "HEB MILK"},  # Sets body.
    )  # Ends request.
    app.dependency_overrides.clear()  # Clears dependency overrides.
    assert response.status_code == 200  # Verifies success.
    assert response.json()["canonical_name"] == "H-E-B Milk"  # Verifies canonical name.
    assert response.json()["alias"] == "HEB MILK"  # Verifies alias.


def test_approve_route_returns_created_ids(monkeypatch) -> None:  # Tests approval route.
    async def fake_approve_correction_session(session_id, purchases_access, raw_inputs_access, products_access):  # Defines fake approval pipeline.
        return ApproveSessionResponse(  # Returns fake approval result.
            raw_input_id="raw-input-1",  # Sets raw input ID.
            purchase_ids=["purchase-1"],  # Sets purchase IDs.
            purchase_count=1,  # Sets purchase count.
            price_history_updates=1,  # Sets price history updates.
            loader_version="etl-loader-v1.0",  # Sets loader version.
        )  # Ends fake result.

    app.dependency_overrides[etl_api.get_db] = _override_db  # Overrides database dependency.
    monkeypatch.setattr(etl_api, "approve_correction_session", fake_approve_correction_session)  # Patches approval pipeline.
    client: TestClient = TestClient(app)  # Creates test client.
    response = client.post("/api/v1/correction/session-1/approve")  # Calls approval endpoint.
    app.dependency_overrides.clear()  # Clears dependency overrides.
    assert response.status_code == 200  # Verifies success.
    assert response.json()["raw_input_id"] == "raw-input-1"  # Verifies raw input ID.
    assert response.json()["purchase_ids"] == ["purchase-1"]  # Verifies purchase IDs.
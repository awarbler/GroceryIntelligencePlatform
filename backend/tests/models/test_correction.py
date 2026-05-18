# =============================================================================
# File: test_etl_pipeline.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests P1-11 ETL pipeline orchestration without direct MongoDB access.
# Security Note: Tests use synthetic H-E-B receipt data only.
# SRS Traceability: Supports SRS v5.0 ET-001 through ET-005 and HC-001 through HC-009.
# SDD Traceability: Supports SDD v5.0 ETL Pipeline Design.
# =============================================================================

from __future__ import annotations  # Enables modern type hint behavior.

from datetime import date  # Imports date for price history fake checks.
from decimal import Decimal  # Imports Decimal for exact money checks.
from typing import Any  # Imports Any for fake documents.

import pytest  # Imports pytest for async tests and assertions.

from backend.etl.pipeline import approve_correction_session  # Imports approval orchestration.
from backend.etl.pipeline import clear_sessions_for_test  # Imports test cleanup helper.
from backend.etl.pipeline import create_session_from_pasted_text  # Imports paste orchestration.
from backend.etl.pipeline import expire_session_for_test  # Imports expiration helper.
from backend.etl.pipeline import get_correction_session  # Imports session retrieval.
from backend.etl.pipeline import save_item_normalization  # Imports alias save orchestration.
from backend.etl.pipeline import update_correction_item  # Imports item update orchestration.
from backend.models.correction import CorrectionItemUpdateRequest  # Imports item update request.
from backend.models.correction import NormalizeCorrectionRequest  # Imports normalize request.
from backend.services.correction_service import CorrectionSessionNotFoundError  # Imports missing session error.


class FakeProductsAccess:  # Defines a fake products DAL.
    def __init__(self) -> None:  # Initializes fake products access.
        self.aliases_added: list[tuple[str, str]] = []  # Tracks saved aliases.
        self.price_updates: list[dict[str, Any]] = []  # Tracks price history updates.

    async def find_all_products(self) -> list[dict[str, Any]]:  # Fakes product catalog lookup.
        return [  # Returns fake products.
            {  # Starts product document.
                "_id": "product-1",  # Sets fake product ID.
                "canonical_name": "H-E-B Milk",  # Sets canonical name.
                "aliases": ["HEB MILK"],  # Sets alias list.
            }  # Ends product document.
        ]  # Ends product list.

    async def add_product_alias(self, canonical_name: str, alias: str) -> bool:  # Fakes alias save.
        self.aliases_added.append((canonical_name, alias))  # Tracks alias save.
        return True  # Pretends an existing product was updated.

    async def update_price_history(  # Fakes price history update.
        self,  # Receives fake instance.
        canonical_name: str,  # Receives canonical name.
        store_ref: str,  # Receives store reference.
        regular_price: Decimal,  # Receives regular price.
        sale_price: Decimal | None,  # Receives sale price.
        observed_date: date,  # Receives observed date.
        source: str,  # Receives source label.
    ) -> None:  # Returns no value.
        self.price_updates.append(  # Tracks price update.
            {  # Starts update record.
                "canonical_name": canonical_name,  # Stores canonical name.
                "store_ref": store_ref,  # Stores store reference.
                "regular_price": regular_price,  # Stores regular price.
                "sale_price": sale_price,  # Stores sale price.
                "observed_date": observed_date,  # Stores observed date.
                "source": source,  # Stores source.
            }  # Ends update record.
        )  # Ends append.


class FakePurchasesAccess:  # Defines a fake purchases DAL.
    def __init__(self) -> None:  # Initializes fake purchases access.
        self.documents: list[dict[str, Any]] = []  # Tracks inserted purchase documents.

    async def insert_many_purchases(self, documents: list[dict[str, Any]]) -> list[str]:  # Fakes purchase insert.
        self.documents = documents  # Stores inserted documents.
        return [f"purchase-{index}" for index, _ in enumerate(documents, start=1)]  # Returns fake purchase IDs.


class FakeRawInputsAccess:  # Defines a fake raw inputs DAL.
    def __init__(self) -> None:  # Initializes fake raw inputs access.
        self.document: dict[str, Any] | None = None  # Tracks raw input document.
        self.linked_ids: list[str] = []  # Tracks linked record IDs.

    async def insert_raw_input(self, document: dict[str, Any]) -> str:  # Fakes raw input insert.
        self.document = document  # Stores raw input document.
        return "raw-input-1"  # Returns fake raw input ID.

    async def append_linked_record_ids(self, raw_input_id: str, record_ids: list[str]) -> None:  # Fakes raw input linking.
        self.linked_ids = record_ids  # Stores linked IDs.


def _receipt_text() -> str:  # Builds synthetic real-format H-E-B receipt text.
    return "\n".join(  # Joins lines with newlines.
        [  # Starts line list.
            "Order # 12345",  # Adds order number.
            "Order placed on 5/18/2026",  # Adds order date.
            "Item, HEB MILK. Quantity: 1 each. Price: $3.99.",  # Adds item line.
            "Subtotal $3.99",  # Adds subtotal.
            "Tax $0.00",  # Adds tax.
            "Total $3.99",  # Adds total.
        ]  # Ends line list.
    )  # Returns receipt text.


@pytest.mark.asyncio  # Marks test as async.
async def test_paste_creates_session_id() -> None:  # Tests paste orchestration.
    clear_sessions_for_test()  # Clears shared sessions.
    product_access: FakeProductsAccess = FakeProductsAccess()  # Creates fake products access.
    session = await create_session_from_pasted_text(_receipt_text(), product_access)  # Creates session.
    assert session.session_id  # Verifies session ID exists.
    assert session.raw_lines[0] == "Order # 12345"  # Verifies raw lines are stored.
    assert len(session.items) == 1  # Verifies parsed item exists.


@pytest.mark.asyncio  # Marks test as async.
async def test_session_can_be_retrieved() -> None:  # Tests session retrieval.
    clear_sessions_for_test()  # Clears shared sessions.
    product_access: FakeProductsAccess = FakeProductsAccess()  # Creates fake products access.
    session = await create_session_from_pasted_text(_receipt_text(), product_access)  # Creates session.
    retrieved = get_correction_session(session.session_id)  # Retrieves session.
    assert retrieved.session_id == session.session_id  # Verifies same session.


@pytest.mark.asyncio  # Marks test as async.
async def test_item_update_changes_session_data() -> None:  # Tests item update.
    clear_sessions_for_test()  # Clears shared sessions.
    product_access: FakeProductsAccess = FakeProductsAccess()  # Creates fake products access.
    session = await create_session_from_pasted_text(_receipt_text(), product_access)  # Creates session.
    updated = update_correction_item(session.session_id, "item-1", CorrectionItemUpdateRequest(normalized_name="Corrected Milk"))  # Updates item.
    assert updated.items[0].normalized_name == "Corrected Milk"  # Verifies changed name.
    assert updated.items[0].user_corrected is True  # Verifies correction flag.


@pytest.mark.asyncio  # Marks test as async.
async def test_normalize_saves_alias_into_products_aliases() -> None:  # Tests alias save flow.
    clear_sessions_for_test()  # Clears shared sessions.
    product_access: FakeProductsAccess = FakeProductsAccess()  # Creates fake products access.
    session = await create_session_from_pasted_text(_receipt_text(), product_access)  # Creates session.
    request = NormalizeCorrectionRequest(canonical_name="H-E-B Milk", alias="HEB MILK 1 GAL")  # Creates normalize request.
    updated = await save_item_normalization(session.session_id, "item-1", request, product_access)  # Saves alias.
    assert product_access.aliases_added == [("H-E-B Milk", "HEB MILK 1 GAL")]  # Verifies alias save.
    assert updated.items[0].matched_rule_type == "owner_alias_correction"  # Verifies item updated.


@pytest.mark.asyncio  # Marks test as async.
async def test_approve_triggers_stage_3_loader() -> None:  # Tests approval and loader trigger.
    clear_sessions_for_test()  # Clears shared sessions.
    product_access: FakeProductsAccess = FakeProductsAccess()  # Creates fake products access.
    purchases_access: FakePurchasesAccess = FakePurchasesAccess()  # Creates fake purchases access.
    raw_inputs_access: FakeRawInputsAccess = FakeRawInputsAccess()  # Creates fake raw inputs access.
    session = await create_session_from_pasted_text(_receipt_text(), product_access)  # Creates session.
    result = await approve_correction_session(session.session_id, purchases_access, raw_inputs_access, product_access)  # Approves session.
    assert result.raw_input_id == "raw-input-1"  # Verifies raw input created.
    assert result.purchase_ids == ["purchase-1"]  # Verifies purchase created.
    assert result.price_history_updates == 1  # Verifies price history updated.
    assert raw_inputs_access.linked_ids == ["purchase-1"]  # Verifies raw input linked.


@pytest.mark.asyncio  # Marks test as async.
async def test_expired_session_is_treated_as_not_found() -> None:  # Tests expired session behavior.
    clear_sessions_for_test()  # Clears shared sessions.
    product_access: FakeProductsAccess = FakeProductsAccess()  # Creates fake products access.
    session = await create_session_from_pasted_text(_receipt_text(), product_access)  # Creates session.
    expire_session_for_test(session.session_id)  # Forces expiration.
    with pytest.raises(CorrectionSessionNotFoundError):  # Expects not-found error.
        get_correction_session(session.session_id)  # Attempts retrieval.
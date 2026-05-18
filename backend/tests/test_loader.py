# =============================================================================
# File: test_loader.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Unit tests for the Stage 3 ETL loader.
# SRS Traceability: Supports SRS v5.0 Section 12 ET-004, Section 3.5 RD-001 through RD-004, Section 23 PR-001 through PR-003.
# SDD Traceability: Supports SDD v5.0 Stage 3 Load and testing architecture.
# =============================================================================
from __future__ import annotations  # Enables modern type hints.

from datetime import date, datetime, timezone  # Imports date and datetime for loader input types.
from decimal import Decimal  # Imports Decimal for money values matching the parser.
from pathlib import Path  # Imports Path for architecture boundary test.
from typing import Any  # Imports Any for fake document typing.

import pytest  # Imports pytest for async test support.

from backend.etl.loader import (  # Imports loader components under test.
    LOADER_VERSION,  # Imports version constant for traceability assertion.
    ApprovedItem,  # Imports approved item dataclass.
    LoadResult,  # Imports load result dataclass.
    RawInputArchive,  # Imports raw input archive dataclass.
    load_approved_session,  # Imports the Stage 3 entry point.
)


# ---------------------------------------------------------------------------
# Fake data access objects
# ---------------------------------------------------------------------------


class FakePurchasesAccess:  # Defines in-memory fake for purchases data access.
    def __init__(self) -> None:  # Initializes fake purchase storage.
        self.inserted: list[dict[str, Any]] = []  # Records inserted purchase documents.

    async def insert_many_purchases(self, documents: list[dict[str, Any]]) -> list[str]:  # Fakes bulk insert.
        self.inserted.extend(documents)  # Records documents.
        return [f"purchase-{i}" for i in range(len(documents))]  # Returns deterministic fake IDs.


class FakeRawInputsAccess:  # Defines in-memory fake for raw inputs data access.
    def __init__(self) -> None:  # Initializes fake raw input storage.
        self.inserted: list[dict[str, Any]] = []  # Records inserted archive documents.
        self.linked: dict[str, list[str]] = {}  # Records linked record ID updates.

    async def insert_raw_input(self, document: dict[str, Any]) -> str:  # Fakes archive insert.
        self.inserted.append(document)  # Records archive document.
        return "raw-input-1"  # Returns deterministic fake ID.

    async def append_linked_record_ids(self, raw_input_id: str, record_ids: list[str]) -> None:  # Fakes link update.
        self.linked[raw_input_id] = record_ids  # Records the linked purchase IDs.


class FakeProductsAccess:  # Defines in-memory fake for products data access.
    def __init__(self) -> None:  # Initializes fake price history storage.
        self.price_history_calls: list[dict[str, Any]] = []  # Records price history update calls.

    async def update_price_history(  # Fakes price history update.
        self,  # Fake instance.
        canonical_name: str,  # Canonical product name.
        store_ref: str,  # Store identifier.
        regular_price: Decimal,  # Regular price as Decimal.
        sale_price: Decimal | None,  # Sale price or None.
        observed_date: date,  # Observation date as date object.
        source: str,  # Source label.
    ) -> None:  # No return value.
        self.price_history_calls.append({  # Records all call arguments.
            "canonical_name": canonical_name,  # Stores canonical name.
            "store_ref": store_ref,  # Stores store ref.
            "regular_price": regular_price,  # Stores regular price.
            "sale_price": sale_price,  # Stores sale price.
            "observed_date": observed_date,  # Stores observed date.
            "source": source,  # Stores source.
        })  # Ends append.


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def make_archive() -> RawInputArchive:  # Builds reusable test archive metadata.
    return RawInputArchive(  # Creates RawInputArchive with correct types.
        source_type="heb_online_pdf",  # Uses Phase 1 HEB source type.
        store_ref="heb",  # Uses plain string store ref matching Phase 1.
        filename="receipt.pdf",  # Uses test filename.
        file_path="uploads/receipts/receipt.pdf",  # Uses test archive path.
        raw_lines=["Item, H-E-B Milk. Quantity: 1 each. Price: $3.48."],  # Uses safe synthetic line.
        ocr_confidence=None,  # Uses None because text PDFs do not use OCR.
        page_count=1,  # Uses 1 matching RawInputModel ge=1 constraint.
        timestamp=datetime(2026, 5, 18, 10, 0, 0, tzinfo=timezone.utc),  # Uses datetime object not string.
        parser_version="heb-online-v1.0",  # Uses P1-08 parser version.
    )  # Ends archive.


def make_item(name: str = "H-E-B Whole Milk 1 Gal") -> ApprovedItem:  # Builds reusable test approved item.
    return ApprovedItem(  # Creates ApprovedItem with correct types.
        canonical_name=name,  # Uses provided canonical name.
        raw_name="H-E-B Whole Milk, 1 gal",  # Uses raw parsed name.
        store_id="heb",  # Uses plain string store id matching Phase 1.
        quantity=Decimal("1"),  # Uses Decimal matching parser output.
        quantity_unit="each",  # Uses each unit.
        unit_price=Decimal("3.48"),  # Uses Decimal matching parser output.
        line_total=Decimal("3.48"),  # Uses Decimal matching parser output.
        purchase_date=date(2026, 5, 18),  # Uses date object not string matching PurchaseModel.purchase_date.
        parser_version="heb-online-v1.0",  # Uses P1-08 parser version.
        product_ref="product-abc123",  # Uses test product reference.
    )  # Ends approved item.


# ---------------------------------------------------------------------------
# Tests: raw_inputs archive
# ---------------------------------------------------------------------------


@pytest.mark.asyncio  # Marks as async test.
async def test_raw_inputs_archive_is_created() -> None:  # Tests archive creation.
    raw_inputs = FakeRawInputsAccess()  # Creates fake raw inputs access.

    result = await load_approved_session(  # Runs loader.
        approved_items=[make_item()],  # Passes one approved item.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=raw_inputs,  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert len(raw_inputs.inserted) == 1  # Verifies one archive document inserted.
    assert result.raw_input_id == "raw-input-1"  # Verifies archive ID in result.


@pytest.mark.asyncio  # Marks as async test.
async def test_raw_inputs_archive_uses_datetime_for_timestamp() -> None:  # Tests timestamp type is datetime.
    raw_inputs = FakeRawInputsAccess()  # Creates fake raw inputs access.

    await load_approved_session(  # Runs loader.
        approved_items=[],  # Passes no items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=raw_inputs,  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert isinstance(raw_inputs.inserted[0]["timestamp"], datetime)  # Verifies timestamp is datetime not string.


@pytest.mark.asyncio  # Marks as async test.
async def test_raw_inputs_archive_stores_parser_version() -> None:  # Tests RD-004 parser version on archive.
    raw_inputs = FakeRawInputsAccess()  # Creates fake raw inputs access.

    await load_approved_session(  # Runs loader.
        approved_items=[],  # Passes no items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=raw_inputs,  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert raw_inputs.inserted[0]["parser_version"] == "heb-online-v1.0"  # Verifies parser version per RD-004.


@pytest.mark.asyncio  # Marks as async test.
async def test_archive_created_even_when_no_approved_items() -> None:  # Tests raw input always preserved.
    raw_inputs = FakeRawInputsAccess()  # Creates fake raw inputs access.
    purchases = FakePurchasesAccess()  # Creates fake purchases access.

    result = await load_approved_session(  # Runs loader with empty items.
        approved_items=[],  # Passes no approved items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=purchases,  # Passes fake purchases.
        raw_inputs_access=raw_inputs,  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert result.purchase_count == 0  # Verifies no purchases saved.
    assert len(purchases.inserted) == 0  # Verifies no purchase insert occurred.
    assert len(raw_inputs.inserted) == 1  # Verifies archive was still created.


# ---------------------------------------------------------------------------
# Tests: purchase records
# ---------------------------------------------------------------------------


@pytest.mark.asyncio  # Marks as async test.
async def test_every_purchase_has_raw_input_ref() -> None:  # Tests RD-001 raw_input_ref on purchases.
    purchases = FakePurchasesAccess()  # Creates fake purchases access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item(), make_item("H-E-B Sour Cream 16 oz")],  # Passes two items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=purchases,  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    for purchase in purchases.inserted:  # Checks every inserted purchase.
        assert purchase["raw_input_ref"] == "raw-input-1"  # Verifies raw_input_ref on every purchase.


@pytest.mark.asyncio  # Marks as async test.
async def test_every_purchase_stores_parser_version() -> None:  # Tests RD-004 on purchases.
    purchases = FakePurchasesAccess()  # Creates fake purchases access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item()],  # Passes one item.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=purchases,  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert purchases.inserted[0]["parser_version"] == "heb-online-v1.0"  # Verifies parser version per RD-004.


@pytest.mark.asyncio  # Marks as async test.
async def test_purchase_uses_decimal_for_money_fields() -> None:  # Tests Decimal types on purchase docs.
    purchases = FakePurchasesAccess()  # Creates fake purchases access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item()],  # Passes one item.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=purchases,  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert isinstance(purchases.inserted[0]["unit_price"], Decimal)  # Verifies unit_price is Decimal.
    assert isinstance(purchases.inserted[0]["line_total"], Decimal)  # Verifies line_total is Decimal.


@pytest.mark.asyncio  # Marks as async test.
async def test_purchase_uses_date_for_purchase_date() -> None:  # Tests date type on purchase docs.
    purchases = FakePurchasesAccess()  # Creates fake purchases access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item()],  # Passes one item.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=purchases,  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert isinstance(purchases.inserted[0]["purchase_date"], date)  # Verifies purchase_date is date not string.


@pytest.mark.asyncio  # Marks as async test.
async def test_purchase_count_matches_approved_items() -> None:  # Tests correct number of purchases saved.
    result = await load_approved_session(  # Runs loader.
        approved_items=[make_item(), make_item("H-E-B Sour Cream 16 oz"), make_item("Mission Tortillas")],  # Passes three items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert result.purchase_count == 3  # Verifies three purchases saved.


# ---------------------------------------------------------------------------
# Tests: linked_record_ids
# ---------------------------------------------------------------------------


@pytest.mark.asyncio  # Marks as async test.
async def test_raw_inputs_linked_record_ids_updated() -> None:  # Tests purchase IDs linked to archive.
    raw_inputs = FakeRawInputsAccess()  # Creates fake raw inputs access.

    result = await load_approved_session(  # Runs loader.
        approved_items=[make_item(), make_item("H-E-B Sour Cream 16 oz")],  # Passes two items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=raw_inputs,  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    linked = raw_inputs.linked.get(result.raw_input_id, [])  # Gets linked IDs for this archive.
    assert len(linked) == 2  # Verifies both purchase IDs linked.


# ---------------------------------------------------------------------------
# Tests: price history
# ---------------------------------------------------------------------------


@pytest.mark.asyncio  # Marks as async test.
async def test_price_history_updated_for_each_item() -> None:  # Tests one update per item.
    products = FakeProductsAccess()  # Creates fake products access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item(), make_item("H-E-B Sour Cream 16 oz")],  # Passes two items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=products,  # Passes fake products.
    )  # Ends loader call.

    assert len(products.price_history_calls) == 2  # Verifies two price history updates.


@pytest.mark.asyncio  # Marks as async test.
async def test_price_history_receives_date_not_string() -> None:  # Tests date type passed to price history.
    products = FakeProductsAccess()  # Creates fake products access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item()],  # Passes one item.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=products,  # Passes fake products.
    )  # Ends loader call.

    assert isinstance(products.price_history_calls[0]["observed_date"], date)  # Verifies date object not string.


@pytest.mark.asyncio  # Marks as async test.
async def test_price_history_receives_decimal_for_price() -> None:  # Tests Decimal type passed to price history.
    products = FakeProductsAccess()  # Creates fake products access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item()],  # Passes one item.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=products,  # Passes fake products.
    )  # Ends loader call.

    assert isinstance(products.price_history_calls[0]["regular_price"], Decimal)  # Verifies Decimal not float.


@pytest.mark.asyncio  # Marks as async test.
async def test_price_history_skipped_when_canonical_name_empty() -> None:  # Tests graceful skip.
    products = FakeProductsAccess()  # Creates fake products access.

    await load_approved_session(  # Runs loader.
        approved_items=[make_item("")],  # Passes item with empty canonical name.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=products,  # Passes fake products.
    )  # Ends loader call.

    assert len(products.price_history_calls) == 0  # Verifies no price history call for unnamed item.


# ---------------------------------------------------------------------------
# Tests: traceability
# ---------------------------------------------------------------------------


@pytest.mark.asyncio  # Marks as async test.
async def test_load_result_has_loader_version() -> None:  # Tests RD-004 loader version on result.
    result = await load_approved_session(  # Runs loader.
        approved_items=[],  # Passes no items.
        raw_input_archive=make_archive(),  # Passes test archive.
        purchases_access=FakePurchasesAccess(),  # Passes fake purchases.
        raw_inputs_access=FakeRawInputsAccess(),  # Passes fake raw inputs.
        products_access=FakeProductsAccess(),  # Passes fake products.
    )  # Ends loader call.

    assert result.loader_version == LOADER_VERSION  # Verifies loader version on result.
    assert result.loader_version.startswith("etl-loader-")  # Verifies version string format.


# ---------------------------------------------------------------------------
# Tests: architecture boundary
# ---------------------------------------------------------------------------


def test_loader_has_no_forbidden_imports() -> None:  # Tests loader does not cross architecture boundaries.
    source_text: str = Path("backend/etl/loader.py").read_text(encoding="utf-8")  # Reads loader source text.
    forbidden: list[str] = [  # Defines forbidden import tokens.
        "motor",  # Blocks Motor driver direct import.
        "pymongo",  # Blocks PyMongo direct import.
        "from backend.api",  # Blocks FastAPI route imports.
        "from fastapi",  # Blocks FastAPI imports.
        "import fastapi",  # Blocks FastAPI package import.
        "normalize_product_name",  # Blocks normalization calls in Stage 3.
        "parse_heb",  # Blocks parser calls in Stage 3.
    ]  # Ends forbidden list.

    for token in forbidden:  # Checks each forbidden token.
        assert token not in source_text, f"Forbidden token '{token}' found in loader.py"  # Fails on violation.
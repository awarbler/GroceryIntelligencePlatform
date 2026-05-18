# =============================================================================
# File: loader.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Implements Stage 3 ETL loading for approved correction session data.
# Security Note: The loader writes approved grocery data only and must not store credentials, tokens, or secrets.
# SRS Traceability: Supports SRS v5.0 Section 12 ET-004, Section 3.5 RD-001 through RD-004, and Section 23 PR-001 through PR-003.
# SDD Traceability: Supports SDD v5.0 Stage 3 Load, purchases, raw_inputs, and price history design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints without runtime forward-reference issues.

import logging  # Imports logging for Stage 3 traceability.
from dataclasses import dataclass, field  # Imports dataclass tools for structured loader inputs and outputs.
from datetime import date, datetime  # Imports date for purchases and datetime for raw input archives.
from decimal import Decimal  # Imports Decimal for exact money values.
from typing import Any, Protocol  # Imports Any for document dictionaries and Protocol for dependency typing.

logger = logging.getLogger(__name__)  # Creates a module-level logger for this ETL stage.

LOADER_VERSION: str = "etl-loader-v1.0"  # Stores the loader version for traceability.


class PurchasesAccessProtocol(Protocol):  # Defines the purchases data access methods required by the loader.
    async def insert_many_purchases(self, documents: list[dict[str, Any]]) -> list[str]:  # Requires bulk purchase insertion.
        ...  # Marks this method as a protocol stub.


class RawInputsAccessProtocol(Protocol):  # Defines the raw input data access methods required by the loader.
    async def insert_raw_input(self, document: dict[str, Any]) -> str:  # Requires raw input archive insertion.
        ...  # Marks this method as a protocol stub.

    async def append_linked_record_ids(self, raw_input_id: str, record_ids: list[str]) -> None:  # Requires purchase ID linking.
        ...  # Marks this method as a protocol stub.


class ProductsAccessProtocol(Protocol):  # Defines the product data access methods required by the loader.
    async def update_price_history(  # Requires product price history updates.
        self,  # Uses the data access instance.
        canonical_name: str,  # Receives the canonical product name.
        store_ref: str,  # Receives the Phase 1 store identifier string.
        regular_price: Decimal,  # Receives the observed regular price.
        sale_price: Decimal | None,  # Receives the observed sale price when known.
        observed_date: date,  # Receives the date the price was observed.
        source: str,  # Receives the source label.
    ) -> None:  # Returns no value.
        ...  # Marks this method as a protocol stub.


@dataclass
class RawInputArchive:  # Represents the raw source metadata that must be archived.
    source_type: str  # Stores the source type, such as "heb_online_pdf".
    store_ref: str  # Stores the Phase 1 store identifier string.
    filename: str  # Stores the original uploaded filename.
    file_path: str  # Stores the archived file path.
    raw_lines: list[str]  # Stores raw extracted text lines.
    ocr_confidence: float | None  # Stores OCR confidence or None for text-based PDFs.
    page_count: int  # Stores the page count and must be at least one.
    timestamp: datetime  # Stores the extraction/archive timestamp as a datetime object.
    parser_version: str  # Stores the parser version for traceability.


@dataclass
class ApprovedItem:  # Represents one approved item from the correction workflow.
    canonical_name: str  # Stores the normalized product name.
    raw_name: str  # Stores the original parsed item name.
    store_id: str  # Stores the Phase 1 store identifier string.
    quantity: Decimal  # Stores the item quantity using Decimal.
    quantity_unit: str  # Stores the item quantity unit.
    unit_price: Decimal  # Stores the unit price using Decimal.
    line_total: Decimal  # Stores the line total using Decimal.
    purchase_date: date  # Stores the purchase date as a date object.
    parser_version: str  # Stores the parser version for traceability.
    product_ref: str | None = None  # Stores the matched product ID when known.
    confidence: float = 1.0  # Stores the parser or normalization confidence score.
    extra_fields: dict[str, Any] = field(default_factory=dict)  # Stores approved future fields.


@dataclass
class LoadResult:  # Represents the result returned after Stage 3 completes.
    raw_input_id: str  # Stores the created raw_inputs archive ID.
    purchase_ids: list[str] = field(default_factory=list)  # Stores created purchase IDs.
    price_history_updates: int = 0  # Stores the number of price history updates completed.
    loader_version: str = LOADER_VERSION  # Stores the loader version.

    @property
    def purchase_count(self) -> int:  # Computes the number of saved purchases.
        return len(self.purchase_ids)  # Returns the number of inserted purchase IDs.


async def load_approved_session(  # Runs Stage 3 loading for approved correction-session data.
    approved_items: list[ApprovedItem],  # Receives approved normalized items.
    raw_input_archive: RawInputArchive,  # Receives raw input archive metadata.
    purchases_access: PurchasesAccessProtocol,  # Receives the purchases Data Access Layer dependency.
    raw_inputs_access: RawInputsAccessProtocol,  # Receives the raw_inputs Data Access Layer dependency.
    products_access: ProductsAccessProtocol,  # Receives the products Data Access Layer dependency.
) -> LoadResult:  # Returns a structured load result.
    raw_input_doc: dict[str, Any] = _build_raw_input_document(raw_input_archive)  # Builds the raw_inputs archive document.
    raw_input_id: str = await raw_inputs_access.insert_raw_input(raw_input_doc)  # Saves raw input first.
    logger.info("loader: raw_inputs archive created id=%s", raw_input_id)  # Logs raw archive creation.

    result: LoadResult = LoadResult(raw_input_id=raw_input_id)  # Starts the loader result.

    if not approved_items:  # Checks whether there are approved purchases to save.
        logger.info("loader: no approved items to save")  # Logs the empty approved item case.
        return result  # Returns after preserving the raw input archive.

    purchase_docs: list[dict[str, Any]] = [  # Builds all purchase documents.
        _build_purchase_document(item, raw_input_id)  # Builds one purchase document.
        for item in approved_items  # Iterates over approved items.
    ]  # Ends the purchase document list.

    purchase_ids: list[str] = await purchases_access.insert_many_purchases(purchase_docs)  # Inserts approved purchases second.
    result.purchase_ids = purchase_ids  # Stores created purchase IDs.
    logger.info("loader: inserted %d purchase records", len(purchase_ids))  # Logs purchase insert count.

    await raw_inputs_access.append_linked_record_ids(raw_input_id, purchase_ids)  # Links purchase IDs back to raw input third.
    logger.info("loader: linked %d records to raw_input %s", len(purchase_ids), raw_input_id)  # Logs raw input linking.

    for item in approved_items:  # Iterates over approved items for price history.
        if item.canonical_name:  # Skips price history when no canonical product name exists.
            await products_access.update_price_history(  # Updates product price history fourth.
                canonical_name=item.canonical_name,  # Passes canonical product name.
                store_ref=item.store_id,  # Passes Phase 1 store identifier string.
                regular_price=item.unit_price,  # Passes observed unit price as Decimal.
                sale_price=None,  # Uses None because Phase 1 receipt lines do not prove separate sale price.
                observed_date=item.purchase_date,  # Passes purchase date as a date object.
                source="heb_online_receipt",  # Labels the price source.
            )  # Ends price history call.
            result.price_history_updates += 1  # Counts one price history update.

    logger.info("loader: completed %d price history updates", result.price_history_updates)  # Logs price history count.
    return result  # Returns completed load result.


def _build_raw_input_document(archive: RawInputArchive) -> dict[str, Any]:  # Builds one raw_inputs archive document.
    return {  # Starts the raw_inputs document.
        "source_type": archive.source_type,  # Stores the source type.
        "store_ref": archive.store_ref,  # Stores the store reference.
        "filename": archive.filename,  # Stores the uploaded filename.
        "file_path": archive.file_path,  # Stores the archived file path.
        "raw_lines": archive.raw_lines,  # Stores raw extracted text lines.
        "ocr_confidence": archive.ocr_confidence,  # Stores OCR confidence or None.
        "page_count": archive.page_count,  # Stores page count.
        "timestamp": archive.timestamp,  # Stores datetime timestamp.
        "parser_version": archive.parser_version,  # Stores parser version.
        "linked_record_ids": [],  # Starts empty until purchases are inserted.
        "reprocessed": False,  # Marks this archive as not reprocessed.
    }  # Ends the raw_inputs document.


def _build_purchase_document(item: ApprovedItem, raw_input_id: str) -> dict[str, Any]:  # Builds one purchase document.
    return {  # Starts the purchase document.
        "canonical_name": item.canonical_name,  # Stores normalized item name.
        "raw_name": item.raw_name,  # Stores original parsed item name.
        "product_ref": item.product_ref,  # Stores matched product reference.
        "store_ref": item.store_id,  # Stores Phase 1 store identifier.
        "quantity": item.quantity,  # Stores quantity as Decimal.
        "quantity_unit": item.quantity_unit,  # Stores quantity unit.
        "unit_price": item.unit_price,  # Stores unit price as Decimal.
        "line_total": item.line_total,  # Stores line total as Decimal.
        "purchase_date": item.purchase_date,  # Stores purchase date as date.
        "parse_confidence": item.confidence,  # Stores confidence score.
        "parser_version": item.parser_version,  # Stores parser version.
        "raw_input_ref": raw_input_id,  # Links purchase to raw_inputs archive.
        "user_corrected": False,  # Defaults to not manually corrected at load time.
        **item.extra_fields,  # Adds approved extra fields.
    }  # Ends the purchase document.
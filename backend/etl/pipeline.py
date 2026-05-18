# =============================================================================  # File header separator.
# File: pipeline.py  # Identifies this ETL orchestration file.
# Project: Grocery Intelligence Platform  # Identifies the project.
# Author: Anita Woodford  # Identifies the project author.
# Description: Orchestrates Stage 1 extraction, Stage 2 parsing/normalization, correction, and Stage 3 loading.  # Explains the file purpose.
# Security Note: Pipeline orchestration must not store credentials, tokens, or payment card data.  # States security boundary.
# SRS Traceability: Supports SRS v5.0 Section 12 ET-001 through ET-005 and Section 13 HC-001 through HC-009.  # Maps to SRS.
# SDD Traceability: Supports SDD v5.0 Section 4 ETL Pipeline Design and Section 8 API Endpoint Design.  # Maps to SDD.
# =============================================================================  # File header separator.

from __future__ import annotations  # Enables modern type hint behavior.

from datetime import UTC  # Imports UTC for timezone-aware timestamps.
from datetime import date  # Imports date for loader purchase_date values.
from datetime import datetime  # Imports datetime for raw input archives.
from decimal import Decimal  # Imports Decimal for exact item quantity and money values.
from pathlib import Path  # Imports Path for uploaded PDF paths.
from typing import Any  # Imports Any for dependency dictionaries.

from backend.data_access.products import ProductsDataAccess  # Imports product Data Access Layer.
from backend.data_access.purchases import PurchasesDataAccess  # Imports purchases Data Access Layer.
from backend.data_access.raw_inputs import RawInputsDataAccess  # Imports raw inputs Data Access Layer.
from backend.etl.extractor import ExtractionResult  # Imports the extractor result type.
from backend.etl.extractor import extract_pdf  # Imports Stage 1 PDF extraction.
from backend.etl.loader import ApprovedItem  # Imports the Stage 3 approved item type.
from backend.etl.loader import RawInputArchive  # Imports the Stage 3 raw input archive type.
from backend.etl.loader import load_approved_session  # Imports Stage 3 loader function.
from backend.models.correction import ApproveSessionResponse  # Imports approval response model.
from backend.models.correction import CorrectionItem  # Imports correction item model.
from backend.models.correction import CorrectionItemUpdateRequest  # Imports correction update request model.
from backend.models.correction import CorrectionSession  # Imports correction session model.
from backend.models.correction import NormalizeCorrectionRequest  # Imports normalize request model.
from backend.normalizer.rule_normalizer import normalize_product_name  # Imports Stage 2B normalizer.
from backend.parsers.heb.online_receipt_parser import PARSER_VERSION  # Imports parser version.
from backend.parsers.heb.online_receipt_parser import ParsedItem  # Imports parsed item type.
from backend.parsers.heb.online_receipt_parser import ParsedReceipt  # Imports parsed receipt type.
from backend.parsers.heb.online_receipt_parser import parse_heb_online_receipt  # Imports Stage 2A parser.
from backend.services.correction_service import CorrectionItemNotFoundError  # Imports item not-found error.
from backend.services.correction_service import CorrectionSessionNotFoundError  # Imports session not-found error.
from backend.services.correction_service import correction_session_store  # Imports shared correction session store.


HEB_ONLINE_SOURCE_TYPE: str = "heb_online_pdf"  # Defines the Phase 1 source type.
HEB_STORE_NAME: str = "HEB"  # Defines the Phase 1 store label.
HEB_STORE_REF: str = "heb"  # Defines the Phase 1 store reference used by loader.
PASTE_FILENAME: str = "pasted_heb_receipt.txt"  # Defines a synthetic filename for pasted receipt text.
PASTE_FILE_PATH: str = "paste://heb-online-receipt"  # Defines a synthetic path for pasted input.


async def create_session_from_pdf(  # Creates a correction session from an uploaded H-E-B PDF.
    file_path: str | Path,  # Receives the temporary uploaded file path.
    original_filename: str,  # Receives the original uploaded filename.
    product_access: ProductsDataAccess,  # Receives product Data Access Layer dependency.
) -> CorrectionSession:  # Returns a correction session.
    extraction_result: ExtractionResult = extract_pdf(file_path, original_filename)  # Runs Stage 1 extraction.
    parsed_receipt: ParsedReceipt = parse_heb_online_receipt(  # Runs Stage 2A parser.
        raw_lines=extraction_result.raw_lines,  # Passes extracted raw lines.
        source_type=extraction_result.source_type,  # Passes source type.
        store=extraction_result.store,  # Passes store label.
    )  # Ends parser call.
    correction_items: list[CorrectionItem] = await _build_correction_items(parsed_receipt, product_access)  # Runs Stage 2B normalization.
    return correction_session_store.create_session(  # Creates the correction session.
        source_type=extraction_result.source_type,  # Stores source type.
        store=extraction_result.store,  # Stores store label.
        raw_lines=extraction_result.raw_lines,  # Stores raw lines.
        items=correction_items,  # Stores reviewable items.
        parse_errors=parsed_receipt.parse_errors,  # Stores parse errors.
        source_metadata={  # Starts source metadata.
            "filename": extraction_result.filename,  # Stores original filename.
            "file_path": extraction_result.file_path,  # Stores archived file path.
            "ocr_confidence": extraction_result.ocr_confidence,  # Stores extraction confidence.
            "page_count": extraction_result.page_count,  # Stores page count.
            "timestamp": extraction_result.timestamp,  # Stores extraction timestamp.
            "parser_version": parsed_receipt.parser_version,  # Stores parser version.
        },  # Ends source metadata.
    )  # Ends session creation.


async def create_session_from_pasted_text(  # Creates a correction session from pasted H-E-B receipt text.
    text: str,  # Receives pasted receipt text.
    product_access: ProductsDataAccess,  # Receives product Data Access Layer dependency.
) -> CorrectionSession:  # Returns a correction session.
    raw_lines: list[str] = [line.strip() for line in text.splitlines() if line.strip()]  # Converts pasted text into raw lines.
    parsed_receipt: ParsedReceipt = parse_heb_online_receipt(  # Runs Stage 2A parser.
        raw_lines=raw_lines,  # Passes pasted raw lines.
        source_type=HEB_ONLINE_SOURCE_TYPE,  # Passes Phase 1 source type.
        store=HEB_STORE_NAME,  # Passes Phase 1 store label.
    )  # Ends parser call.
    correction_items: list[CorrectionItem] = await _build_correction_items(parsed_receipt, product_access)  # Runs Stage 2B normalization.
    return correction_session_store.create_session(  # Creates the correction session.
        source_type=HEB_ONLINE_SOURCE_TYPE,  # Stores source type.
        store=HEB_STORE_NAME,  # Stores store label.
        raw_lines=raw_lines,  # Stores pasted raw lines.
        items=correction_items,  # Stores reviewable items.
        parse_errors=parsed_receipt.parse_errors,  # Stores parse errors.
        source_metadata={  # Starts source metadata.
            "filename": PASTE_FILENAME,  # Stores synthetic filename.
            "file_path": PASTE_FILE_PATH,  # Stores synthetic file path.
            "ocr_confidence": 1.0,  # Stores text confidence.
            "page_count": 1,  # Stores synthetic page count.
            "timestamp": datetime.now(UTC),  # Stores creation timestamp.
            "parser_version": parsed_receipt.parser_version,  # Stores parser version.
        },  # Ends source metadata.
    )  # Ends session creation.


def get_correction_session(session_id: str) -> CorrectionSession:  # Retrieves one correction session.
    return correction_session_store.get_session(session_id)  # Delegates session retrieval to the session store.


def update_correction_item(  # Updates one item inside a correction session.
    session_id: str,  # Receives the session ID.
    item_id: str,  # Receives the item ID.
    update_request: CorrectionItemUpdateRequest,  # Receives validated update data.
) -> CorrectionSession:  # Returns the updated session.
    return correction_session_store.update_item(session_id, item_id, update_request)  # Delegates item update to the session store.


async def save_item_normalization(  # Saves owner-approved correction as a product alias.
    session_id: str,  # Receives the session ID.
    item_id: str,  # Receives the item ID.
    request: NormalizeCorrectionRequest,  # Receives validated normalization request.
    product_access: ProductsDataAccess,  # Receives product Data Access Layer dependency.
) -> CorrectionSession:  # Returns the updated session.
    session: CorrectionSession = correction_session_store.get_session(session_id)  # Retrieves the current session.
    target_item: CorrectionItem | None = next((item for item in session.items if item.item_id == item_id), None)  # Finds the target item.
    if target_item is None:  # Checks whether the item was found.
        raise CorrectionItemNotFoundError(item_id)  # Raises item not found.
    await product_access.add_product_alias(request.canonical_name, request.alias)  # Saves the alias through DAL.
    updated_item: CorrectionItem = target_item.model_copy(  # Builds updated item.
        update={  # Starts update fields.
            "normalized_name": request.canonical_name,  # Stores corrected canonical name.
            "matched_rule_type": "owner_alias_correction",  # Stores correction match type.
            "confidence": 1.0,  # Marks owner correction as high confidence.
            "user_corrected": True,  # Marks item as owner corrected.
        }  # Ends update fields.
    )  # Ends item copy.
    return correction_session_store.replace_item(session_id, updated_item)  # Saves the updated item in the session.


async def approve_correction_session(  # Approves a correction session and triggers Stage 3 loading.
    session_id: str,  # Receives the session ID.
    purchases_access: PurchasesDataAccess,  # Receives purchases DAL dependency.
    raw_inputs_access: RawInputsDataAccess,  # Receives raw inputs DAL dependency.
    products_access: ProductsDataAccess,  # Receives products DAL dependency.
) -> ApproveSessionResponse:  # Returns Stage 3 loading output.
    session: CorrectionSession = correction_session_store.mark_approved(session_id)  # Marks the session approved.
    approved_items: list[ApprovedItem] = [_to_approved_item(item, session) for item in session.items if not item.skipped and not item.out_of_stock]  # Converts approved items.
    raw_input_archive: RawInputArchive = _to_raw_input_archive(session)  # Converts session metadata to raw input archive.
    load_result = await load_approved_session(  # Runs Stage 3 loader.
        approved_items=approved_items,  # Passes approved items.
        raw_input_archive=raw_input_archive,  # Passes raw archive metadata.
        purchases_access=purchases_access,  # Passes purchases DAL.
        raw_inputs_access=raw_inputs_access,  # Passes raw inputs DAL.
        products_access=products_access,  # Passes products DAL.
    )  # Ends loader call.
    return ApproveSessionResponse(  # Builds approval response.
        raw_input_id=load_result.raw_input_id,  # Stores raw input ID.
        purchase_ids=load_result.purchase_ids,  # Stores purchase IDs.
        purchase_count=load_result.purchase_count,  # Stores purchase count.
        price_history_updates=load_result.price_history_updates,  # Stores price history update count.
        loader_version=load_result.loader_version,  # Stores loader version.
    )  # Ends response creation.


async def _build_correction_items(  # Converts parsed items into normalized correction items.
    parsed_receipt: ParsedReceipt,  # Receives parsed receipt.
    product_access: ProductsDataAccess,  # Receives products DAL dependency.
) -> list[CorrectionItem]:  # Returns correction items.
    correction_items: list[CorrectionItem] = []  # Initializes correction item list.
    for index, parsed_item in enumerate(parsed_receipt.items, start=1):  # Iterates through parsed items.
        correction_items.append(await _build_correction_item(index, parsed_item, parsed_receipt, product_access))  # Adds normalized correction item.
    return correction_items  # Returns all correction items.


async def _build_correction_item(  # Converts one parsed item into one correction item.
    index: int,  # Receives item index.
    parsed_item: ParsedItem,  # Receives parsed item.
    parsed_receipt: ParsedReceipt,  # Receives parsed receipt metadata.
    product_access: ProductsDataAccess,  # Receives products DAL dependency.
) -> CorrectionItem:  # Returns one correction item.
    normalization = await normalize_product_name(parsed_item.parsed_name, product_access)  # Runs Stage 2B normalization.
    combined_confidence: float = min(parsed_item.confidence, normalization.confidence)  # Combines parser and normalizer confidence conservatively.
    return CorrectionItem(  # Builds correction item.
        item_id=f"item-{index}",  # Stores stable item ID.
        raw_name=parsed_item.raw_name,  # Stores raw parsed name.
        parsed_name=parsed_item.parsed_name,  # Stores parsed name.
        normalized_name=normalization.normalized_name,  # Stores normalized name.
        product_ref=normalization.product_ref,  # Stores product reference.
        quantity=parsed_item.quantity,  # Stores quantity.
        quantity_unit=parsed_item.quantity_unit,  # Stores quantity unit.
        unit_price=parsed_item.unit_price,  # Stores unit price.
        line_total=parsed_item.line_total,  # Stores line total.
        purchase_date=parsed_receipt.order_date,  # Stores order date text.
        parser_version=parsed_item.parser_version,  # Stores parser version.
        normalizer_version=normalization.normalizer_version,  # Stores normalizer version.
        confidence=combined_confidence,  # Stores combined confidence.
        matched_rule_type=normalization.matched_rule_type,  # Stores match type.
        substituted=parsed_item.substituted,  # Stores substitution flag.
        out_of_stock=parsed_item.out_of_stock,  # Stores out-of-stock flag.
    )  # Ends correction item.


def _to_approved_item(item: CorrectionItem, session: CorrectionSession) -> ApprovedItem:  # Converts a correction item into a loader item.
    purchase_date: date = _parse_purchase_date(item.purchase_date)  # Converts purchase date text into date.
    unit_price: Decimal = item.unit_price if item.unit_price is not None else Decimal("0.00")  # Uses zero if unit price is missing.
    return ApprovedItem(  # Builds loader-approved item.
        canonical_name=item.normalized_name,  # Stores canonical name.
        raw_name=item.raw_name,  # Stores raw name.
        store_id=HEB_STORE_REF,  # Stores Phase 1 store reference.
        quantity=item.quantity,  # Stores quantity.
        quantity_unit=item.quantity_unit,  # Stores quantity unit.
        unit_price=unit_price,  # Stores unit price.
        line_total=item.line_total,  # Stores line total.
        purchase_date=purchase_date,  # Stores purchase date.
        parser_version=item.parser_version,  # Stores parser version.
        product_ref=item.product_ref,  # Stores product reference.
        confidence=item.confidence,  # Stores confidence.
        extra_fields={  # Starts extra purchase fields.
            "source_type": session.source_type,  # Stores source type.
            "user_corrected": item.user_corrected,  # Stores correction flag.
        },  # Ends extra purchase fields.
    )  # Ends ApprovedItem construction.


def _to_raw_input_archive(session: CorrectionSession) -> RawInputArchive:  # Converts a correction session into raw input archive metadata.
    metadata: dict[str, Any] = session.source_metadata  # Reads source metadata.
    timestamp_value: Any = metadata.get("timestamp", session.created_at)  # Reads timestamp with fallback.
    timestamp: datetime = timestamp_value if isinstance(timestamp_value, datetime) else session.created_at  # Ensures timestamp is datetime.
    return RawInputArchive(  # Builds raw input archive.
        source_type=session.source_type,  # Stores source type.
        store_ref=HEB_STORE_REF,  # Stores Phase 1 store reference.
        filename=str(metadata.get("filename", PASTE_FILENAME)),  # Stores filename.
        file_path=str(metadata.get("file_path", PASTE_FILE_PATH)),  # Stores file path.
        raw_lines=session.raw_lines,  # Stores raw lines.
        ocr_confidence=float(metadata.get("ocr_confidence", 1.0)),  # Stores confidence.
        page_count=int(metadata.get("page_count", 1)),  # Stores page count.
        timestamp=timestamp,  # Stores timestamp.
        parser_version=str(metadata.get("parser_version", PARSER_VERSION)),  # Stores parser version.
    )  # Ends raw archive construction.


def _parse_purchase_date(value: str | None) -> date:  # Converts parser date text into a date object.
    if value is None:  # Checks whether no date was parsed.
        return datetime.now(UTC).date()  # Uses current UTC date as fallback.
    for date_format in ("%m/%d/%Y", "%m/%d/%y"):  # Tries supported H-E-B date formats.
        try:  # Starts protected date parsing.
            return datetime.strptime(value, date_format).date()  # Returns parsed date.
        except ValueError:  # Handles format mismatch.
            continue  # Tries the next format.
    return datetime.now(UTC).date()  # Uses current UTC date if parsing fails.


def clear_sessions_for_test() -> None:  # Clears sessions for tests.
    correction_session_store.clear()  # Clears the in-memory store.


def expire_session_for_test(session_id: str) -> None:  # Expires one session for tests.
    correction_session_store.expire_session_for_test(session_id)  # Forces session expiration.
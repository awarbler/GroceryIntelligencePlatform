from __future__ import annotations  # Enables modern type hint behavior for Python 3.14.

from decimal import Decimal  # Imports Decimal so tests can compare money and quantity values exactly.
from pathlib import Path  # Imports Path so tests can read fixture files.

from backend.parsers.heb.online_receipt_parser import PARSER_VERSION  # Imports the required parser version constant.
from backend.parsers.heb.online_receipt_parser import ParsedItem  # Imports ParsedItem for output type checks.
from backend.parsers.heb.online_receipt_parser import ParsedReceipt  # Imports ParsedReceipt for output type checks.
from backend.parsers.heb.online_receipt_parser import parse_heb_online_receipt  # Imports the public parser function.


FIXTURE_PATH: Path = Path("backend/tests/fixtures/heb/sample_receipt_01.txt")  # Defines the synthetic real-format fixture path.


def _load_fixture_lines() -> list[str]:  # Defines a helper for reading the synthetic fixture.
    fixture_text: str = FIXTURE_PATH.read_text(encoding="utf-8")  # Reads the fixture text from disk.
    return fixture_text.splitlines()  # Splits the fixture into raw_lines like P1-07 extractor output.


def test_parser_version_constant_exists() -> None:  # Defines a test for the required parser version.
    assert PARSER_VERSION == "heb-online-v1.0"  # Verifies the parser version matches the P1-08 issue requirement.


def test_valid_fixture_returns_parsed_receipt() -> None:  # Defines a test for full fixture parsing.
    raw_lines: list[str] = _load_fixture_lines()  # Loads synthetic real-format HEB receipt lines.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines)  # Parses the raw lines.

    assert isinstance(receipt, ParsedReceipt)  # Verifies the parser returns a ParsedReceipt object.
    assert receipt.parser_version == PARSER_VERSION  # Verifies receipt-level parser version is included.
    assert receipt.order_number == "HEB-TEST-1001"  # Verifies order number extraction from "Order #".
    assert receipt.order_date == "4/25/26"  # Verifies order placed date extraction from the real-format footer line.
    assert receipt.subtotal == Decimal("117.16")  # Verifies subtotal extraction from "Subtotal $117.16".
    assert receipt.delivery_fee == Decimal("9.95")  # Verifies delivery fee extraction from "Delivery fee $9.95".
    assert receipt.tax == Decimal("0.17")  # Verifies tax extraction from "Tax $0.17".
    assert receipt.driver_tip == Decimal("10.97")  # Verifies driver tip extraction from "Driver tip $10.97".
    assert receipt.total == Decimal("131.25")  # Verifies total extraction from "Total $131.25".
    assert receipt.savings == Decimal("-7.00")  # Verifies savings extraction from "Your savings -$7.00".
    assert len(receipt.items) == 5  # Verifies all synthetic fixture item lines are extracted.


def test_first_standard_item_is_extracted_correctly() -> None:  # Defines a test for the first standard item.
    raw_lines: list[str] = _load_fixture_lines()  # Loads synthetic real-format HEB receipt lines.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines)  # Parses the raw lines.
    first_item: ParsedItem = receipt.items[0]  # Gets the first parsed item.

    assert first_item.raw_name == "Mission 25 Calories Yellow Corn Tortillas, 30 ct"  # Verifies real-format raw item name extraction.
    assert first_item.parsed_name == "Mission 25 Calories Yellow Corn Tortillas, 30 ct"  # Verifies parsed name remains unnormalized.
    assert first_item.quantity == Decimal("1")  # Verifies quantity extraction from "Quantity: 1 each".
    assert first_item.quantity_unit == "each"  # Verifies quantity unit extraction.
    assert first_item.unit_price == Decimal("3.13")  # Verifies unit price computed from line total divided by quantity.
    assert first_item.line_total == Decimal("3.13")  # Verifies line total extraction from "Price: $3.13".
    assert first_item.substituted is False  # Verifies standard item is not marked substituted.
    assert first_item.out_of_stock is False  # Verifies standard item is not marked out of stock.
    assert first_item.confidence == 1.0  # Verifies clear text-based item confidence.
    assert first_item.parser_version == PARSER_VERSION  # Verifies item-level parser version is included.


def test_out_of_stock_original_item_is_flagged() -> None:  # Defines a test for the unavailable original item.
    raw_lines: list[str] = _load_fixture_lines()  # Loads synthetic real-format HEB receipt lines.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines)  # Parses the raw lines.
    out_of_stock_items: list[ParsedItem] = [item for item in receipt.items if item.out_of_stock]  # Filters out-of-stock items.

    assert len(out_of_stock_items) == 1  # Verifies exactly one out-of-stock item exists in the fixture.
    assert out_of_stock_items[0].raw_name == "H-E-B Bakery Banana Nut Mini Muffins, 12 ct"  # Verifies out-of-stock item name.
    assert out_of_stock_items[0].quantity == Decimal("1")  # Verifies out-of-stock item quantity.
    assert out_of_stock_items[0].quantity_unit == "each"  # Verifies out-of-stock item unit.
    assert out_of_stock_items[0].line_total == Decimal("0.00")  # Verifies out-of-stock item total is zero.
    assert out_of_stock_items[0].substituted is False  # Verifies original unavailable item is not the replacement.
    assert out_of_stock_items[0].out_of_stock is True  # Verifies original unavailable item is flagged out of stock.


def test_replacement_item_is_flagged_as_substituted() -> None:  # Defines a test for the replacement substituted item.
    raw_lines: list[str] = _load_fixture_lines()  # Loads synthetic real-format HEB receipt lines.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines)  # Parses the raw lines.
    substituted_items: list[ParsedItem] = [item for item in receipt.items if item.substituted]  # Filters substituted replacement items.

    assert len(substituted_items) == 1  # Verifies exactly one replacement item exists in the fixture.
    assert substituted_items[0].raw_name == "H-E-B Bakery Chocolate Chip Mini Muffins, 12 ct"  # Verifies replacement item name.
    assert substituted_items[0].quantity == Decimal("1")  # Verifies replacement item quantity.
    assert substituted_items[0].quantity_unit == "each"  # Verifies replacement item unit.
    assert substituted_items[0].unit_price == Decimal("5.23")  # Verifies replacement item unit price.
    assert substituted_items[0].line_total == Decimal("5.23")  # Verifies replacement item line total.
    assert substituted_items[0].substituted is True  # Verifies replacement item is marked substituted.
    assert substituted_items[0].out_of_stock is False  # Verifies replacement item is not marked out of stock.
    assert substituted_items[0].confidence == 1.0  # Verifies replacement item confidence.


def test_weighted_item_quantity_and_unit_are_extracted() -> None:  # Defines a test for weighted produce quantity parsing.
    raw_lines: list[str] = _load_fixture_lines()  # Loads synthetic real-format HEB receipt lines.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines)  # Parses the raw lines.
    banana_item: ParsedItem = next(item for item in receipt.items if item.raw_name.startswith("Fresh Bunch of Bananas"))  # Finds banana item.

    assert banana_item.quantity == Decimal("2.4")  # Verifies decimal quantity extraction.
    assert banana_item.quantity_unit == "lbs"  # Verifies weight unit extraction.
    assert banana_item.line_total == Decimal("0.74")  # Verifies weighted item line total.
    assert banana_item.unit_price == Decimal("0.31")  # Verifies computed unit price rounded to cents.
    assert banana_item.substituted is False  # Verifies banana item is not substituted.
    assert banana_item.out_of_stock is False  # Verifies banana item is not out of stock.


def test_multi_quantity_item_unit_price_is_computed() -> None:  # Defines a test for quantity greater than one.
    raw_lines: list[str] = _load_fixture_lines()  # Loads synthetic real-format HEB receipt lines.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines)  # Parses the raw lines.
    blackberry_item: ParsedItem = next(item for item in receipt.items if item.raw_name.startswith("H-E-B Premium Fresh Sweet Karoline Blackberries"))  # Finds blackberry item.

    assert blackberry_item.quantity == Decimal("2")  # Verifies quantity greater than one.
    assert blackberry_item.quantity_unit == "eachs"  # Verifies raw HEB unit spelling is preserved.
    assert blackberry_item.line_total == Decimal("8.36")  # Verifies line total extraction.
    assert blackberry_item.unit_price == Decimal("4.18")  # Verifies unit price calculation from line total divided by quantity.
    assert blackberry_item.substituted is False  # Verifies this fixture item is not part of the substitution pair.
    assert blackberry_item.out_of_stock is False  # Verifies this fixture item is not out of stock.


def test_empty_input_returns_empty_items_and_parse_errors() -> None:  # Defines a test for empty parser input.
    receipt: ParsedReceipt = parse_heb_online_receipt([])  # Parses an empty raw_lines list.

    assert receipt.items == []  # Verifies empty input returns no items.
    assert receipt.parse_errors != []  # Verifies empty input records a parse error.
    assert "No raw lines supplied" in receipt.parse_errors[0]  # Verifies the parse error explains the problem.
    assert receipt.parser_version == PARSER_VERSION  # Verifies parser version is still returned.


def test_malformed_input_returns_partial_result_with_errors() -> None:  # Defines a test for malformed but partially parseable input.
    raw_lines: list[str] = [  # Creates partially valid and partially malformed raw lines.
        "Order # HEB-TEST-2002",  # Provides valid order metadata in real HEB format.
        "Item, H-E-B Apples, 3 lb bag. Quantity: 1 each. Price: $3.00.",  # Provides one valid real-format item.
        "BROKEN ITEM LINE $not-a-number",  # Provides one malformed price-like line.
        "Total $3.00",  # Provides valid total metadata in exported PDF format.
    ]  # Ends malformed raw_lines list.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines)  # Parses malformed input.

    assert receipt.order_number == "HEB-TEST-2002"  # Verifies valid metadata still parsed.
    assert len(receipt.items) == 1  # Verifies valid item still parsed.
    assert receipt.items[0].raw_name == "H-E-B Apples, 3 lb bag"  # Verifies valid item name.
    assert receipt.items[0].quantity_unit == "each"  # Verifies valid item quantity unit.
    assert receipt.items[0].line_total == Decimal("3.00")  # Verifies valid item line total.
    assert receipt.parse_errors != []  # Verifies malformed input records parse errors.
    assert any("was not parsed" in error for error in receipt.parse_errors)  # Verifies malformed line error is present.


def test_unexpected_source_type_and_store_are_nonfatal_errors() -> None:  # Defines a test for parser input contract mismatch.
    raw_lines: list[str] = _load_fixture_lines()  # Loads synthetic real-format HEB receipt lines.
    receipt: ParsedReceipt = parse_heb_online_receipt(raw_lines, source_type="photo", store="Walmart")  # Parses with mismatched source and store.

    assert receipt.items != []  # Verifies parser still returns partial parsed data.
    assert any("Unexpected source_type" in error for error in receipt.parse_errors)  # Verifies source mismatch is recorded.
    assert any("Unexpected store" in error for error in receipt.parse_errors)  # Verifies store mismatch is recorded.


def test_parser_has_no_forbidden_imports() -> None:  # Defines a test for parser architecture boundaries.
    source_text: str = Path("backend/parsers/heb/online_receipt_parser.py").read_text(encoding="utf-8")  # Reads parser source text.
    forbidden_tokens: list[str] = [  # Defines forbidden imports for Stage 2A parser.
        "from fastapi",  # Blocks API route imports.
        "import fastapi",  # Blocks FastAPI package imports.
        "from backend.services",  # Blocks service-layer imports.
        "import backend.services",  # Blocks service package imports.
        "from backend.data_access",  # Blocks Data Access Layer imports.
        "import backend.data_access",  # Blocks Data Access Layer package imports.
        "from backend.dal",  # Blocks old DAL path imports.
        "import backend.dal",  # Blocks old DAL path package imports.
        "motor",  # Blocks Motor database driver imports.
        "pymongo",  # Blocks PyMongo database driver imports.
    ]  # Ends forbidden token list.

    for token in forbidden_tokens:  # Iterates over each forbidden token.
        assert token not in source_text  # Verifies the parser does not contain the forbidden token.
        
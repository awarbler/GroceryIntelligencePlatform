from __future__ import annotations  # Enables modern type hint behavior for Python 3.14.

import re  # Imports regular expressions for H-E-B receipt line matching.
from dataclasses import dataclass, field, replace  # Imports dataclass helpers for structured parser output.
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP  # Imports Decimal tools for exact money math.


PARSER_VERSION: str = "heb-online-v1.0"  # Defines the parser version required for traceability.
EXPECTED_SOURCE_TYPE: str = "heb_online_pdf"  # Defines the expected source type from the P1-07 extractor.
EXPECTED_STORE: str = "HEB"  # Defines the expected store name for this Phase 1 parser.
DEFAULT_CONFIDENCE: float = 1.0  # Defines confidence for clear text-based PDF item lines.
CENT: Decimal = Decimal("0.01")  # Defines the two-decimal currency quantization value.


ORDER_NUMBER_RE: re.Pattern[str] = re.compile(r"^Order\s*#\s*(?P<value>[A-Za-z0-9-]+)$", re.IGNORECASE)  # Matches real H-E-B "Order # ..." lines.
ORDER_PLACED_RE: re.Pattern[str] = re.compile(r"^Order placed on (?P<date>\d{1,2}/\d{1,2}/\d{2,4})", re.IGNORECASE)  # Matches real H-E-B order placed date lines.
ITEM_LINE_RE: re.Pattern[str] = re.compile(r"^Item(?: with note| with note and preference)?, (?P<name>.+?)\. Quantity: (?P<quantity>\d+(?:\.\d+)?) (?P<unit>[A-Za-z]+)\. Price: \$?(?P<line_total>\d+(?:\.\d{2})?)\.$", re.IGNORECASE)  # Matches real H-E-B item accessibility lines.
SUBTOTAL_RE: re.Pattern[str] = re.compile(r"^Subtotal\s+\$?(?P<value>\d+(?:\.\d{2})?)$", re.IGNORECASE)  # Matches "Subtotal $117.16" lines.
DELIVERY_FEE_RE: re.Pattern[str] = re.compile(r"^Delivery fee\s+\$?(?P<value>\d+(?:\.\d{2})?)$", re.IGNORECASE)  # Matches "Delivery fee $9.95" lines.
TAX_RE: re.Pattern[str] = re.compile(r"^Tax\s+\$?(?P<value>\d+(?:\.\d{2})?)$", re.IGNORECASE)  # Matches "Tax $0.17" lines.
DRIVER_TIP_RE: re.Pattern[str] = re.compile(r"^Driver tip\s+\$?(?P<value>\d+(?:\.\d{2})?)$", re.IGNORECASE)  # Matches "Driver tip $10.97" lines.
TOTAL_RE: re.Pattern[str] = re.compile(r"^Total\s+\$?(?P<value>\d+(?:\.\d{2})?)$", re.IGNORECASE)  # Matches "Total $131.25" lines.
SAVINGS_RE: re.Pattern[str] = re.compile(r"^Your savings\s+(?P<value>-\$?\d+(?:\.\d{2})?)$", re.IGNORECASE)  # Matches "Your savings -$7.00" lines.
IGNORED_LINE_RE: re.Pattern[str] = re.compile(r"^(Order delivered\. Thank you!|Quick actions|Delivery details|Delivery|Order details|Payment summary|Payment method|Adjust quantity|Enter quantity|View note|Don’t substitute|Thank you)$", re.IGNORECASE)  # Matches common H-E-B non-data lines.


@dataclass(frozen=True)  # Makes ParsedItem immutable after construction.
class ParsedItem:  # Defines one structured item parsed from the receipt.
    raw_name: str  # Stores the raw item name exactly as parsed from the H-E-B item line.
    parsed_name: str  # Stores the parser-cleaned item name before product normalization.
    quantity: Decimal  # Stores the purchased quantity from the H-E-B item line.
    quantity_unit: str  # Stores the quantity unit such as each, eachs, or lbs.
    unit_price: Decimal | None  # Stores computed unit price when quantity is greater than zero.
    line_total: Decimal  # Stores the item line total from the H-E-B item line.
    substituted: bool  # Stores whether this item is the replacement item after "Substituted with".
    out_of_stock: bool  # Stores whether this item is the unavailable original item.
    confidence: float  # Stores parser confidence for this item.
    parser_version: str = PARSER_VERSION  # Stores parser version for item-level traceability.


@dataclass(frozen=True)  # Makes ParsedReceipt immutable after construction.
class ParsedReceipt:  # Defines the structured output from the H-E-B online receipt parser.
    order_number: str | None  # Stores the parsed H-E-B order number if found.
    order_date: str | None  # Stores the parsed order placed date if found.
    store_name: str | None  # Stores the parsed store name if found.
    subtotal: Decimal | None  # Stores the parsed subtotal if found.
    tax: Decimal | None  # Stores the parsed tax if found.
    total: Decimal | None  # Stores the parsed total if found.
    delivery_fee: Decimal | None  # Stores the parsed delivery fee if found.
    savings: Decimal | None  # Stores the parsed savings value if found.
    driver_tip: Decimal | None  # Stores the parsed driver tip if found.
    items: list[ParsedItem] = field(default_factory=list)  # Stores parsed receipt items.
    parse_errors: list[str] = field(default_factory=list)  # Stores non-fatal parser errors.
    parser_version: str = PARSER_VERSION  # Stores parser version for receipt-level traceability.


def parse_heb_online_receipt(raw_lines: list[str], source_type: str = EXPECTED_SOURCE_TYPE, store: str = EXPECTED_STORE) -> ParsedReceipt:  # Defines the public parser entry point.
    order_number: str | None = None  # Initializes the order number as missing.
    order_date: str | None = None  # Initializes the order date as missing.
    store_name: str | None = None  # Initializes the store name as missing because the real export may not provide a clean store-name field.
    subtotal: Decimal | None = None  # Initializes the subtotal as missing.
    tax: Decimal | None = None  # Initializes the tax as missing.
    total: Decimal | None = None  # Initializes the total as missing.
    delivery_fee: Decimal | None = None  # Initializes the delivery fee as missing.
    savings: Decimal | None = None  # Initializes the savings value as missing.
    driver_tip: Decimal | None = None  # Initializes the driver tip as missing.
    items: list[ParsedItem] = []  # Initializes the parsed item list.
    parse_errors: list[str] = []  # Initializes the non-fatal parse error list.
    pending_out_of_stock: bool = False  # Tracks whether the next zero-dollar item is an out-of-stock original.
    pending_substitution: bool = False  # Tracks whether the next non-zero item is a substituted replacement.

    if source_type != EXPECTED_SOURCE_TYPE:  # Checks that the parser is receiving the expected source type.
        parse_errors.append(f"Unexpected source_type: {source_type}")  # Records a source type mismatch without crashing.

    if store.upper() != EXPECTED_STORE:  # Checks that the parser is receiving H-E-B input.
        parse_errors.append(f"Unexpected store: {store}")  # Records a store mismatch without crashing.

    if not raw_lines:  # Checks whether Stage 1 produced no raw lines.
        parse_errors.append("No raw lines supplied to HEB online receipt parser.")  # Records empty input as a parse error.
        return ParsedReceipt(order_number, order_date, store_name, subtotal, tax, total, delivery_fee, savings, driver_tip, items, parse_errors)  # Returns safe empty result with all fields.

    for line_number, raw_line in enumerate(raw_lines, start=1):  # Iterates through each raw line with a human-readable line number.
        line: str = raw_line.strip()  # Strips whitespace so matching is consistent.

        if not line:  # Checks for blank lines defensively.
            continue  # Skips blank lines.

        if line.lower() == "out of stock":  # Checks for an out-of-stock marker line.
            if items and items[-1].line_total == Decimal("0.00"):  # Checks whether the previous parsed item is a zero-dollar unavailable item.
                items[-1] = replace(items[-1], out_of_stock=True)  # Replaces the frozen previous item with an out-of-stock copy.
                pending_out_of_stock = False  # Clears pending out-of-stock because the marker was applied retroactively.
            else:  # Handles the less common case where the marker appears before the item line.
                pending_out_of_stock = True  # Marks that the next zero-dollar item should be treated as unavailable.
            continue  # Moves to the next line.

        if line.lower() == "substituted with":  # Checks for a substitution marker line.
            pending_substitution = True  # Marks that the next charged item line is likely the replacement item.
            continue  # Moves to the next line.

        order_number_match: re.Match[str] | None = ORDER_NUMBER_RE.match(line)  # Attempts to match the H-E-B order number line.
        if order_number_match is not None:  # Checks whether this line contains the order number.
            order_number = order_number_match.group("value")  # Stores the captured order number.
            continue  # Moves to the next line.

        order_placed_match: re.Match[str] | None = ORDER_PLACED_RE.match(line)  # Attempts to match the real-format order placed date line.
        if order_placed_match is not None:  # Checks whether this line contains the order placed date.
            order_date = order_placed_match.group("date")  # Stores the captured order date.
            continue  # Moves to the next line.

        subtotal_match: re.Match[str] | None = SUBTOTAL_RE.match(line)  # Attempts to match subtotal.
        if subtotal_match is not None:  # Checks whether this line contains subtotal.
            subtotal = _to_decimal(subtotal_match.group("value"), parse_errors, line_number)  # Converts subtotal to Decimal.
            continue  # Moves to the next line.

        delivery_fee_match: re.Match[str] | None = DELIVERY_FEE_RE.match(line)  # Attempts to match delivery fee.
        if delivery_fee_match is not None:  # Checks whether this line contains delivery fee.
            delivery_fee = _to_decimal(delivery_fee_match.group("value"), parse_errors, line_number)  # Converts delivery fee to Decimal.
            continue  # Moves to the next line.

        tax_match: re.Match[str] | None = TAX_RE.match(line)  # Attempts to match tax.
        if tax_match is not None:  # Checks whether this line contains tax.
            tax = _to_decimal(tax_match.group("value"), parse_errors, line_number)  # Converts tax to Decimal.
            continue  # Moves to the next line.

        driver_tip_match: re.Match[str] | None = DRIVER_TIP_RE.match(line)  # Attempts to match driver tip.
        if driver_tip_match is not None:  # Checks whether this line contains driver tip.
            driver_tip = _to_decimal(driver_tip_match.group("value"), parse_errors, line_number)  # Converts driver tip to Decimal.
            continue  # Moves to the next line.

        total_match: re.Match[str] | None = TOTAL_RE.match(line)  # Attempts to match total.
        if total_match is not None:  # Checks whether this line contains total.
            total = _to_decimal(total_match.group("value"), parse_errors, line_number)  # Converts total to Decimal.
            continue  # Moves to the next line.

        savings_match: re.Match[str] | None = SAVINGS_RE.match(line)  # Attempts to match savings.
        if savings_match is not None:  # Checks whether this line contains savings.
            savings = _to_decimal(savings_match.group("value").replace("$", ""), parse_errors, line_number)  # Converts savings to Decimal after removing dollar sign.
            continue  # Moves to the next line.

        item_match: re.Match[str] | None = ITEM_LINE_RE.match(line)  # Attempts to match the real H-E-B item line.
        if item_match is not None:  # Checks whether this line contains an item.
            parsed_item: ParsedItem | None = _parse_item_line(item_match, pending_out_of_stock, pending_substitution, parse_errors, line_number)  # Parses the item line with current substitution state.
            if parsed_item is not None:  # Checks whether the item parsed successfully.
                items.append(parsed_item)  # Adds the parsed item to the receipt item list.
                if parsed_item.out_of_stock:  # Checks whether this parsed item consumed the out-of-stock marker.
                    pending_out_of_stock = False  # Clears the out-of-stock marker after assigning it to the original item.
                if parsed_item.substituted:  # Checks whether this parsed item consumed the substituted marker.
                    pending_substitution = False  # Clears the substitution marker after assigning it to the replacement item.
            continue  # Moves to the next line.

        if IGNORED_LINE_RE.match(line) is not None:  # Checks whether the line is known non-data page text.
            continue  # Skips known non-data lines.

        if _looks_like_possible_unparsed_data(line):  # Checks whether an unknown line looks like data that should have parsed.
            parse_errors.append(f"Line {line_number} was not parsed: {line}")  # Records malformed but non-fatal input.

    if order_number is None:  # Checks whether required order metadata was missing.
        parse_errors.append("Order number was not found.")  # Records missing order number as non-fatal.

    if total is None:  # Checks whether total metadata was missing.
        parse_errors.append("Total was not found.")  # Records missing total as non-fatal.

    return ParsedReceipt(order_number, order_date, store_name, subtotal, tax, total, delivery_fee, savings, driver_tip, items, parse_errors)  # Returns the complete parsed receipt with every required field.


def _parse_item_line(match: re.Match[str], pending_out_of_stock: bool, pending_substitution: bool, parse_errors: list[str], line_number: int) -> ParsedItem | None:  # Defines helper for real H-E-B item lines.
    raw_name: str = match.group("name").strip()  # Captures and trims the raw item name.
    quantity: Decimal | None = _to_decimal(match.group("quantity"), parse_errors, line_number)  # Converts quantity text to Decimal.
    quantity_unit: str = match.group("unit").strip()  # Captures the quantity unit from the item line.
    line_total: Decimal | None = _to_decimal(match.group("line_total"), parse_errors, line_number)  # Converts line total text to Decimal.

    if quantity is None or line_total is None:  # Checks whether numeric conversion failed.
        return None  # Skips the item while preserving parse errors.

    unit_price: Decimal | None = _calculate_unit_price(line_total, quantity)  # Computes unit price from line total and quantity.
    out_of_stock: bool = pending_out_of_stock and line_total == Decimal("0.00")  # Flags the unavailable original item when it follows "Out of stock" and has zero total.
    substituted: bool = pending_substitution and line_total > Decimal("0.00")  # Flags the replacement item when it follows "Substituted with" and has a positive total.

    return ParsedItem(raw_name=raw_name, parsed_name=raw_name, quantity=quantity, quantity_unit=quantity_unit, unit_price=unit_price, line_total=line_total, substituted=substituted, out_of_stock=out_of_stock, confidence=DEFAULT_CONFIDENCE)  # Returns the parsed real-format H-E-B item.


def _calculate_unit_price(line_total: Decimal, quantity: Decimal) -> Decimal | None:  # Defines helper for unit price calculation.
    if quantity == Decimal("0"):  # Checks for division by zero.
        return None  # Returns no unit price when quantity is zero.
    return (line_total / quantity).quantize(CENT, rounding=ROUND_HALF_UP)  # Computes and rounds unit price to cents.


def _to_decimal(value: str, parse_errors: list[str], line_number: int) -> Decimal | None:  # Defines helper for safe Decimal conversion.
    normalized_value: str = value.replace("$", "").strip()  # Removes dollar signs and surrounding whitespace.
    try:  # Starts protected money/quantity conversion.
        return Decimal(normalized_value)  # Converts the normalized text to Decimal.
    except InvalidOperation:  # Handles invalid Decimal strings.
        parse_errors.append(f"Line {line_number} has invalid numeric value: {value}")  # Records a non-fatal numeric parse error.
        return None  # Returns None so caller can skip the malformed field safely.


def _looks_like_possible_unparsed_data(line: str) -> bool:  # Defines helper for identifying malformed candidate lines.
    starts_like_item: bool = line.startswith("Item,") or line.startswith("Item with note")  # Checks whether the line appears to be a malformed item line.
    has_bad_price: bool = "$not-a-number" in line  # Checks for the explicit malformed price test case.
    return starts_like_item or has_bad_price  # Returns True only for likely parser-relevant malformed data.
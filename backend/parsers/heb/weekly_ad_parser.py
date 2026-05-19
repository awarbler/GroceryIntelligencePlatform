# =============================================================================
# File: backend/parsers/heb/weekly_ad_parser.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Purpose: Parse H-E-B weekly ad text into structured ad deal items.
# Security Note: This parser processes public weekly ad text only.
# SRS Traceability: Supports SRS v5.0 Section 7 AD-001 through AD-010.
# SDD Traceability: Supports SDD v5.0 Section 5.1 parser design and Section 7.5 ads collection.
# =============================================================================

from __future__ import annotations  # Enables modern type annotations.

import re  # Supports pattern matching for prices and date ranges.
from dataclasses import dataclass  # Provides small typed parser result objects.
from datetime import date  # Represents parsed ad start and end dates.
from decimal import Decimal  # Represents money values exactly.

from backend.models.ad import DealType  # Imports approved deal type enum.
from backend.parsers.deal_semantic import classify_deal_type  # Classifies raw ad text into DealType.


PARSER_VERSION: str = "heb-weekly-ad-v1.0"  # Stores parser version for traceability.


@dataclass(frozen=True)  # Creates an immutable parsed ad item object.
class ParsedWeeklyAdItem:  # Represents one parsed weekly ad item.
    raw_text: str  # Stores the original block text.
    item_name: str  # Stores the parsed item name.
    sale_price: Decimal  # Stores the parsed sale price.
    regular_price: Decimal | None  # Stores the optional regular price.
    deal_type: DealType  # Stores the classified deal type.
    size: str | None  # Stores optional size text.
    confidence: float  # Stores parser confidence.


@dataclass(frozen=True)  # Creates an immutable parsed ad result object.
class ParsedWeeklyAd:  # Represents the full parsed weekly ad.
    store: str  # Stores store label.
    source_type: str  # Stores source type.
    start_date: date | None  # Stores parsed or supplied ad start date.
    end_date: date | None  # Stores parsed or supplied ad end date.
    items: list[ParsedWeeklyAdItem]  # Stores parsed ad items.
    parse_errors: list[str]  # Stores parser warnings or errors.
    parser_version: str  # Stores parser version.


def parse_heb_weekly_ad(
    raw_lines: list[str],
    source_type: str,
    store: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ParsedWeeklyAd:
    """Parse copied or extracted H-E-B weekly ad text."""
    cleaned_lines: list[str] = [line.strip() for line in raw_lines if line.strip()]  # Removes empty lines.
    parsed_start, parsed_end = _extract_date_range(cleaned_lines)  # Attempts date extraction.
    final_start: date | None = start_date or parsed_start  # Uses supplied date first, parsed date second.
    final_end: date | None = end_date or parsed_end  # Uses supplied date first, parsed date second.
    blocks: list[list[str]] = _split_item_blocks(cleaned_lines)  # Splits raw text into item blocks.
    items: list[ParsedWeeklyAdItem] = []  # Creates output item list.
    parse_errors: list[str] = []  # Creates parse error list.

    for block in blocks:  # Loops through each possible item block.
        item: ParsedWeeklyAdItem | None = _parse_item_block(block)  # Parses one item block.
        if item is None:  # Checks whether the block could not be parsed.
            parse_errors.append("Skipped unparseable ad block: " + " | ".join(block[:5]))  # Records a safe error.
            continue  # Moves to the next block.
        items.append(item)  # Adds parsed item to output list.

    return ParsedWeeklyAd(  # Returns the full parsed ad result.
        store=store,  # Stores the store label.
        source_type=source_type,  # Stores the source type.
        start_date=final_start,  # Stores final start date.
        end_date=final_end,  # Stores final end date.
        items=items,  # Stores parsed items.
        parse_errors=parse_errors,  # Stores parse errors.
        parser_version=PARSER_VERSION,  # Stores parser version.
    )


def _split_item_blocks(lines: list[str]) -> list[list[str]]:
    """Split H-E-B ad text into item blocks using Add to cart as the sentinel."""
    blocks: list[list[str]] = []  # Stores completed blocks.
    current: list[str] = []  # Stores the current block.

    for line in lines:  # Reads each line in order.
        current.append(line)  # Adds the line to the current block.
        if line.lower().startswith("add to cart"):  # Detects end of one H-E-B item block.
            blocks.append(current)  # Saves the completed block.
            current = []  # Starts a new block.

    if current:  # Keeps a trailing block from PDF extraction if no sentinel exists.
        blocks.append(current)  # Saves trailing block.

    return blocks  # Returns all blocks.


def _parse_item_block(block: list[str]) -> ParsedWeeklyAdItem | None:
    """Parse one H-E-B weekly ad item block."""
    if not block:  # Rejects empty blocks.
        return None  # Returns no item.

    item_name: str = block[0].strip()  # Uses the first line as the item name.
    prices: list[Decimal] = [_parse_money(line) for line in block if _parse_money(line) is not None]  # Extracts money values.
    prices = [price for price in prices if price is not None]  # Removes None values.

    multi_unit_price: Decimal | None = _parse_multi_unit_price(block)  # Extracts prices like "2 for 7.00".
    if multi_unit_price is not None:  # Checks whether multi-unit price was found.
        prices.append(multi_unit_price)  # Adds calculated unit price.

    if not prices:  # Requires at least one price for an ad item.
        return None  # Skips blocks without prices.

    sale_price: Decimal = prices[-1]  # Uses the last price as sale price.
    regular_price: Decimal | None = prices[0] if len(prices) > 1 else None  # Uses first price as regular price when available.
    raw_text: str = " ".join(block)  # Preserves the full original block.
    deal_type: DealType = classify_deal_type(raw_text)  # Classifies deal semantic type.
    size: str | None = _extract_size_line(block, item_name)  # Attempts to extract size.
    confidence: float = 0.9 if item_name and sale_price >= Decimal("0") else 0.5  # Assigns basic parser confidence.

    return ParsedWeeklyAdItem(  # Returns parsed ad item.
        raw_text=raw_text,  # Stores original block text.
        item_name=item_name,  # Stores item name.
        sale_price=sale_price,  # Stores sale price.
        regular_price=regular_price,  # Stores regular price.
        deal_type=deal_type,  # Stores deal type.
        size=size,  # Stores size.
        confidence=confidence,  # Stores confidence.
    )


def _parse_money(line: str) -> Decimal | None:
    """Parse a money value from one line."""
    match: re.Match[str] | None = re.search(r"\$(\d+(?:\.\d{1,2})?)", line)  # Finds dollar amount.
    if match is None:  # Handles no match.
        return None  # Returns no value.
    return Decimal(match.group(1)).quantize(Decimal("0.01"))  # Returns cents-normalized Decimal.


def _parse_multi_unit_price(block: list[str]) -> Decimal | None:
    """Parse text like 2 for 7.00 into a unit price."""
    for line in block:  # Reads each line.
        match: re.Match[str] | None = re.search(r"(\d+)\s+for\s+(\d+(?:\.\d{1,2})?)", line.lower())  # Finds multi-unit price.
        if match is None:  # Handles non-matching lines.
            continue  # Tries next line.
        quantity: Decimal = Decimal(match.group(1))  # Parses quantity.
        total: Decimal = Decimal(match.group(2))  # Parses total price.
        return (total / quantity).quantize(Decimal("0.01"))  # Returns unit price.
    return None  # Returns no multi-unit price.


def _extract_size_line(block: list[str], item_name: str) -> str | None:
    """Extract a likely size line from a block."""
    for line in block:  # Reads each line.
        if line.startswith(item_name + ","):  # Finds repeated product line with size.
            return line.replace(item_name + ",", "").strip()  # Returns size portion.
    return None  # Returns no size.


def _extract_date_range(lines: list[str]) -> tuple[date | None, date | None]:
    """Extract date range when text includes May 13th - May 19th 2026 style wording."""
    joined: str = " ".join(lines)  # Joins lines for date search.
    match: re.Match[str] | None = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?\s*-\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)?\s*(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})",
        joined,
    )  # Finds a simple H-E-B date range.
    if match is None:  # Handles missing date range.
        return None, None  # Returns no dates.

    month_name: str = match.group(1)  # Reads month name.
    start_day: int = int(match.group(2))  # Reads start day.
    end_day: int = int(match.group(3))  # Reads end day.
    year: int = int(match.group(4))  # Reads year.
    month_number: int = _month_number(month_name)  # Converts month name to number.

    return date(year, month_number, start_day), date(year, month_number, end_day)  # Returns parsed dates.


def _month_number(month_name: str) -> int:
    """Convert English month name to month number."""
    months: dict[str, int] = {  # Defines month mapping.
        "January": 1,  # Maps January.
        "February": 2,  # Maps February.
        "March": 3,  # Maps March.
        "April": 4,  # Maps April.
        "May": 5,  # Maps May.
        "June": 6,  # Maps June.
        "July": 7,  # Maps July.
        "August": 8,  # Maps August.
        "September": 9,  # Maps September.
        "October": 10,  # Maps October.
        "November": 11,  # Maps November.
        "December": 12,  # Maps December.
    }
    return months[month_name]  # Returns mapped month number.
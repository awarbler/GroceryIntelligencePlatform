# =============================================================================
# File: test_correction_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests P1-11 in-memory correction-session storage and confidence flags.
# Security Note: Tests use synthetic grocery data only.
# SRS Traceability: Supports SRS v5.0 Section 13 HC-001 through HC-009.
# SDD Traceability: Supports SDD v5.0 correction workflow design.
# =============================================================================

from __future__ import annotations  # Enables modern type hint behavior.

from decimal import Decimal  # Imports Decimal for exact item values.

import pytest  # Imports pytest for assertions.

from backend.models.correction import CorrectionItem  # Imports correction item model.
from backend.models.correction import CorrectionItemUpdateRequest  # Imports update request model.
from backend.services.correction_service import CorrectionSessionNotFoundError  # Imports missing session error.
from backend.services.correction_service import InMemoryCorrectionSessionStore  # Imports session store.


def _item(confidence: float) -> CorrectionItem:  # Creates a synthetic correction item.
    return CorrectionItem(  # Returns a valid correction item.
        item_id=f"item-{confidence}",  # Sets item ID based on confidence.
        raw_name="HEB MILK",  # Sets raw name.
        parsed_name="HEB MILK",  # Sets parsed name.
        normalized_name="H-E-B Milk",  # Sets normalized name.
        quantity=Decimal("1"),  # Sets quantity.
        quantity_unit="each",  # Sets quantity unit.
        unit_price=Decimal("3.99"),  # Sets unit price.
        line_total=Decimal("3.99"),  # Sets line total.
        parser_version="heb-online-v1.0",  # Sets parser version.
        confidence=confidence,  # Sets confidence.
    )  # Ends item creation.


def test_create_session_applies_required_review_flag() -> None:  # Tests confidence below 0.70.
    store: InMemoryCorrectionSessionStore = InMemoryCorrectionSessionStore()  # Creates a fresh store.
    session = store.create_session("heb_online_pdf", "HEB", ["raw"], [_item(0.50)], [], {})  # Creates a session.
    assert session.items[0].review_required is True  # Verifies required review.
    assert session.items[0].review_suggested is False  # Verifies suggested review false.
    assert session.items[0].auto_accepted is False  # Verifies auto accepted false.


def test_create_session_applies_suggested_review_flag() -> None:  # Tests confidence from 0.70 to 0.84.
    store: InMemoryCorrectionSessionStore = InMemoryCorrectionSessionStore()  # Creates a fresh store.
    session = store.create_session("heb_online_pdf", "HEB", ["raw"], [_item(0.70)], [], {})  # Creates a session.
    assert session.items[0].review_required is False  # Verifies required review false.
    assert session.items[0].review_suggested is True  # Verifies suggested review.
    assert session.items[0].auto_accepted is False  # Verifies auto accepted false.


def test_create_session_applies_auto_accepted_flag() -> None:  # Tests confidence 0.85 and above.
    store: InMemoryCorrectionSessionStore = InMemoryCorrectionSessionStore()  # Creates a fresh store.
    session = store.create_session("heb_online_pdf", "HEB", ["raw"], [_item(0.85)], [], {})  # Creates a session.
    assert session.items[0].review_required is False  # Verifies required review false.
    assert session.items[0].review_suggested is False  # Verifies suggested review false.
    assert session.items[0].auto_accepted is True  # Verifies auto accepted.


def test_update_item_changes_session_data() -> None:  # Tests correction item editing.
    store: InMemoryCorrectionSessionStore = InMemoryCorrectionSessionStore()  # Creates a fresh store.
    session = store.create_session("heb_online_pdf", "HEB", ["raw"], [_item(1.0)], [], {})  # Creates a session.
    updated = store.update_item(session.session_id, "item-1.0", CorrectionItemUpdateRequest(normalized_name="Corrected Milk"))  # Updates item.
    assert updated.items[0].normalized_name == "Corrected Milk"  # Verifies item was changed.
    assert updated.items[0].user_corrected is True  # Verifies correction flag.


def test_expired_session_is_not_found() -> None:  # Tests TTL expiration behavior.
    store: InMemoryCorrectionSessionStore = InMemoryCorrectionSessionStore()  # Creates a fresh store.
    session = store.create_session("heb_online_pdf", "HEB", ["raw"], [_item(1.0)], [], {})  # Creates a session.
    store.expire_session_for_test(session.session_id)  # Forces expiration.
    with pytest.raises(CorrectionSessionNotFoundError):  # Expects missing-session error.
        store.get_session(session.session_id)  # Attempts to retrieve expired session.
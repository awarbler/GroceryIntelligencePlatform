# =============================================================================
# File: test_raw_input.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests RawInputModel validation rules using fixed pytest examples.
# Security Note: Tests use fake ObjectIds and fake file metadata only.
# SRS Traceability: Supports SRS v5.0 raw input validation and ETL traceability requirements.
# SDD Traceability: Supports SDD v5.0 backend model validation and parser pipeline testing.
# =============================================================================

from __future__ import (
    annotations,
)  # Enables postponed evaluation of type hints for cleaner test annotations.

from datetime import (
    datetime,
    timezone,
)  # Imports datetime tools for timestamp test values.

import pytest  # Imports pytest for assertions and exception testing.
from pydantic import (
    ValidationError,
)  # Imports Pydantic validation error type for invalid model tests.

from backend.models.purchase import (
    InputType,
)  # Imports the shared source type enum used by RawInputModel.
from backend.models.raw_input import RawInputModel  # Imports the model under test.


def test_raw_input_model_valid() -> (
    None
):  # Verifies that a complete valid raw input model can be created.
    raw_input = RawInputModel(  # Creates a valid RawInputModel instance.
        source_type=InputType.PDF,  # Uses a valid InputType enum value imported from purchase.py.
        store_ref="507f1f77bcf86cd799439011",  # Provides a valid fake MongoDB ObjectId for the store reference.
        filename="heb_receipt.pdf",  # Provides a fake source filename.
        file_path="uploads/heb_receipt.pdf",  # Provides a fake stored file path.
        raw_lines=[
            "H-E-B",
            "Milk 3.98",
            "Coupon -1.00",
        ],  # Provides fake extracted text lines.
        ocr_confidence=0.97,  # Provides a valid OCR confidence value.
        page_count=2,  # Provides a valid page count greater than or equal to one.
        timestamp=datetime(
            2026, 5, 14, tzinfo=timezone.utc
        ),  # Provides a deterministic UTC timestamp for the test.
        linked_record_ids=[
            "507f1f77bcf86cd799439012"
        ],  # Provides a valid fake linked parsed record id.
        reprocessed=False,  # Marks the input as not reprocessed.
        parser_version="heb-online-v1",  # Provides a fake parser version string.
    )

    assert (
        raw_input.source_type == InputType.PDF
    )  # Confirms the source type was stored as the enum value.
    assert raw_input.store_ref is not None  # Confirms the store reference was accepted.
    assert (
        raw_input.filename == "heb_receipt.pdf"
    )  # Confirms the filename was stored correctly.
    assert (
        raw_input.file_path == "uploads/heb_receipt.pdf"
    )  # Confirms the file path was stored correctly.
    assert raw_input.raw_lines == [
        "H-E-B",
        "Milk 3.98",
        "Coupon -1.00",
    ]  # Confirms raw lines were stored correctly.
    assert (
        raw_input.ocr_confidence == 0.97
    )  # Confirms OCR confidence was stored correctly.
    assert raw_input.page_count == 2  # Confirms page count was stored correctly.
    assert (
        raw_input.linked_record_ids is not None
    )  # Confirms linked record references were accepted.
    assert (
        raw_input.reprocessed is False
    )  # Confirms the reprocessed flag was stored correctly.
    assert (
        raw_input.parser_version == "heb-online-v1"
    )  # Confirms parser version was stored correctly.


def test_raw_input_rejects_bad_source_type() -> (
    None
):  # Verifies that invalid source_type values are rejected.
    with pytest.raises(
        ValidationError
    ):  # Expects Pydantic to raise a validation error.
        RawInputModel(  # Attempts to create an invalid RawInputModel instance.
            source_type="BAD_SOURCE_TYPE",  # Provides an invalid value not included in the InputType enum.
            store_ref="507f1f77bcf86cd799439011",  # Provides a valid fake MongoDB ObjectId for the store reference.
            filename="heb_receipt.pdf",  # Provides a fake source filename.
            file_path="uploads/heb_receipt.pdf",  # Provides a fake stored file path.
            raw_lines=["H-E-B", "Milk 3.98"],  # Provides fake extracted text lines.
            ocr_confidence=0.95,  # Provides a valid OCR confidence value.
            page_count=1,  # Provides a valid page count.
            timestamp=datetime(
                2026, 5, 14, tzinfo=timezone.utc
            ),  # Provides a deterministic UTC timestamp for the test.
            linked_record_ids=[],  # Provides an empty linked record list.
            reprocessed=False,  # Marks the input as not reprocessed.
            parser_version="heb-online-v1",  # Provides a fake parser version string.
        )


def test_raw_input_rejects_extra_field() -> (
    None
):  # Verifies that undeclared fields are rejected.
    with pytest.raises(
        ValidationError
    ):  # Expects Pydantic to raise a validation error.
        RawInputModel(  # Attempts to create a RawInputModel with an extra field.
            source_type=InputType.PDF,  # Uses a valid InputType enum value.
            store_ref="507f1f77bcf86cd799439011",  # Provides a valid fake MongoDB ObjectId for the store reference.
            filename="heb_receipt.pdf",  # Provides a fake source filename.
            file_path="uploads/heb_receipt.pdf",  # Provides a fake stored file path.
            raw_lines=["H-E-B", "Milk 3.98"],  # Provides fake extracted text lines.
            ocr_confidence=0.95,  # Provides a valid OCR confidence value.
            page_count=1,  # Provides a valid page count.
            timestamp=datetime(
                2026, 5, 14, tzinfo=timezone.utc
            ),  # Provides a deterministic UTC timestamp for the test.
            linked_record_ids=[],  # Provides an empty linked record list.
            reprocessed=False,  # Marks the input as not reprocessed.
            parser_version="heb-online-v1",  # Provides a fake parser version string.
            unexpected_field="not allowed",  # Provides an undeclared field that should be rejected.
        )

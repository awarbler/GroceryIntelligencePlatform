# =============================================================================
# File: test_raw_input_generated.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Uses Hypothesis to generate RawInputModel validation cases.
# Security Note: Tests use generated fake data only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 generated validation coverage for raw input records.
# SDD Traceability: Supports SDD v5.0 generated model testing and parser pipeline validation.
# =============================================================================

from __future__ import annotations  # Enables postponed evaluation of type hints for cleaner test annotations.

from datetime import datetime, timezone  # Imports datetime tools for deterministic generated tests.

from hypothesis import given  # Imports the Hypothesis decorator for generated test cases.
from hypothesis import strategies as st  # Imports Hypothesis strategies for generated data.

from backend.models.purchase import InputType  # Imports the shared source type enum used by RawInputModel.
from backend.models.raw_input import RawInputModel  # Imports the model under test.


object_id_strategy = st.sampled_from(  # Defines a strategy that returns valid fake MongoDB ObjectId strings.
    [  # Starts the list of valid fake ObjectId strings.
        "507f1f77bcf86cd799439011",  # Provides the first valid fake ObjectId string.
        "507f1f77bcf86cd799439012",  # Provides the second valid fake ObjectId string.
        "507f1f77bcf86cd799439013",  # Provides the third valid fake ObjectId string.
    ]  # Ends the list of valid fake ObjectId strings.
)  # Ends the ObjectId strategy definition.

source_type_strategy = st.sampled_from(list(InputType))  # Generates valid InputType enum values from purchase.py.

filename_strategy = st.text(min_size=1, max_size=50).filter(lambda value: value.strip() != "")  # Generates non-empty filename text.

file_path_strategy = st.text(min_size=1, max_size=100).filter(lambda value: value.strip() != "")  # Generates non-empty file path text.

raw_lines_strategy = st.lists(st.text(max_size=80), min_size=0, max_size=10)  # Generates a small list of raw text lines.

ocr_confidence_strategy = st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))  # Generates None or a valid OCR confidence score.

page_count_strategy = st.integers(min_value=1, max_value=100)  # Generates valid positive page counts.

linked_record_ids_strategy = st.lists(object_id_strategy, min_size=0, max_size=5)  # Generates zero or more valid linked ObjectIds.

reprocessed_strategy = st.booleans()  # Generates true or false reprocessed values.

parser_version_strategy = st.text(min_size=1, max_size=30).filter(lambda value: value.strip() != "")  # Generates non-empty parser version text.


@given(  # Starts the generated RawInputModel validation test.
    source_type=source_type_strategy,  # Generates valid source type values.
    store_ref=object_id_strategy,  # Generates valid store reference ObjectIds.
    filename=filename_strategy,  # Generates valid filename strings.
    file_path=file_path_strategy,  # Generates valid file path strings.
    raw_lines=raw_lines_strategy,  # Generates valid raw line lists.
    ocr_confidence=ocr_confidence_strategy,  # Generates valid OCR confidence values.
    page_count=page_count_strategy,  # Generates valid page count values.
    linked_record_ids=linked_record_ids_strategy,  # Generates valid linked record ObjectId lists.
    reprocessed=reprocessed_strategy,  # Generates valid reprocessed boolean values.
    parser_version=parser_version_strategy,  # Generates valid parser version strings.
) 
def test_generated_raw_input_model_accepts_valid_values(  # Tests that generated valid values build a RawInputModel.
    source_type: InputType,  # Receives a generated InputType value.
    store_ref: str,  # Receives a generated fake store ObjectId string.
    filename: str,  # Receives a generated filename string.
    file_path: str,  # Receives a generated file path string.
    raw_lines: list[str],  # Receives a generated list of raw text lines.
    ocr_confidence: float | None,  # Receives a generated OCR confidence value or None.
    page_count: int,  # Receives a generated page count.
    linked_record_ids: list[str],  # Receives generated fake linked ObjectId strings.
    reprocessed: bool,  # Receives a generated reprocessed flag.
    parser_version: str,  # Receives a generated parser version string.
) -> None:  # Declares that this test returns nothing.
    raw_input = RawInputModel(  # Creates a RawInputModel with generated valid values.
        source_type=source_type,  # Stores the generated valid source type.
        store_ref=store_ref,  # Stores the generated valid store reference.
        filename=filename,  # Stores the generated filename.
        file_path=file_path,  # Stores the generated file path.
        raw_lines=raw_lines,  # Stores the generated raw lines.
        ocr_confidence=ocr_confidence,  # Stores the generated OCR confidence value.
        page_count=page_count,  # Stores the generated page count.
        timestamp=datetime(2026, 5, 14, tzinfo=timezone.utc),  # Stores a deterministic UTC timestamp.
        linked_record_ids=linked_record_ids,  # Stores the generated linked record references.
        reprocessed=reprocessed,  # Stores the generated reprocessed flag.
        parser_version=parser_version,  # Stores the generated parser version.
    )  

    assert raw_input.source_type == source_type  # Confirms the generated source type was stored correctly.
    assert raw_input.filename == filename  # Confirms the generated filename was stored correctly.
    assert raw_input.file_path == file_path  # Confirms the generated file path was stored correctly.
    assert raw_input.raw_lines == raw_lines  # Confirms the generated raw lines were stored correctly.
    assert raw_input.ocr_confidence == ocr_confidence  # Confirms the generated OCR confidence was stored correctly.
    assert raw_input.page_count == page_count  # Confirms the generated page count was stored correctly.
    assert raw_input.reprocessed == reprocessed  # Confirms the generated reprocessed flag was stored correctly.
    assert raw_input.parser_version == parser_version  # Confirms the generated parser version was stored correctly.
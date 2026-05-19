# =============================================================================
# File: backend/etl/extractor.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Stage 1 ETL extractor for HEB online receipt PDFs.
# Security Note: Extracted data must not contain personally identifiable information (PII).
# SRS Traceability: Supports SRS v5.0 SE-008, SE-
# 009, ET-001 through ET-005, and HC-001 through HC-009.
# SDD Traceability: Supports SDD v5.0 ETL design and modular architecture.
# ==============================================================================

"""Stage 1 ETL extractor for HEB online receipt PDFs."""  # Defines the module purpose for maintainers and tests.

from __future__ import annotations  # Enables modern type hints and forward references safely.

from dataclasses import dataclass  # Imports dataclass for a simple typed extraction result object.
from datetime import UTC, datetime  # Imports UTC-aware datetime support for extraction timestamps.
from pathlib import Path  # Imports Path for safe cross-platform file path handling.
from shutil import copy2  # Imports copy2 so archived files preserve useful file metadata.

import pdfplumber  # Imports pdfplumber for text extraction from text-based PDF files.


MIN_TEXT_CHARS_PER_PAGE: int = 50  # Defines the minimum average extracted characters per page for a text-based PDF.
RECEIPT_UPLOAD_DIR: Path = Path("uploads") / "receipts"  # Defines the permanent archive folder for receipt uploads.
HEB_ONLINE_SOURCE_TYPE: str = "heb_online_pdf"  # Defines the Phase 1 source type for HEB online receipt PDFs.
HEB_STORE_NAME: str = "HEB"  # Defines the store label used by the extractor for Phase 1 HEB receipts.
TEXT_PDF_CONFIDENCE: float = 1.0  # Defines confidence for text PDFs because OCR is not used.
IMAGE_PDF_CONFIDENCE: float = 0.0  # Defines confidence for unsupported image-based PDFs.


class UnsupportedPdfError(ValueError):  # Defines a specific error for PDFs that Phase 1 cannot process.
    """Raised when a PDF cannot be processed by the Phase 1 text extractor."""  # Documents the custom exception purpose.


@dataclass(frozen=True)  # Creates an immutable result object so extraction output is stable after creation.
class ExtractionResult:  # Defines the output contract for Stage 1 extraction.
    """Structured output returned by the Stage 1 extractor."""  # Documents that this class is the extractor output contract.

    source_type: str  # Stores the input source type for downstream traceability.
    store: str  # Stores the store name connected to this extraction.
    raw_lines: list[str]  # Stores extracted non-empty raw text lines in PDF order.
    filename: str  # Stores the original uploaded filename.
    file_path: str  # Stores the permanent archived file path.
    ocr_confidence: float  # Stores extraction confidence; text PDFs use 1.0 because no OCR is used.
    image_based: bool  # Stores whether the PDF appeared image-based or too low-text for Phase 1.
    page_count: int  # Stores the number of PDF pages read by pdfplumber.
    timestamp: datetime  # Stores the UTC timestamp when extraction completed.


def extract_pdf(file_path: str | Path, original_filename: str) -> ExtractionResult:  # Defines the public Stage 1 extraction function.
    """Validate, archive, and extract raw text lines from a text-based PDF."""  # Describes the public extractor behavior.

    source_path: Path = Path(file_path)  # Converts the input file path into a Path object.
    _validate_pdf_path(source_path)  # Validates that the input exists and has a .pdf extension.

    archived_path: Path = _save_to_archive(source_path, original_filename)  # Saves the PDF before extraction for raw data preservation.
    raw_lines, image_based, page_count = _extract_pdf_text(archived_path)  # Extracts raw lines and PDF metadata from the archived copy.

    if image_based:  # Checks whether the PDF is unsupported for Phase 1.
        raise UnsupportedPdfError(  # Raises a clear Phase 1 unsupported error instead of silently returning bad data.
            "Image-based PDFs are not supported in Phase 1. "  # Explains the immediate reason the file was rejected.
            "Upload a text-based HEB online receipt PDF instead."  # Gives the expected valid input type.
        )  # Ends the unsupported PDF error construction.

    return ExtractionResult(  # Returns the complete Stage 1 output contract.
        source_type=HEB_ONLINE_SOURCE_TYPE,  # Records that this extraction came from an HEB online PDF.
        store=HEB_STORE_NAME,  # Records that this extraction is for HEB Phase 1.
        raw_lines=raw_lines,  # Returns the extracted non-empty text lines.
        filename=original_filename,  # Preserves the original uploaded filename.
        file_path=str(archived_path),  # Returns the archived path as a string for later storage.
        ocr_confidence=TEXT_PDF_CONFIDENCE,  # Sets confidence to 1.0 because text PDFs do not use OCR.
        image_based=False,  # Marks the accepted result as not image-based.
        page_count=page_count,  # Returns the number of pages found by pdfplumber.
        timestamp=datetime.now(UTC),  # Records when the extraction result was produced.
    )  # Ends the ExtractionResult construction.


def _validate_pdf_path(source_path: Path) -> None:  # Defines a helper that validates the incoming file path.
    """Validate that the source path exists and points to a PDF file."""  # Documents the validation helper.

    if not source_path.exists():  # Checks whether the source file exists on disk.
        raise ValueError(f"File not found: {source_path}")  # Rejects missing files with a clear message.

    if not source_path.is_file():  # Checks whether the path is a regular file.
        raise ValueError(f"Path is not a file: {source_path}")  # Rejects directories or non-file paths.

    if source_path.suffix.lower() != ".pdf":  # Checks whether the file extension is a PDF extension.
        raise ValueError("Stage 1 extractor only accepts PDF files in Phase 1.")  # Rejects non-PDF files for P1-07.


def _save_to_archive(source_path: Path, original_filename: str) -> Path:  # Defines a helper that archives the uploaded file.
    """Copy the uploaded PDF into uploads/receipts before extraction."""  # Documents why the archive helper exists.

    RECEIPT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Creates uploads/receipts if it does not already exist.
    safe_name: str = Path(original_filename).name  # Removes any directory components from the original filename.
    destination_path: Path = RECEIPT_UPLOAD_DIR / safe_name  # Builds the initial archive destination path.

    if destination_path.exists():  # Checks whether a file with the same name is already archived.
        destination_path = _timestamped_destination_path(safe_name)  # Creates a unique timestamped filename to prevent overwrites.

    copy2(source_path, destination_path)  # Copies the uploaded PDF into the permanent archive folder.
    return destination_path  # Returns the archived path for extraction and later traceability.


def _timestamped_destination_path(filename: str) -> Path:  # Defines a helper for duplicate upload filenames.
    """Create a timestamped archive path when a filename already exists."""  # Documents duplicate filename handling.

    original_path: Path = Path(filename)  # Converts the filename into a Path object for name parsing.
    timestamp: str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")  # Builds a high-resolution UTC timestamp string.
    new_filename: str = f"{original_path.stem}_{timestamp}{original_path.suffix}"  # Inserts the timestamp before the file extension.
    return RECEIPT_UPLOAD_DIR / new_filename  # Returns the unique archive destination path.


def _extract_pdf_text(pdf_path: Path) -> tuple[list[str], bool, int]:  # Defines the helper that reads text with pdfplumber.
    """Extract non-empty lines, image-based flag, and page count from a PDF."""  # Documents the helper output.

    raw_lines: list[str] = []  # Initializes the list that will hold extracted non-empty text lines.
    total_chars: int = 0  # Initializes the total extracted character counter.
    page_count: int = 0  # Initializes the PDF page count.

    try:  # Starts protected PDF reading so pdfplumber errors can be wrapped clearly.
        with pdfplumber.open(pdf_path) as pdf:  # Opens the archived PDF with pdfplumber.
            page_count = len(pdf.pages)  # Counts how many pages are in the PDF.

            for page in pdf.pages:  # Iterates over every page in PDF order.
                page_text: str | None = page.extract_text()  # Extracts text from the current page.

                if page_text is None:  # Checks whether pdfplumber found no text layer on this page.
                    continue  # Skips image-only or empty pages.

                total_chars += len(page_text)  # Adds the current page text length to the total character count.

                for line in page_text.splitlines():  # Splits page text into individual raw lines.
                    stripped_line: str = line.strip()  # Removes leading and trailing whitespace from the line.

                    if stripped_line:  # Keeps only non-empty lines.
                        raw_lines.append(stripped_line)  # Adds the cleaned line to the output list.

    except Exception as exc:  # Catches pdfplumber and file-reading failures.
        raise RuntimeError(f"Failed to extract text from PDF: {pdf_path}") from exc  # Raises a clear extraction failure.

    image_based: bool = _is_image_based(page_count, total_chars)  # Determines whether the PDF is unsupported low-text/image-based.

    if image_based:  # Checks whether the PDF should be treated as image-based.
        return [], True, page_count  # Returns no raw lines because Phase 1 does not support OCR.

    return raw_lines, False, page_count  # Returns extracted lines, accepted text-PDF flag, and page count.


def _is_image_based(page_count: int, total_chars: int) -> bool:  # Defines the low-text PDF detection helper.
    """Return True when a PDF has too little extracted text for Phase 1."""  # Documents image-based detection.

    if page_count <= 0:  # Checks for empty or unreadable PDFs with no pages.
        return True  # Treats no-page PDFs as unsupported.

    average_chars_per_page: float = total_chars / page_count  # Calculates average extracted text per page.
    return average_chars_per_page < MIN_TEXT_CHARS_PER_PAGE  # Flags PDFs below the text threshold as image-based.
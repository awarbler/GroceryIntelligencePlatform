"""Tests for backend.etl.extractor Stage 1 PDF text extraction."""  # Defines the test module purpose.

from __future__ import annotations  # Enables modern type hints and forward references safely.

from datetime import datetime  # Imports datetime so tests can verify timestamp type.
from pathlib import Path  # Imports Path for filesystem assertions.
from unittest.mock import MagicMock, patch  # Imports mocking tools for pdfplumber behavior.

import pytest  # Imports pytest for fixtures and exception assertions.

from backend.etl.extractor import (  # Imports the extractor objects under test.
    ExtractionResult,  # Imports the Stage 1 output dataclass.
    UnsupportedPdfError,  # Imports the custom unsupported PDF exception.
    extract_pdf,  # Imports the public extraction function.
)  # Ends the grouped import from extractor.


@pytest.fixture  # Registers this function as a pytest fixture.
def fake_pdf_file(tmp_path: Path) -> Path:  # Defines a fixture that creates a fake PDF path.
    """Create a temporary fake PDF file for extractor validation tests."""  # Documents the fixture purpose.

    pdf_path: Path = tmp_path / "heb_receipt.pdf"  # Builds a temporary PDF file path.
    pdf_path.write_bytes(b"%PDF-1.4 fake test pdf")  # Writes fake PDF bytes so the file exists.
    return pdf_path  # Returns the temporary PDF path to the test.


@pytest.fixture  # Registers this function as a pytest fixture.
def fake_txt_file(tmp_path: Path) -> Path:  # Defines a fixture that creates a non-PDF file path.
    """Create a temporary non-PDF file for rejection tests."""  # Documents the fixture purpose.

    txt_path: Path = tmp_path / "not_a_pdf.txt"  # Builds a temporary text file path.
    txt_path.write_text("not a pdf", encoding="utf-8")  # Writes text content to the file.
    return txt_path  # Returns the temporary non-PDF path to the test.


@pytest.fixture(autouse=True)  # Registers this fixture to run automatically for every test.
def redirect_upload_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:  # Defines a fixture that redirects archives.
    """Redirect uploads/receipts to a temp folder during tests."""  # Documents why the fixture exists.

    test_upload_dir: Path = tmp_path / "uploads" / "receipts"  # Builds a temporary archive folder path.
    monkeypatch.setattr("backend.etl.extractor.RECEIPT_UPLOAD_DIR", test_upload_dir)  # Redirects archive writes for tests.
    return test_upload_dir  # Returns the temporary archive folder for assertions.


def _mock_pdf_with_page_texts(page_texts: list[str | None]) -> MagicMock:  # Defines a helper that mocks a pdfplumber PDF.
    """Build a mock pdfplumber PDF object with controlled page text."""  # Documents the mock helper.

    mock_pages: list[MagicMock] = []  # Initializes the fake page list.

    for page_text in page_texts:  # Iterates over provided page text values.
        mock_page: MagicMock = MagicMock()  # Creates a mock page object.
        mock_page.extract_text.return_value = page_text  # Configures extract_text to return the provided text.
        mock_pages.append(mock_page)  # Adds the mock page to the fake PDF page list.

    mock_pdf: MagicMock = MagicMock()  # Creates a mock PDF object.
    mock_pdf.pages = mock_pages  # Assigns the fake page list to the mock PDF.
    mock_pdf.__enter__.return_value = mock_pdf  # Makes the mock work as a context manager.
    mock_pdf.__exit__.return_value = False  # Makes the context manager not suppress exceptions.
    return mock_pdf  # Returns the configured fake PDF.


def test_extraction_result_has_expected_fields() -> None:  # Defines a test for the output contract.
    """ExtractionResult should expose the P1-07 output contract fields."""  # Documents the test purpose.

    result: ExtractionResult = ExtractionResult(  # Creates a sample extraction result.
        source_type="heb_online_pdf",  # Sets the source type field.
        store="HEB",  # Sets the store field.
        raw_lines=["line 1"],  # Sets the raw lines field.
        filename="receipt.pdf",  # Sets the filename field.
        file_path="uploads/receipts/receipt.pdf",  # Sets the archived file path field.
        ocr_confidence=1.0,  # Sets the confidence field.
        image_based=False,  # Sets the image-based flag field.
        page_count=1,  # Sets the page count field.
        timestamp=datetime.now(),  # Sets the timestamp field.
    )  # Ends the sample ExtractionResult construction.

    assert result.source_type == "heb_online_pdf"  # Verifies source_type is stored correctly.
    assert result.store == "HEB"  # Verifies store is stored correctly.
    assert result.raw_lines == ["line 1"]  # Verifies raw_lines is stored correctly.
    assert result.filename == "receipt.pdf"  # Verifies filename is stored correctly.
    assert result.file_path == "uploads/receipts/receipt.pdf"  # Verifies file_path is stored correctly.
    assert result.ocr_confidence == 1.0  # Verifies ocr_confidence is stored correctly.
    assert result.image_based is False  # Verifies image_based is stored correctly.
    assert result.page_count == 1  # Verifies page_count is stored correctly.
    assert isinstance(result.timestamp, datetime)  # Verifies timestamp is a datetime object.


def test_extract_pdf_rejects_missing_file() -> None:  # Defines a test for missing file validation.
    """extract_pdf should reject a path that does not exist."""  # Documents the test purpose.

    missing_path: Path = Path("missing_receipt.pdf")  # Creates a path that should not exist.

    with pytest.raises(ValueError, match="File not found"):  # Expects a clear validation error.
        extract_pdf(missing_path, "missing_receipt.pdf")  # Calls the extractor with a missing file.


def test_extract_pdf_rejects_non_pdf(fake_txt_file: Path) -> None:  # Defines a test for extension validation.
    """extract_pdf should reject non-PDF inputs for P1-07."""  # Documents the test purpose.

    with pytest.raises(ValueError, match="only accepts PDF"):  # Expects a clear non-PDF rejection.
        extract_pdf(fake_txt_file, "not_a_pdf.txt")  # Calls the extractor with a non-PDF file.


def test_extract_pdf_returns_raw_lines_for_text_pdf(fake_pdf_file: Path) -> None:  # Defines a test for successful text extraction.
    """Text-based PDFs should return non-empty raw_lines."""  # Documents the test purpose.

    page_text: str = "HEB Online Order 123\nMilk 1 Gallon 3.48\nBread 2.48\nSubtotal 5.96"  # Creates sample text above threshold.
    mock_pdf: MagicMock = _mock_pdf_with_page_texts([page_text])  # Builds a mock PDF with text.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Replaces pdfplumber.open with the mock.
        result: ExtractionResult = extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Runs extraction.

    assert result.raw_lines == [  # Verifies raw lines are split and preserved in order.
        "HEB Online Order 123",  # Checks first extracted line.
        "Milk 1 Gallon 3.48",  # Checks second extracted line.
        "Bread 2.48",  # Checks third extracted line.
        "Subtotal 5.96",  # Checks fourth extracted line.
    ]  # Ends expected raw_lines assertion.
    assert result.image_based is False  # Verifies accepted text PDF is not image-based.
    assert result.ocr_confidence == 1.0  # Verifies text PDF confidence is 1.0.
    assert result.page_count == 1  # Verifies page count is returned.


def test_extract_pdf_filters_blank_lines(fake_pdf_file: Path) -> None:  # Defines a test for blank-line filtering.
    """Blank or whitespace-only lines should not appear in raw_lines."""  # Documents the test purpose.

    page_text: str = (  # Creates sample text with blank lines and enough text to pass the PDF text threshold.
        "Line one has enough receipt-like text to pass the threshold.\n"  # Adds a non-empty line above the threshold.
        "\n"  # Adds a blank line that should be removed.
        "   \n"  # Adds a whitespace-only line that should be removed.
        "Line two also has enough extracted text for the mock PDF.\n"  # Adds another valid text line.
        "Line three confirms blank filtering still works correctly.\n"  # Adds a final valid text line.
    )  # Ends the multiline page text string.

    mock_pdf: MagicMock = _mock_pdf_with_page_texts([page_text])  # Builds a mock PDF with blank lines.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Mocks pdfplumber.open.
        result: ExtractionResult = extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Runs extraction.

    assert result.raw_lines == [  # Verifies only non-empty stripped lines remain.
        "Line one has enough receipt-like text to pass the threshold.",  # Confirms the first valid line remains.
        "Line two also has enough extracted text for the mock PDF.",  # Confirms the second valid line remains.
        "Line three confirms blank filtering still works correctly.",  # Confirms the third valid line remains.
    ]  # Ends the expected raw_lines assertion.


def test_extract_pdf_saves_file_before_extraction(fake_pdf_file: Path) -> None:  # Defines a test for file archiving.
    """The uploaded PDF should be copied into the receipt archive folder."""  # Documents the test purpose.

    page_text: str = "HEB Online Order 123\n" + ("A" * 100)  # Creates sample text above threshold.
    mock_pdf: MagicMock = _mock_pdf_with_page_texts([page_text])  # Builds a mock PDF with text.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Mocks pdfplumber.open.
        result: ExtractionResult = extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Runs extraction.

    archived_path: Path = Path(result.file_path)  # Converts returned file path back to Path.
    assert archived_path.exists()  # Verifies the archived file exists.
    assert archived_path.name == "heb_receipt.pdf"  # Verifies the original filename is preserved.


def test_extract_pdf_does_not_overwrite_duplicate_filename(fake_pdf_file: Path) -> None:  # Defines a duplicate filename test.
    """Duplicate uploaded filenames should receive unique archived names."""  # Documents the test purpose.

    page_text: str = "HEB Online Order 123\n" + ("A" * 100)  # Creates sample text above threshold.
    mock_pdf: MagicMock = _mock_pdf_with_page_texts([page_text])  # Builds a mock PDF with text.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Mocks first extraction.
        first_result: ExtractionResult = extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Archives first upload.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Mocks second extraction.
        second_result: ExtractionResult = extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Archives duplicate upload.

    assert Path(first_result.file_path).exists()  # Verifies first archived file still exists.
    assert Path(second_result.file_path).exists()  # Verifies second archived file exists.
    assert first_result.file_path != second_result.file_path  # Verifies duplicate upload did not overwrite the first file.


def test_extract_pdf_returns_page_count_for_multiple_pages(fake_pdf_file: Path) -> None:  # Defines a test for page_count.
    """ExtractionResult should include the number of PDF pages."""  # Documents the test purpose.

    first_page_text: str = "Page one\n" + ("A" * 100)  # Creates first page text above threshold.
    second_page_text: str = "Page two\n" + ("B" * 100)  # Creates second page text above threshold.
    mock_pdf: MagicMock = _mock_pdf_with_page_texts([first_page_text, second_page_text])  # Builds a two-page mock PDF.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Mocks pdfplumber.open.
        result: ExtractionResult = extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Runs extraction.

    assert result.page_count == 2  # Verifies the result includes the two-page count.


def test_extract_pdf_rejects_low_text_image_based_pdf(fake_pdf_file: Path) -> None:  # Defines a test for image PDF rejection.
    """Low-text PDFs should be rejected as unsupported image-based PDFs."""  # Documents the test purpose.

    page_text: str = "abc"  # Creates page text below the minimum threshold.
    mock_pdf: MagicMock = _mock_pdf_with_page_texts([page_text])  # Builds a low-text mock PDF.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Mocks pdfplumber.open.
        with pytest.raises(UnsupportedPdfError, match="Image-based PDFs are not supported"):  # Expects unsupported PDF error.
            extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Runs extraction on low-text PDF.


def test_extract_pdf_rejects_empty_pdf(fake_pdf_file: Path) -> None:  # Defines a test for no-page PDFs.
    """PDFs with no pages should be rejected as unsupported."""  # Documents the test purpose.

    mock_pdf: MagicMock = _mock_pdf_with_page_texts([])  # Builds a mock PDF with no pages.

    with patch("backend.etl.extractor.pdfplumber.open", return_value=mock_pdf):  # Mocks pdfplumber.open.
        with pytest.raises(UnsupportedPdfError):  # Expects unsupported PDF error.
            extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Runs extraction on empty PDF.


def test_extract_pdf_wraps_pdfplumber_errors(fake_pdf_file: Path) -> None:  # Defines a test for extraction failures.
    """pdfplumber failures should be wrapped in RuntimeError."""  # Documents the test purpose.

    with patch("backend.etl.extractor.pdfplumber.open", side_effect=Exception("bad pdf")):  # Forces pdfplumber to fail.
        with pytest.raises(RuntimeError, match="Failed to extract text from PDF"):  # Expects wrapped extraction error.
            extract_pdf(fake_pdf_file, "heb_receipt.pdf")  # Runs extraction with failing pdfplumber.


def test_extractor_has_no_forbidden_imports() -> None:  # Defines a test for architectural boundaries.
    """extractor.py should not import API, service, DAL, or database modules."""  # Documents the test purpose.

    source_text: str = Path("backend/etl/extractor.py").read_text(encoding="utf-8")  # Reads extractor source code.
    forbidden_tokens: list[str] = [  # Defines strings that should not appear in extractor.py.
        "from fastapi",  # Blocks FastAPI route imports.
        "import fastapi",  # Blocks FastAPI package imports.
        "from backend.services",  # Blocks service-layer imports.
        "import backend.services",  # Blocks service package imports.
        "from backend.data_access",  # Blocks current Data Access Layer imports.
        "import backend.data_access",  # Blocks current Data Access Layer package imports.
        "from backend.dal",  # Blocks old DAL path imports.
        "import backend.dal",  # Blocks old DAL package imports.
        "motor",  # Blocks Motor database driver imports.
        "pymongo",  # Blocks PyMongo database driver imports.
    ]  # Ends forbidden token list.

    for token in forbidden_tokens:  # Iterates over forbidden imports.
        assert token not in source_text  # Verifies the forbidden token is absent.
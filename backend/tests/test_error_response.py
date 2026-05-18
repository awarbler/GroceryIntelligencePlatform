# =============================================================================
# File: test_error_response.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests P1-13 standard error response models, exception handlers, and test DB fixture.
# Security Note: Tests use synthetic data only.
# SRS Traceability: Supports SRS v5.0 Section 20 TS-004, TS-009 and Section 21 SE-009.
# SDD Traceability: Supports SDD v5.0 Section 8, Section 10.3, and Section 11.
# =============================================================================

from __future__ import annotations  # Enables modern type hint behavior.

import os  # Imports os for environment variable checks.
import re  # Imports regex for basic privacy checks.
from pathlib import Path  # Imports Path for reading .env.example.

import pytest  # Imports pytest for assertions and async test support.
from fastapi import FastAPI  # Imports FastAPI for handler test app construction.
from fastapi import HTTPException  # Imports HTTPException for handler test.
from fastapi.testclient import TestClient  # Imports TestClient for route testing.
from pydantic import ValidationError  # Imports ValidationError for strict model tests.

from backend.models.base import ErrorDetail  # Imports error detail model.
from backend.models.base import ErrorResponse  # Imports error response model.
from backend.models.base import SuccessResponse  # Imports success response model.


def test_error_detail_stores_field_message_and_code() -> None:  # Tests ErrorDetail field storage.
    detail = ErrorDetail(field="canonical_name", message="This field is required.", code="validation_error")  # Creates an error detail.
    assert detail.field == "canonical_name"  # Confirms field is stored.
    assert detail.message == "This field is required."  # Confirms message is stored.
    assert detail.code == "validation_error"  # Confirms code is stored.


def test_error_detail_field_is_optional() -> None:  # Tests that field is optional on ErrorDetail.
    detail = ErrorDetail(message="Something went wrong.", code="internal_error")  # Creates general error detail.
    assert detail.field is None  # Confirms field can be omitted.


def test_error_response_success_is_false() -> None:  # Tests ErrorResponse.success value.
    response = ErrorResponse(errors=[ErrorDetail(message="Not found.", code="not_found")])  # Creates failure response.
    assert response.success is False  # Confirms failure flag.


def test_error_response_rejects_extra_fields() -> None:  # Tests strict validation on ErrorResponse.
    with pytest.raises(ValidationError):  # Expects Pydantic to reject unknown fields.
        ErrorResponse(errors=[], unexpected_field=True)  # type: ignore[call-arg]


def test_success_response_success_is_true() -> None:  # Tests SuccessResponse.success value.
    response: SuccessResponse[str] = SuccessResponse(data="ok")  # Creates success response.
    assert response.success is True  # Confirms success flag.


def test_success_response_defaults_are_empty() -> None:  # Tests SuccessResponse default containers.
    response: SuccessResponse[None] = SuccessResponse()  # Creates default success response.
    assert response.errors == []  # Confirms errors defaults to empty list.
    assert response.meta == {}  # Confirms meta defaults to empty dict.


def _make_handler_test_app() -> FastAPI:  # Builds a minimal FastAPI app with handlers.
    from fastapi.exceptions import RequestValidationError  # Imports validation error type locally.

    from backend.main import _handle_http_exception  # Imports HTTPException handler.
    from backend.main import _handle_unexpected_error  # Imports unexpected exception handler.
    from backend.main import _handle_validation_error  # Imports validation handler.
    from backend.main import _handle_value_error  # Imports ValueError handler.

    test_app = FastAPI()  # Creates isolated test app.
    test_app.add_exception_handler(RequestValidationError, _handle_validation_error)  # Registers validation handler.
    test_app.add_exception_handler(ValueError, _handle_value_error)  # Registers ValueError handler.
    test_app.add_exception_handler(HTTPException, _handle_http_exception)  # Registers HTTPException handler.
    test_app.add_exception_handler(Exception, _handle_unexpected_error)  # Registers generic exception handler.

    @test_app.get("/trigger-validation")  # Defines validation test route.
    def trigger_validation(required_field: int):  # Requires query parameter.
        return {"value": required_field}  # Returns validated value.

    @test_app.get("/trigger-value-error")  # Defines ValueError test route.
    def trigger_value_error():  # Defines route function.
        raise ValueError("bad business logic input")  # Raises expected business error.

    @test_app.get("/trigger-http-error")  # Defines HTTPException test route.
    def trigger_http_error():  # Defines route function.
        raise HTTPException(status_code=404, detail="Item not found.")  # Raises HTTP 404.

    @test_app.get("/trigger-unexpected-error")  # Defines unexpected error test route.
    def trigger_unexpected():  # Defines route function.
        raise RuntimeError("something completely unexpected")  # Raises internal error that must not leak.

    return test_app  # Returns isolated app.


def test_validation_error_returns_422_error_response() -> None:  # Tests 422 handler shape.
    client = TestClient(_make_handler_test_app(), raise_server_exceptions=False)  # Creates client.
    response = client.get("/trigger-validation")  # Omits required query parameter.
    assert response.status_code == 422  # Confirms 422 status.
    body = response.json()  # Parses JSON response.
    assert body["success"] is False  # Confirms failure envelope.
    assert len(body["errors"]) >= 1  # Confirms at least one error.
    assert body["errors"][0]["code"] == "validation_error"  # Confirms validation code.


def test_value_error_returns_400_error_response() -> None:  # Tests 400 handler shape.
    client = TestClient(_make_handler_test_app(), raise_server_exceptions=False)  # Creates client.
    response = client.get("/trigger-value-error")  # Calls ValueError route.
    assert response.status_code == 400  # Confirms 400 status.
    body = response.json()  # Parses JSON response.
    assert body["success"] is False  # Confirms failure envelope.
    assert body["errors"][0]["code"] == "bad_request"  # Confirms bad request code.
    assert "bad business logic input" in body["errors"][0]["message"]  # Confirms safe message.


def test_http_exception_returns_original_status_wrapped() -> None:  # Tests HTTPException handler.
    client = TestClient(_make_handler_test_app(), raise_server_exceptions=False)  # Creates client.
    response = client.get("/trigger-http-error")  # Calls HTTPException route.
    assert response.status_code == 404  # Confirms original status.
    body = response.json()  # Parses JSON response.
    assert body["success"] is False  # Confirms failure envelope.
    assert body["errors"][0]["code"] == "http_error"  # Confirms HTTP error code.
    assert "Item not found" in body["errors"][0]["message"]  # Confirms HTTP detail is preserved.


def test_unexpected_error_returns_500_without_leaking_internals() -> None:  # Tests 500 safety.
    client = TestClient(_make_handler_test_app(), raise_server_exceptions=False)  # Creates client.
    response = client.get("/trigger-unexpected-error")  # Calls runtime error route.
    assert response.status_code == 500  # Confirms 500 status.
    body = response.json()  # Parses JSON response.
    assert body["success"] is False  # Confirms failure envelope.
    assert body["errors"][0]["code"] == "internal_error"  # Confirms internal error code.
    assert body["errors"][0]["message"] == "Internal server error."  # Confirms sanitized message.
    assert "something completely unexpected" not in response.text  # Confirms internal message is hidden.
    assert "RuntimeError" not in response.text  # Confirms exception type is hidden.


def test_test_mongo_db_env_var_exists_in_env_example() -> None:  # Tests TEST_MONGO_DB documentation.
    env_example = Path("backend/.env.example").read_text(encoding="utf-8")  # Reads env example.
    assert "TEST_MONGO_DB=grocery_intelligence_test" in env_example  # Confirms test DB variable exists.


def test_test_db_never_uses_development_db_name() -> None:  # Tests test DB name separation.
    test_db_name = os.environ.get("TEST_MONGO_DB", "grocery_intelligence_test")  # Reads test DB name.
    dev_db_name = os.environ.get("MONGO_DB", "grocery_intelligence")  # Reads dev DB name.
    assert test_db_name != dev_db_name  # Confirms names differ.
    assert "test" in test_db_name.lower()  # Confirms test DB name is obviously test-only.


@pytest.mark.asyncio  # Marks async test.
async def test_test_db_fixture_points_to_test_database(test_db) -> None:  # Tests test_db fixture database name.
    expected_name = os.environ.get("TEST_MONGO_DB")  # Reads required test DB name.
    assert expected_name is not None  # Confirms test DB env var exists.
    assert test_db.name == expected_name  # Confirms fixture uses TEST_MONGO_DB.


@pytest.mark.asyncio  # Marks async test.
async def test_test_db_cleanup_removes_inserted_documents(test_db) -> None:  # Tests insert into test DB.
    await test_db["test_cleanup_collection"].insert_one({"test_key": "test_value"})  # Inserts synthetic document.
    count = await test_db["test_cleanup_collection"].count_documents({})  # Counts inserted documents.
    assert count == 1  # Confirms insert worked.


def test_sample_heb_text_fixture_loads_fixture_file(sample_heb_text: str) -> None:  # Tests H-E-B fixture loads.
    assert len(sample_heb_text) > 0  # Confirms file has content.
    assert "Item," in sample_heb_text  # Confirms expected receipt item format exists.
    assert "Total" in sample_heb_text  # Confirms total line exists.


def test_sample_heb_text_fixture_has_no_basic_personal_data(sample_heb_text: str) -> None:  # Tests basic privacy patterns.
    assert not re.search(r"\b\d{3}-\d{3}-\d{4}\b", sample_heb_text)  # Rejects phone number pattern.
    assert not re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", sample_heb_text)  # Rejects email pattern.
    assert not re.search(r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b", sample_heb_text)  # Rejects card number pattern.
# =============================================================================
# File: main.py
# Project: GroceryIntelligence Platform
# Author: Anita Woodford
# Purpose: FASTAPI application entry point for backend API service
# Descriptions: This file creates the FastAPI application instance, defines API routes, and
# includes startup and shutdown event handlers for database connection management.
# Security Note:
#
# =============================================================================
from __future__ import annotations  # Enables modern type annotation behavior.
from collections.abc import AsyncGenerator# Imports the AsyncGenerator type for defining async generator functions.
from contextlib import asynccontextmanager # Imports the asynccontextmanager decorator for creating async context managers.

from fastapi import FastAPI # Imports the FastAPI class used to create the backend application.
from fastapi import FastAPI, HTTPException, Request, status  # Imports FastAPI app tools and exception handler types.
from slowapi.middleware import SlowAPIMiddleware  # Imports SlowAPI middleware so rate limits are enforced.

import logging  # Imports logging for safe server-side error records.

from fastapi.encoders import jsonable_encoder  # Converts Pydantic models into JSON-safe values.
from fastapi.exceptions import RequestValidationError  # Imports FastAPI request validation error type.
from fastapi.responses import JSONResponse  # Allows custom JSON error responses.

from backend.models.base import ErrorDetail  # Imports one structured error item.
from backend.models.base import ErrorResponse  # Imports standard failure response wrapper.

from backend.api.routes import register_routes  # Imports central API route registration.
from backend.data_access.token_denylist import ensure_token_denylist_indexes  # Imports token denylist index creation.
from backend.database import connect_to_mongodb  # Imports MongoDB startup connection logic.
from backend.database import disconnect_from_mongodb  # Imports MongoDB shutdown disconnection logic.
from backend.database import get_db  # Imports the active MongoDB database accessor.
from fastapi import FastAPI, HTTPException, Request, status  # Imports FastAPI app tools and exception handler types.

logger = logging.getLogger(__name__)  # Creates a logger for this module.


@asynccontextmanager  # Decorates the lifespan function to manage application startup and shutdown.
async def lifespan(app: FastAPI,) -> AsyncGenerator[None, None]:  # Defines an async context manager function for managing the application's lifespan.
    await connect_to_mongodb()  # Connects to MongoDB when the application starts up.
    await ensure_token_denylist_indexes(get_db())  # Ensures token denylist indexes exist at startup.
    yield  # Yields control back to the application to run normally.
    await (disconnect_from_mongodb())  # Disconnects from MongoDB when the application is shutting down.


async def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:  # Handles 422 validation errors.
    errors = []  # Creates a list for normalized validation errors.
    for error in exc.errors():  # Loops through Pydantic validation errors.
        field = ".".join(str(part) for part in error.get("loc", [])) or None  # Converts location tuple to readable field path.
        errors.append(ErrorDetail(field=field, message=error.get("msg", "Validation error"), code="validation_error"))  # Adds one structured validation error.
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder(ErrorResponse(errors=errors)))  # Returns standard 422 response.


async def _handle_value_error(request: Request, exc: ValueError) -> JSONResponse:  # Handles expected business-rule errors.
    logger.warning("ValueError in request %s: %s", request.url, exc)  # Logs safe server-side warning.
    response = ErrorResponse(errors=[ErrorDetail(message=str(exc), code="bad_request")])  # Builds standard 400 response.
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))  # Returns HTTP 400.


async def _handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:  # Handles explicit HTTP errors.
    response = ErrorResponse(errors=[ErrorDetail(message=str(exc.detail), code="http_error")])  # Wraps HTTPException detail.
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(response))  # Preserves original status code.


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:  # Handles unexpected failures.
    logger.exception("Unexpected error in request %s", request.url)  # Logs full error server-side only.
    response = ErrorResponse(errors=[ErrorDetail(message="Internal server error.", code="internal_error")])  # Builds sanitized 500 response.
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(response))  # Returns generic 500.

app = FastAPI(lifespan=lifespan)  # Creates the FastAPI application with existing lifespan management.
app.add_exception_handler(RequestValidationError, _handle_validation_error)  # Registers the validation error handler.
app.add_exception_handler(ValueError, _handle_value_error)  # Registers business-rule error handler.
app.add_exception_handler(HTTPException, _handle_http_exception)  # Registers HTTP exception handler.
app.add_exception_handler(Exception, _handle_unexpected_error)  # Registers sanitized fallback handler.
app.add_middleware(SlowAPIMiddleware)  # Enables SlowAPI rate-limit enforcement.
register_routes(app)  # Registers API routers and rate-limit exception handling.

def read_root():  # Creates the function that runs when someone visits the root URL.
    return {"message": "Grocery Intelligence Platform API is running"}  # Sends a simple JSON response so we know the API works.

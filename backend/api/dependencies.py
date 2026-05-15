# =============================================================================
# File: dependencies.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides reusable FastAPI dependencies for database access and JWT-protected routes.
# Security Note: Converts invalid, expired, and revoked tokens into HTTP 401 responses without leaking token details.
# SRS Traceability: Supports SRS v5.0 U-001, SE-003, SE-008, and SE-009.
# SDD Traceability: Supports SDD v5.0 authentication, API endpoint design, and API security.
# =============================================================================

from __future__ import annotations  # Enables modern type annotation behavior.

from typing import Annotated  # Imports Annotated for FastAPI dependency typing.
from typing import Any  # Imports Any for MongoDB database typing.

from fastapi import Depends  # Imports Depends for FastAPI dependency injection.
from fastapi import HTTPException  # Imports HTTPException for authentication errors.
from fastapi import Request  # Imports Request for FastAPI dependency compatibility.
from fastapi import status  # Imports status constants for readable HTTP responses.
from fastapi.security import OAuth2PasswordBearer  # Imports bearer token extraction helper.
from jwt import InvalidTokenError  # Imports PyJWT invalid token exception.

from backend.database import get_db as get_mongo_db  # Imports the existing MongoDB accessor with a clearer alias.
from backend.models.auth_models import CurrentUser  # Imports the safe current-user model.
from backend.services.auth_service import validate_token_and_get_user  # Imports token validation logic.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # Defines the login URL for bearer token docs.


async def get_database_dependency(request: Request) -> Any:  # Provides MongoDB database access as a FastAPI dependency.
    return get_mongo_db()  # Returns the current MongoDB database object from backend.database.


async def get_current_user(  # Defines the reusable dependency for protected endpoints.
    token: Annotated[str, Depends(oauth2_scheme)],  # Extracts the bearer token from the Authorization header.
    db: Annotated[Any, Depends(get_database_dependency)],  # Injects the MongoDB database dependency.
) -> CurrentUser:  # Returns the authenticated user when token validation succeeds.
    try:  # Starts token validation error handling.
        return await validate_token_and_get_user(db, token)  # Validates the JWT and loads the safe user object.
    except InvalidTokenError as exc:  # Catches invalid, expired, revoked, or malformed token errors.
        raise HTTPException(  # Converts the token error into a safe HTTP 401 response.
            status_code=status.HTTP_401_UNAUTHORIZED,  # Uses 401 for authentication failure.
            detail="Invalid or expired authentication token.",  # Returns a safe generic error message.
            headers={"WWW-Authenticate": "Bearer"},  # Tells clients bearer auth is required.
        ) from exc  # Preserves exception chaining without exposing token details.
# =============================================================================
# File: api/auth.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides FastAPI authentication endpoints for login, logout, and current-user lookup.
# Security Note: Does not log passwords, raw JWT tokens, or secrets.
# SRS Traceability: Supports SRS v5.0 U-001, U-004, SE-001, SE-003, SE-008, and SE-009.
# SDD Traceability: Supports SDD v5.0 authentication and API endpoint design.
# =============================================================================

from __future__ import annotations  # Enables modern type annotation behavior.

from typing import Annotated  # Imports Annotated for FastAPI dependency typing.
from typing import Any  # Imports Any for database dependency typing.

from fastapi import APIRouter  # Imports APIRouter for grouping auth endpoints.
from fastapi import Depends  # Imports Depends for dependency injection.
from fastapi import HTTPException  # Imports HTTPException for safe API errors.
from fastapi import Request  # Imports Request because SlowAPI requires it.
from fastapi import status  # Imports HTTP status code constants.

from backend.api.dependencies import get_current_user  # Imports the protected-route current-user dependency.
from backend.api.dependencies import get_database_dependency  # Imports the MongoDB database dependency.
from backend.api.dependencies import oauth2_scheme  # Imports the bearer token extractor.
from backend.api.rate_limit import limiter  # Imports the shared SlowAPI limiter.
from backend.config import settings  # Imports centralized settings.
from backend.models.auth_models import CurrentUser  # Imports the safe current-user model.
from backend.models.auth_models import LoginRequest  # Imports the validated login request model.
from backend.models.auth_models import TokenResponse  # Imports the standard token response model.
from backend.models.auth_models import TokenResponseData  # Imports the token response data model.
from backend.services.auth_service import authenticate_user  # Imports username/password authentication logic.
from backend.services.auth_service import create_access_token  # Imports JWT creation logic.
from backend.services.auth_service import logout_access_token  # Imports JWT logout denylist logic.

router = APIRouter(prefix="/auth", tags=["auth"])  # Creates the auth router mounted under /auth.


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)  # Registers POST /auth/login.
@limiter.limit(settings.login_rate_limit)  # Applies the configured login rate limit.
async def login(  # Defines the login endpoint handler.
    request: Request,  # Receives the request object required by SlowAPI.
    body: LoginRequest,  # Receives the validated login request body.
    db: Annotated[Any, Depends(get_database_dependency)],  # Injects the MongoDB database.
) -> TokenResponse:  # Returns the validated token response model.
    current_user = await authenticate_user(db, body.username, body.password)  # Verifies username and password.
    if current_user is None:  # Checks whether authentication failed.
        raise HTTPException(  # Raises a safe invalid-credentials response.
            status_code=status.HTTP_401_UNAUTHORIZED,  # Uses 401 for failed authentication.
            detail="Invalid username or password.",  # Avoids revealing whether username or password failed.
            headers={"WWW-Authenticate": "Bearer"},  # Tells clients bearer auth is used.
        )  # Ends the HTTPException.
    access_token, expires_at = create_access_token(current_user.username)  # Creates the JWT access token.
    return TokenResponse(  # Returns the standard response shape.
        data=TokenResponseData(  # Builds the nested response data object.
            access_token=access_token,  # Returns the JWT token to the frontend.
            token_type="bearer",  # Returns the expected token type.
            expires_at=expires_at,  # Returns the token expiration timestamp.
        )  # Ends TokenResponseData.
    )  # Ends TokenResponse.


@router.post("/logout", status_code=status.HTTP_200_OK)  # Registers POST /auth/logout.
async def logout(  # Defines the logout endpoint handler.
    token: Annotated[str, Depends(oauth2_scheme)],  # Extracts the bearer token from the request.
    current_user: Annotated[CurrentUser, Depends(get_current_user)],  # Requires a valid authenticated user.
    db: Annotated[Any, Depends(get_database_dependency)],  # Injects the MongoDB database.
) -> dict[str, object]:  # Returns the project standard response shape.
    await logout_access_token(db, token)  # Denylists the current token ID hash until expiration.
    return {"success": True, "data": {"username": current_user.username}, "errors": [], "meta": {}}  # Returns logout success.


@router.get("/me", status_code=status.HTTP_200_OK)  # Registers GET /auth/me.
async def read_current_user(  # Defines the current-user endpoint handler.
    current_user: Annotated[CurrentUser, Depends(get_current_user)],  # Requires a valid authenticated user.
) -> dict[str, object]:  # Returns the project standard response shape.
    return {"success": True, "data": current_user.model_dump(), "errors": [], "meta": {}}  # Returns the safe user object.


@router.get("/protected-test", status_code=status.HTTP_200_OK)  # Registers GET /auth/protected-test.
async def protected_test(  # Defines a temporary protected endpoint for acceptance testing.
    current_user: Annotated[CurrentUser, Depends(get_current_user)],  # Requires a valid authenticated user.
) -> dict[str, object]:  # Returns the project standard response shape.
    return {"success": True, "data": {"username": current_user.username}, "errors": [], "meta": {}}  # Returns success.
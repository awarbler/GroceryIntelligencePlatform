# =============================================================================
# File: auth_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Provides authentication business logic for password hashing, JWT creation, JWT validation, and logout token denial.
# Security Note: Plain text passwords, raw JWTs, and secrets must never be logged or stored.
# SRS Traceability: Supports SRS v5.0 U-001, SE-001, SE-003, SE-004, SE-008, and SE-009.
# SDD Traceability: Supports SDD v5.0 authentication, API security, and backend service layer architecture.
# =============================================================================

from __future__ import annotations  # Enables modern type annotation behavior.

from datetime import UTC  # Imports UTC for timezone-aware JWT timestamps.
from datetime import datetime  # Imports datetime for issued-at and expiration claims.
from datetime import timedelta  # Imports timedelta for token lifetime calculation.
from hashlib import sha256  # Imports sha256 for hashing token IDs before storage.
from typing import Any  # Imports Any for MongoDB document dictionaries.
from uuid import uuid4  # Imports uuid4 for unique JWT ID generation.

import jwt  # Imports PyJWT for JWT creation and validation.
from jwt import InvalidTokenError  # Imports PyJWT invalid token exception.
from pwdlib import PasswordHash  # Imports pwdlib password hashing support.

from backend.config import settings  # Imports centralized environment-based settings.
from backend.data_access.token_denylist import add_token_to_denylist  # Imports denylist insert/update function.
from backend.data_access.token_denylist import is_token_denied  # Imports denylist lookup function.
from backend.data_access.users import get_user_by_username  # Imports user lookup from the existing users data access file.
from backend.models.auth_models import CurrentUser  # Imports the safe current-user model.

password_hasher = PasswordHash.recommended()  # Creates the recommended password hasher.


def hash_password(plain_password: str) -> str:  # Hashes a plain text password for database storage.
    return password_hasher.hash(plain_password)  # Returns a secure password hash string.


def verify_password(plain_password: str, password_hash: str) -> bool:  # Verifies a submitted password against a stored hash.
    return password_hasher.verify(plain_password, password_hash)  # Returns True only when the password matches.


def hash_token_id(jti: str) -> str:  # Hashes a JWT ID before storing it in the denylist.
    return sha256(jti.encode("utf-8")).hexdigest()  # Returns a one-way SHA-256 digest.


def create_access_token(username: str) -> tuple[str, datetime]:  # Creates a signed JWT access token.
    issued_at = datetime.now(UTC)  # Captures the current UTC timestamp.
    expires_at = issued_at + timedelta(minutes=settings.jwt_access_token_expire_minutes)  # Calculates expiration time.
    payload = {  # Builds the JWT claims payload.
        "sub": username,  # Stores the authenticated username as the token subject.
        "iat": issued_at,  # Stores the issued-at timestamp.
        "exp": expires_at,  # Stores the expiration timestamp.
        "iss": settings.jwt_issuer,  # Stores the expected issuer claim.
        "aud": settings.jwt_audience,  # Stores the expected audience claim.
        "jti": str(uuid4()),  # Stores a unique token ID for logout invalidation.
    }  # Ends the JWT payload dictionary.
    token = jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)  # Signs and encodes the JWT.
    return token, expires_at  # Returns the token and expiration timestamp.


def decode_access_token(token: str) -> dict[str, Any]:  # Decodes and validates a JWT access token.
    payload = jwt.decode(  # Validates the token signature and registered claims.
        token,  # Passes the raw bearer token string.
        settings.jwt_secret_key.get_secret_value(),  # Uses the configured JWT signing secret.
        algorithms=[settings.jwt_algorithm],  # Restricts accepted JWT algorithms.
        audience=settings.jwt_audience,  # Requires the expected audience claim.
        issuer=settings.jwt_issuer,  # Requires the expected issuer claim.
        options={"require": ["sub", "iat", "exp", "iss", "aud", "jti"]},  # Requires critical claims.
    )  # Ends JWT decoding.
    return payload  # Returns the validated claims payload.


async def authenticate_user(db: Any, username: str, plain_password: str) -> CurrentUser | None:  # Authenticates a username and password.
    user_doc = await get_user_by_username(db, username)  # Loads the user document from the users collection.
    if user_doc is None:  # Checks whether the username was not found.
        return None  # Returns None for invalid credentials.
    password_hash = user_doc.get("password_hash")  # Reads the stored password hash from the user document.
    if not isinstance(password_hash, str):  # Checks whether the stored password hash is missing or invalid.
        return None  # Returns None for an invalid user record.
    if not verify_password(plain_password, password_hash):  # Checks whether the submitted password matches the stored hash.
        return None  # Returns None for invalid credentials.
    return CurrentUser(username=str(user_doc["username"]))  # Returns a safe user object without password_hash.


async def validate_token_and_get_user(db: Any, token: str) -> CurrentUser:  # Validates a token and returns the current user.
    payload = decode_access_token(token)  # Decodes and validates the JWT.
    jti = str(payload["jti"])  # Extracts the token ID claim.
    jti_hash = hash_token_id(jti)  # Hashes the token ID before denylist lookup.
    if await is_token_denied(db, jti_hash):  # Checks whether the token has been revoked.
        raise InvalidTokenError("Token has been revoked.")  # Raises an auth error for revoked tokens.
    username = str(payload["sub"])  # Extracts the username from the token subject.
    user_doc = await get_user_by_username(db, username)  # Confirms the token subject still exists.
    if user_doc is None:  # Checks whether the user was deleted after token creation.
        raise InvalidTokenError("Token subject does not exist.")  # Raises an auth error for missing users.
    return CurrentUser(username=username)  # Returns the safe current-user object.


async def logout_access_token(db: Any, token: str) -> None:  # Revokes a JWT access token until it expires.
    payload = decode_access_token(token)  # Decodes the token so the jti and exp claims can be read.
    jti = str(payload["jti"])  # Extracts the token ID claim.
    expires_at = datetime.fromtimestamp(int(payload["exp"]), UTC)  # Converts the exp claim into a UTC datetime.
    jti_hash = hash_token_id(jti)  # Hashes the token ID before storage.
    await add_token_to_denylist(db, jti_hash, expires_at)  # Stores the hashed token ID in the denylist.
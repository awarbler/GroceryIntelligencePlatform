from __future__ import annotations  # Enables modern type annotation behavior.

import pytest  # Imports pytest for exception-based test assertions.
from jwt import InvalidTokenError  # Imports PyJWT invalid token exception.

from backend.services.auth_service import create_access_token  # Imports JWT creation function.
from backend.services.auth_service import decode_access_token  # Imports JWT validation function.
from backend.services.auth_service import hash_password  # Imports password hashing function.
from backend.services.auth_service import verify_password  # Imports password verification function.


def test_hash_password_does_not_return_plain_password() -> None:  # Verifies password hashing does not store plain text.
    password = "CorrectHorseBatteryStaple123"  # Creates a sample password for the test.
    password_hash = hash_password(password)  # Hashes the sample password.
    assert password_hash != password  # Confirms the stored value is not the original password.


def test_verify_password_accepts_correct_password() -> None:  # Verifies the correct password passes verification.
    password = "CorrectHorseBatteryStaple123"  # Creates a sample password for the test.
    password_hash = hash_password(password)  # Hashes the sample password.
    assert verify_password(password, password_hash) is True  # Confirms the correct password verifies successfully.


def test_verify_password_rejects_wrong_password() -> None:  # Verifies the wrong password fails verification.
    password_hash = hash_password("CorrectHorseBatteryStaple123")  # Hashes the correct password.
    assert verify_password("WrongPassword123", password_hash) is False  # Confirms a wrong password does not verify.


def test_same_password_gets_different_hashes() -> None:  # Verifies password hashing uses a unique salt.
    first_hash = hash_password("SamePassword123")  # Creates the first password hash.
    second_hash = hash_password("SamePassword123")  # Creates the second password hash.
    assert first_hash != second_hash  # Confirms identical passwords produce different hashes.


def test_create_access_token_contains_required_claims() -> None:  # Verifies generated JWTs contain required claims.
    token, expires_at = create_access_token("aj")  # Creates a JWT access token for a test user.
    payload = decode_access_token(token)  # Decodes and validates the JWT.
    assert payload["sub"] == "aj"  # Confirms the subject claim stores the username.
    assert "exp" in payload  # Confirms the expiration claim exists.
    assert "iat" in payload  # Confirms the issued-at claim exists.
    assert "iss" in payload  # Confirms the issuer claim exists.
    assert "aud" in payload  # Confirms the audience claim exists.
    assert "jti" in payload  # Confirms the token ID claim exists.
    assert expires_at is not None  # Confirms the function returned an expiration datetime.


def test_decode_access_token_accepts_valid_token() -> None:  # Verifies a valid token decodes successfully.
    token, _ = create_access_token("aj")  # Creates a valid JWT access token.
    payload = decode_access_token(token)  # Decodes and validates the JWT.
    assert payload["sub"] == "aj"  # Confirms the decoded subject is the expected username.


def test_decode_access_token_rejects_invalid_token() -> None:  # Verifies invalid tokens are rejected.
    with pytest.raises(InvalidTokenError):  # Expects PyJWT to raise an invalid token error.
        decode_access_token("not-a-valid-token")  # Attempts to decode an invalid token.
from __future__ import annotations  # Enables modern type annotation behavior.

from typing import Any  # Imports Any for fake database typing.

import pytest  # Imports pytest for async test support.
from fastapi import HTTPException  # Imports HTTPException for dependency failure checks.

from backend.api.dependencies import get_current_user  # Imports the current-user dependency.
from backend.services.auth_service import create_access_token  # Imports JWT creation function.
from backend.services.auth_service import hash_password  # Imports password hashing for fake users.


class FakeUsersCollection:  # Defines a fake users collection.
    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:  # Mocks user lookup.
        return {"username": query["username"], "password_hash": hash_password("unused-password")}  # Returns a fake user.


class FakeDenylistCollection:  # Defines a fake denylist collection.
    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:  # Mocks denylist lookup.
        return None  # Returns None so the token is not denied.


class FakeDb:  # Defines a fake database.
    def __init__(self) -> None:  # Initializes the fake database.
        self.users = FakeUsersCollection()  # Stores the fake users collection.
        self.token_denylist = FakeDenylistCollection()  # Stores the fake denylist collection.

    def __getitem__(self, collection_name: str) -> Any:  # Supports db["collection_name"] access.
        return getattr(self, collection_name)  # Returns the requested fake collection.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_get_current_user_accepts_valid_token() -> None:  # Verifies get_current_user accepts a valid JWT.
    token, _ = create_access_token("aj")  # Creates a valid JWT access token.
    current_user = await get_current_user(token=token, db=FakeDb())  # Calls the dependency directly.
    assert current_user.username == "aj"  # Confirms the current user is returned.


@pytest.mark.asyncio  # Marks this as an async pytest test.
async def test_get_current_user_rejects_invalid_token() -> None:  # Verifies get_current_user rejects invalid JWTs.
    with pytest.raises(HTTPException) as exc_info:  # Expects an HTTPException.
        await get_current_user(token="not-a-valid-token", db=FakeDb())  # Calls the dependency with a bad token.
    assert exc_info.value.status_code == 401  # Confirms invalid token becomes HTTP 401.
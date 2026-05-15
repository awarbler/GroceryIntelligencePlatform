from __future__ import annotations  # Enables modern type annotation behavior.

from typing import Any  # Imports Any for fake MongoDB typing.

import pytest  # Imports pytest for fixtures.
from fastapi.testclient import TestClient  # Imports FastAPI TestClient for API tests.

from backend.api.dependencies import get_database_dependency  # Imports the database dependency for test override.
from backend.main import app  # Imports the FastAPI application.
from backend.services.auth_service import hash_password  # Imports password hashing for fake test users.


class FakeUsersCollection:  # Defines a fake MongoDB users collection.
    def __init__(self, user_doc: dict[str, Any] | None) -> None:  # Initializes the fake users collection.
        self.user_doc = user_doc  # Stores the fake user document.

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:  # Mocks MongoDB find_one behavior.
        if self.user_doc is None:  # Checks whether this fake DB has no user.
            return None  # Returns no user document.
        if query.get("username") == self.user_doc.get("username"):  # Checks whether the username matches.
            return self.user_doc  # Returns the fake user document.
        return None  # Returns no user document when the username does not match.


class FakeDenylistCollection:  # Defines a fake MongoDB token denylist collection.
    def __init__(self) -> None:  # Initializes the fake denylist collection.
        self.docs: dict[str, dict[str, Any]] = {}  # Stores fake denylist records by jti hash.

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:  # Mocks MongoDB find_one behavior.
        return self.docs.get(str(query.get("jti_hash")))  # Returns the denylist record if present.

    async def update_one(self, query: dict[str, Any], update: dict[str, Any], upsert: bool = False) -> None:  # Mocks MongoDB update_one behavior.
        self.docs[str(query["jti_hash"])] = dict(update["$set"])  # Stores the fake denylist update.


class FakeDb:  # Defines a fake MongoDB database object.
    def __init__(self, user_doc: dict[str, Any] | None) -> None:  # Initializes the fake database.
        self.users = FakeUsersCollection(user_doc)  # Creates the fake users collection.
        self.token_denylist = FakeDenylistCollection()  # Creates the fake token denylist collection.

    def __getitem__(self, collection_name: str) -> Any:  # Supports db["collection_name"] access.
        return getattr(self, collection_name)  # Returns the requested fake collection object.


@pytest.fixture()  # Registers the pytest fixture.
def client() -> TestClient:  # Creates a FastAPI test client with a fake database.
    user_doc = {"username": "aj", "password_hash": hash_password("correct-password")}  # Creates a fake valid user document.
    fake_db = FakeDb(user_doc)  # Creates a fake database containing the test user.

    async def override_get_database_dependency() -> FakeDb:  # Defines a dependency override for the fake database.
        return fake_db  # Returns the fake database.

    app.dependency_overrides[get_database_dependency] = override_get_database_dependency  # Overrides the real DB dependency.
    test_client = TestClient(app)  # Creates the FastAPI test client.
    yield test_client  # Provides the client to the test.
    app.dependency_overrides.clear()  # Clears dependency overrides after each test.


def test_login_success_returns_access_token(client: TestClient) -> None:  # Verifies valid login returns an access token.
    response = client.post("/api/v1/auth/login", json={"username": "aj", "password": "correct-password"})  # Sends valid credentials.
    assert response.status_code == 200  # Confirms login succeeds.
    body = response.json()  # Reads the response JSON.
    assert body["success"] is True  # Confirms the standard success flag is true.
    assert body["data"]["token_type"] == "bearer"  # Confirms the token type is bearer.
    assert isinstance(body["data"]["access_token"], str)  # Confirms an access token string was returned.


def test_login_failure_returns_401(client: TestClient) -> None:  # Verifies invalid login returns HTTP 401.
    response = client.post("/api/v1/auth/login", json={"username": "aj", "password": "wrong-password"})  # Sends invalid credentials.
    assert response.status_code == 401  # Confirms invalid credentials are rejected.


def test_login_missing_password_returns_422(client: TestClient) -> None:  # Verifies Pydantic rejects missing password input.
    response = client.post("/api/v1/auth/login", json={"username": "aj"})  # Sends an incomplete login request.
    assert response.status_code == 422  # Confirms validation fails before authentication logic runs.


def test_protected_endpoint_without_token_returns_401(client: TestClient) -> None:  # Verifies protected endpoints require auth.
    response = client.get("/api/v1/auth/protected-test")  # Calls a protected route without a token.
    assert response.status_code == 401  # Confirms access is denied.


def test_protected_endpoint_with_token_returns_200(client: TestClient) -> None:  # Verifies valid token allows protected access.
    login_response = client.post("/api/v1/auth/login", json={"username": "aj", "password": "correct-password"})  # Logs in.
    token = login_response.json()["data"]["access_token"]  # Extracts the returned access token.
    response = client.get("/api/v1/auth/protected-test", headers={"Authorization": f"Bearer {token}"})  # Calls protected route.
    assert response.status_code == 200  # Confirms access is allowed.


def test_logout_denies_token(client: TestClient) -> None:  # Verifies logout revokes the current token.
    login_response = client.post("/api/v1/auth/login", json={"username": "aj", "password": "correct-password"})  # Logs in.
    token = login_response.json()["data"]["access_token"]  # Extracts the returned access token.
    logout_response = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})  # Logs out.
    assert logout_response.status_code == 200  # Confirms logout succeeds.
    protected_response = client.get("/api/v1/auth/protected-test", headers={"Authorization": f"Bearer {token}"})  # Reuses token.
    assert protected_response.status_code == 401  # Confirms the logged-out token is rejected.
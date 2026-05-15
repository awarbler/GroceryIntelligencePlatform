from __future__ import annotations  # Enables forward-compatible type annotations.

from datetime import datetime  # Imports datetime for token expiration fields.

from pydantic import BaseModel  # Imports BaseModel for Pydantic request and response models.
from pydantic import ConfigDict  # Imports ConfigDict for strict Pydantic model configuration.
from pydantic import Field  # Imports Field for validation constraints and default factories.


class LoginRequest(BaseModel):  # Defines the validated request body for login.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields so raw input cannot drift into processing.

    username: str = Field(min_length=1, max_length=64)  # Stores the submitted username with length validation.
    password: str = Field(min_length=1, max_length=256)  # Stores the submitted password with length validation.


class TokenResponseData(BaseModel):  # Defines the data object returned after successful login.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected response fields.

    access_token: str  # Stores the signed JWT access token returned to the client.
    token_type: str = "bearer"  # Stores the token type expected by Authorization headers.
    expires_at: datetime  # Stores the UTC datetime when the token expires.


class TokenResponse(BaseModel):  # Defines the standard API response for login.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected response fields.

    success: bool = True  # Stores whether the request succeeded.
    data: TokenResponseData  # Stores the token response payload.
    errors: list[str] = Field(default_factory=list)  # Stores response errors using the project standard shape.
    meta: dict[str, object] = Field(default_factory=dict)  # Stores response metadata using the project standard shape.


class CurrentUser(BaseModel):  # Defines the safe authenticated user object used by protected endpoints.
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected user fields.

    username: str  # Stores the authenticated username.
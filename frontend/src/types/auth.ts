/** 
 * File: frontend/src/types/auth.ts
 * Description: This file contains the types related to authentication used across the frontend application.
 * Author: Anita Woodford
 * Created: 2024-06-01
 * License: MIT
 * Copyright (c) 2024 Anita Woodford. All rights reserved.
 * SRS Document: 
 * SDD Document: 
 * Revision History:
 */



import type { StandardResponse } from './base'; // Imports the shared backend response wrapper.

export interface LoginRequest { // Defines the request body for login.
  username: string; // Stores the username submitted from the login form.
  password: string; // Stores the password submitted from the login form.
}

export interface TokenResponseData { // Defines the successful login token payload.
  access_token: string; // Stores the JWT access token returned by the backend.
  token_type: 'bearer'; // Restricts the token type to the expected bearer value.
  expires_at: string; // Stores the token expiration timestamp as an ISO string.
}

export interface CurrentUser { // Defines the authenticated user returned by the backend.
  username: string; // Stores the authenticated username.
}

export type LoginResponse = StandardResponse<TokenResponseData>; // Wraps token data in the standard backend response shape.
export type CurrentUserResponse = StandardResponse<CurrentUser>; // Wraps current-user data in the standard backend response shape.
export type LogoutResponse = StandardResponse<null>; // Defines logout as a standard response with no data payload.
/** // Defines the file documentation block.
 * File: authStorage.ts // Identifies the auth storage helper file.
 * Project: Grocery Intelligence Platform // Identifies the project.
 * Description: Centralizes JWT token storage so page components do not manage storage directly. // Explains the file purpose.
 * Author: Anita Woodford // Identifies the author.
 * SRS Traceability: Supports SRS v5.0 Section 21 SE-003 and SE-004. // Links this file to security requirements.
 * SDD Traceability: Supports SDD v5.0 Section 10.1 Authentication. // Links this file to auth design.
 */ // Ends the documentation block.

const ACCESS_TOKEN_KEY = 'access_token'; // Stores the localStorage key used for the JWT access token.

const EXPIRES_AT_KEY = 'expires_at'; // Stores the localStorage key used for the token expiration timestamp.

export function saveAuthToken(token: string, expiresAt: string): void { // Saves the JWT token and expiration timestamp.
  localStorage.setItem(ACCESS_TOKEN_KEY, token); // Saves the JWT access token.
  localStorage.setItem(EXPIRES_AT_KEY, expiresAt); // Saves the token expiration timestamp.
} // Ends saveAuthToken.

export function getAuthToken(): string | null { // Reads the saved JWT token.
  return localStorage.getItem(ACCESS_TOKEN_KEY); // Returns the stored token or null.
} // Ends getAuthToken.

export function clearAuthToken(): void { // Removes authentication data.
  localStorage.removeItem(ACCESS_TOKEN_KEY); // Removes the JWT access token.
  localStorage.removeItem(EXPIRES_AT_KEY); // Removes the expiration timestamp.
} // Ends clearAuthToken.

export function isAuthenticated(): boolean { // Checks whether the user currently has a token.
  return getAuthToken() !== null; // Returns true when a token exists.
} // Ends isAuthenticated.
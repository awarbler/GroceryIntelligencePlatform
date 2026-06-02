import axios, { type AxiosError } from 'axios'; // Imports Axios and its typed error shape.
import type { StandardResponse, ApiErrorDetail } from '../types/base'; // Imports the shared API response types.
import type { LoginRequest, LoginResponse, CurrentUserResponse, LogoutResponse } from '../types/auth'; // Imports auth request and response types.

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'; // Reads the API base URL from Vite env or local backend.

const apiClient = axios.create({ // Creates one reusable Axios client.
  baseURL: `${API_BASE_URL}/api/v1`, // Adds the backend API prefix once.
  headers: { // Defines default request headers.
    'Content-Type': 'application/json', // Sends JSON by default.
  }, // Ends default headers.
}); // Ends Axios client setup.

apiClient.interceptors.request.use((config) => { // Adds logic before every request.
  const token = localStorage.getItem('access_token'); // Reads the stored JWT token.
  if (token !== null) { // Checks whether a token exists.
    config.headers.Authorization = `Bearer ${token}`; // Adds the bearer token header.
  } // Ends token check.
  return config; // Returns the updated request config.
}); // Ends request interceptor.

apiClient.interceptors.response.use( // Adds logic after every response.
  (response) => response, // Returns successful responses unchanged.
  (error: AxiosError<StandardResponse<null>>) => { // Handles typed API errors.
    if (error.response?.status === 401) { // Checks for unauthorized responses.
      localStorage.removeItem('access_token'); // Removes an invalid token.
      localStorage.removeItem('expires_at'); // Removes the stored expiration time.
    } // Ends unauthorized handling.
    return Promise.reject(error); // Passes the error to the calling code.
  }, // Ends error handler.
); // Ends response interceptor.

export function getApiErrors(error: unknown): ApiErrorDetail[] { // Converts unknown errors into displayable API errors.
  if (axios.isAxiosError<StandardResponse<null>>(error)) { // Checks whether the error came from Axios.
    return error.response?.data.errors ?? [{ message: 'Request failed.' }]; // Returns backend errors or fallback.
  } // Ends Axios error check.
  return [{ message: 'Unexpected error.' }]; // Returns fallback for non-Axios errors.
}

export async function loginUser(request: LoginRequest): Promise<LoginResponse> { // Logs in a user with typed request and response.
  const response = await apiClient.post<LoginResponse>('/auth/login', request); // Sends login request to backend.
  if (response.data.success && response.data.data !== null) { // Checks for successful token response.
    localStorage.setItem('access_token', response.data.data.access_token); // Stores JWT for later requests.
    localStorage.setItem('expires_at', response.data.data.expires_at); // Stores token expiration timestamp.
  } // Ends token storage.
  return response.data; // Returns the standard response body.
}

export async function getCurrentUser(): Promise<CurrentUserResponse> { // Gets the currently authenticated user.
  const response = await apiClient.get<CurrentUserResponse>('/auth/me'); // Sends current-user request.
  return response.data; // Returns the standard response body.
}

export async function logoutUser(): Promise<LogoutResponse> { // Logs out the current user.
  const response = await apiClient.post<LogoutResponse>('/auth/logout'); // Sends logout request.
  localStorage.removeItem('access_token'); // Removes the stored JWT token.
  localStorage.removeItem('expires_at'); // Removes the stored expiration timestamp.
  return response.data; // Returns the standard response body.
}
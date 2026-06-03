/** // Defines the file documentation block.
 * File: LoginPage.test.tsx // Identifies the login page test file.
 * Project: Grocery Intelligence Platform // Identifies the project.
 * Description: Tests login rendering, successful login redirect, failed login error, and authenticated-user redirect. // Explains the test purpose.
 * Author: Anita Woodford // Identifies the author.
 * SRS Traceability: Supports SRS v5.0 Section 20 TS-010 and Section 21 SE-003. // Links tests to requirements.
 * SDD Traceability: Supports SDD v5.0 Section 11 Testing Architecture and Section 10.1 Authentication. // Links tests to design.
 */ // Ends the documentation block.

import { render, screen, waitFor } from "@testing-library/react"; // Imports React Testing Library helpers.
import userEvent from "@testing-library/user-event"; // Imports realistic user interaction helpers.
import { MemoryRouter, Route, Routes } from "react-router-dom"; // Imports in-memory routing for component tests.
import { afterEach, describe, expect, it, vi } from "vitest"; // Imports Vitest test helpers.

import LoginPage from "../pages/LoginPage"; // Imports the login page component.
import * as api from "../services/api"; // Imports API service functions for mocking.
import { clearAuthToken, saveAuthToken } from "../services/authStorage"; // Imports token helpers.

function renderLoginPage(initialPath: string = "/login"): void { // Renders LoginPage inside a test router.
  render( // Starts rendering the test component tree.
    <MemoryRouter initialEntries={[initialPath]}> {/* Creates an isolated in-memory router. */}
      <Routes> {/* Defines test-only routes. */}
        <Route path="/login" element={<LoginPage />} /> {/* Mounts the login page at /login. */}
        <Route path="/upload" element={<div>Upload Page</div>} /> {/* Mounts a target page for redirect assertions. */}
      </Routes> {/* Ends test-only routes. */}
    </MemoryRouter>, // Ends the test router.
  ); // Ends render call.
} // Ends renderLoginPage.

afterEach(() => { // Runs cleanup after each test.
  vi.restoreAllMocks(); // Restores all mocked functions.
  clearAuthToken(); // Clears saved authentication data.
  localStorage.clear(); // Clears browser storage for test isolation.
}); // Ends cleanup hook.

describe("LoginPage", () => { // Groups LoginPage tests.
  it("renders the username and password form", () => { // Tests initial form rendering.
    renderLoginPage(); // Renders the login page.

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument(); // Verifies the username field is visible.
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument(); // Verifies the password field is visible.
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument(); // Verifies the submit button is visible.
  }); // Ends render test.

  it("redirects to upload after valid login", async () => { // Tests successful login redirect.
    const user = userEvent.setup(); // Creates a user-event controller.

    vi.spyOn(api, "loginUser").mockResolvedValue({ // Mocks a successful login response.
      success: true, // Marks the backend response as successful.
      data: { // Provides the expected token payload.
        access_token: "test-token", // Provides a fake JWT token.
        token_type: "bearer", // Provides the expected bearer token type.
        expires_at: "2099-12-31T23:59:59.000Z", // Provides a future expiration timestamp.
      }, // Ends token payload.
      errors: [], // Provides no API errors.
      meta: {}, // Provides an empty metadata object.
    }); // Ends successful login mock.

    renderLoginPage(); // Renders the login page.

    await user.type(screen.getByLabelText(/username/i), "anita"); // Types a username.
    await user.type(screen.getByLabelText(/password/i), "correct-password"); // Types a password.
    await user.click(screen.getByRole("button", { name: /sign in/i })); // Submits the form.

    await waitFor(() => expect(screen.getByText("Upload Page")).toBeInTheDocument()); // Verifies redirect target rendered.
  }); // Ends successful login test.

  it("shows an error after invalid login", async () => { // Tests failed login behavior.
    const user = userEvent.setup(); // Creates a user-event controller.

    vi.spyOn(api, "loginUser").mockRejectedValue(new Error("Invalid username or password.")); // Mocks failed login.

    renderLoginPage(); // Renders the login page.

    await user.type(screen.getByLabelText(/username/i), "anita"); // Types a username.
    await user.type(screen.getByLabelText(/password/i), "wrong-password"); // Types a password.
    await user.click(screen.getByRole("button", { name: /sign in/i })); // Submits the form.

    expect(await screen.findByText(/invalid username or password/i)).toBeInTheDocument(); // Verifies the safe error appears.
    expect(screen.queryByText("Upload Page")).not.toBeInTheDocument(); // Verifies the user did not redirect.
  }); // Ends invalid login test.

  it("redirects authenticated users away from login", async () => { // Tests already-authenticated redirect behavior.
    saveAuthToken("existing-token", "2099-12-31T23:59:59.000Z"); // Seeds localStorage with an existing token.

    renderLoginPage(); // Renders the login page.

    await waitFor(() => expect(screen.getByText("Upload Page")).toBeInTheDocument()); // Verifies authenticated users redirect.
  }); // Ends authenticated redirect test.
}); // Ends LoginPage test group.
/** // Defines the file documentation block.
 * File: LoginPage.tsx // Identifies the login page file.
 * Project: Grocery Intelligence Platform // Identifies the project.
 * Description: Renders the username/password login page and redirects after successful authentication. // Explains the page purpose.
 * Author: Anita Woodford // Identifies the author.
 * SRS Traceability: Supports SRS v5.0 Section 2 U-001, U-003 and Section 21 SE-001, SE-008. // Links this page to requirements.
 * SDD Traceability: Supports SDD v5.0 Section 2.1 Material UI and Section 10.1 Authentication. // Links this page to design.
 */ // Ends the documentation block.

import { Alert, Box, Button, Container, Paper, Stack, TextField, Typography } from "@mui/material"; // Imports Material UI layout and form components.
import { useEffect, useState, type FormEvent, type ReactElement } from "react"; // Imports React hooks and type-only React types.
import { useNavigate } from "react-router-dom"; // Imports navigation hook for redirects.
import { loginUser } from "../services/api"; // Imports the existing typed login API function.
import { isAuthenticated } from "../services/authStorage"; // Imports centralized authentication check.

export default function LoginPage(): ReactElement { // Defines the LoginPage component. // Defines the LoginPage component.
  const navigate = useNavigate(); // Creates the navigation function.
  const [username, setUsername] = useState<string>(""); // Stores the username field value.
  const [password, setPassword] = useState<string>(""); // Stores the password field value.
  const [errorMessage, setErrorMessage] = useState<string>(""); // Stores the safe login error message.
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false); // Stores whether the form is currently submitting.

  useEffect(() => { // Runs authentication redirect logic when the page loads.
    if (isAuthenticated()) { // Checks whether a token already exists.
      navigate("/upload", { replace: true }); // Redirects authenticated users away from /login.
    } // Ends authenticated-user redirect check.
  }, [navigate]); // Re-runs only if the navigate function reference changes.

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> { // Handles login form submission.
    event.preventDefault(); // Prevents the browser from refreshing the page.
    setErrorMessage(""); // Clears any previous login error.
    setIsSubmitting(true); // Marks the form as submitting.

    try { // Starts the protected login attempt block.
      await loginUser({ username, password }); // Sends credentials through the service layer.
      setPassword(""); // Clears the password from component state after successful login.
      navigate("/upload", { replace: true }); // Redirects to the upload page after login.
    } catch { // Handles failed login without exposing backend internals.
      setErrorMessage("Invalid username or password."); // Shows a clear safe error message.
    } finally { // Runs cleanup after success or failure.
      setIsSubmitting(false); // Marks the form as no longer submitting.
    } // Ends cleanup block.
  } // Ends handleSubmit.

  return ( // Returns the login page UI.
    <Container maxWidth="sm"> {/* Centers the login content and limits width. */}
      <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}> {/* Vertically centers the login card. */}
        <Paper elevation={3} sx={{ width: "100%", p: 4 }}> {/* Creates the card surface for the login form. */}
          <Stack component="form" spacing={3} onSubmit={handleSubmit}> {/* Creates a vertical form layout. */}
            <Box> {/* Groups the page title and subtitle. */}
              <Typography component="h1" variant="h4"> {/* Renders the main login heading. */}
                Grocery Intelligence Platform {/* Shows the application name. */}
              </Typography> {/* Ends the main login heading. */}
              <Typography color="text.secondary" sx={{ mt: 1 }}> {/* Renders the short instruction text. */}
                Sign in to continue. {/* Explains what the user should do. */}
              </Typography> {/* Ends the instruction text. */}
            </Box> {/* Ends the title group. */}

            {errorMessage.length > 0 ? ( /* Shows an error only when one exists. */
              <Alert severity="error">{errorMessage}</Alert> /* Displays a safe Material UI error message. */
            ) : null} {/* Renders nothing when no error exists. */}

            <TextField // Renders the username input.
              id="username" // Provides a stable id for accessibility and tests.
              label="Username" // Shows the username label.
              name="username" // Names the form field.
              value={username} // Binds the field to username state.
              onChange={(event) => setUsername(event.target.value)} // Updates username state when the user types.
              autoComplete="username" // Enables browser username autofill.
              required // Requires a username before submit.
              fullWidth // Makes the field fill the form width.
            /> {/* Ends the username input. */}

            <TextField // Renders the password input.
              id="password" // Provides a stable id for accessibility and tests.
              label="Password" // Shows the password label.
              name="password" // Names the form field.
              type="password" // Masks the password characters.
              value={password} // Binds the field to password state.
              onChange={(event) => setPassword(event.target.value)} // Updates password state when the user types.
              autoComplete="current-password" // Enables browser password manager support.
              required // Requires a password before submit.
              fullWidth // Makes the field fill the form width.
            /> {/* Ends the password input. */}

            <Button type="submit" variant="contained" disabled={isSubmitting} fullWidth> {/* Renders the submit button. */}
              {isSubmitting ? "Signing in..." : "Sign in"} {/* Shows progress text while submitting. */}
            </Button> {/* Ends the submit button. */}
          </Stack> {/* Ends the form stack. */}
        </Paper> {/* Ends the login card. */}
      </Box> {/* Ends the page centering wrapper. */}
    </Container> // Ends the responsive page container.
  ); // Ends the returned JSX.
} // Ends LoginPage.
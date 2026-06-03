import { Navigate, Route, Routes } from "react-router-dom"; // Imports React Router route components.

import LoginPage from "./pages/LoginPage"; // Imports the login page.

function App() { // Defines the root application component.
  return ( // Returns the application route tree.
    <Routes> {/* Defines all frontend routes. */}
      <Route path="/login" element={<LoginPage />} /> {/* Registers the login page route. */}
      <Route path="/upload" element={<div>Upload Page</div>} /> {/* Adds a temporary upload placeholder until P1-22. */}
      <Route path="/" element={<Navigate to="/login" replace />} /> {/* Redirects root traffic to login. */}
    </Routes> // Ends the route tree.
  ); // Ends the return statement.
} // Ends the App component.

export default App; // Exports the App component.
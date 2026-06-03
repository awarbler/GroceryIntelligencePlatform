import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter } from "react-router-dom"; // Imports the router provider.


import "./index.css"; // Imports global styles.

createRoot(document.getElementById("root")!).render( // Creates and renders the React app root.
  <StrictMode> {/* Enables extra development checks. */}
    <BrowserRouter> {/* Enables browser URL routing for Routes and Navigate. */}
      <App /> {/* Renders the root app component. */}
    </BrowserRouter> {/* Ends the browser router provider. */}
  </StrictMode>, // Ends strict mode.
); // Ends root render.
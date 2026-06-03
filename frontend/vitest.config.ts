import { defineConfig } from "vitest/config"; // Imports the Vitest config helper.

import react from "@vitejs/plugin-react"; // Imports the React plugin.

export default defineConfig({ // Exports the Vitest configuration.
  plugins: [react()], // Enables React support in tests.
  test: { // Defines Vitest test settings.
    environment: "jsdom", // Gives tests a browser-like DOM.
    setupFiles: "./src/tests/setup.ts", // Loads shared test setup before tests run.
    globals: true, // Enables global Vitest test APIs for jest-dom setup.
  }, // Ends test settings.
}); // Ends config.
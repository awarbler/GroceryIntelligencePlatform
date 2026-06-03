import "@testing-library/jest-dom"; // Adds DOM matchers.

const localStorageMock = { // Creates a fake browser localStorage.
  store: {} as Record<string, string>, // Stores key/value pairs.

  getItem(key: string): string | null { // Reads a value.
    return this.store[key] ?? null; // Returns value or null.
  },

  setItem(key: string, value: string): void { // Saves a value.
    this.store[key] = value; // Stores value.
  },

  removeItem(key: string): void { // Removes a value.
    delete this.store[key]; // Deletes value.
  },

  clear(): void { // Clears storage.
    this.store = {}; // Resets storage.
  },
};

Object.defineProperty(globalThis, "localStorage", { // Adds localStorage to the test environment.
  value: localStorageMock,
  writable: true,
});
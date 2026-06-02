import { describe, expect, it } from 'vitest'; // Imports Vitest test helpers.
import { getApiErrors } from '../services/api'; // Imports API error helper from service layer.

describe('api service layer', () => { // Groups API service layer tests.
  it('converts unknown errors into a safe frontend error message', () => { // Tests fallback error behavior.
    const result = getApiErrors(new Error('boom')); // Calls helper with non-Axios error.
    expect(result).toEqual([{ message: 'Unexpected error.' }]); // Verifies safe fallback output.
  }); // Ends fallback error test.
}); // Ends API service layer test group.
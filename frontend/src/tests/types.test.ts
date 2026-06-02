import { describe, expect, it } from 'vitest'; // Imports Vitest test helpers.
import type { LoginResponse } from '../types/auth'; // Imports login response type.
import type { PurchaseModel } from '../types/purchase'; // Imports purchase model type.

describe('frontend TypeScript types', () => { // Groups type smoke tests.
  it('supports the standard login response shape', () => { // Tests login response structure.
    const response: LoginResponse = { // Creates a typed login response.
      success: true, // Sets success flag.
      data: { // Sets token payload.
        access_token: 'test-token', // Sets test token value.
        token_type: 'bearer', // Sets expected token type.
        expires_at: '2026-06-02T12:00:00Z', // Sets test expiration timestamp.
      }, // Ends token payload.
      errors: [], // Sets empty error list.
    }; // Ends typed login response.

    expect(response.data?.access_token).toBe('test-token'); // Verifies typed token access.
  }); // Ends login response type test.

  it('supports Decimal-safe purchase money fields as strings', () => { // Tests purchase money field typing.
    const purchase: PurchaseModel = { // Creates a typed purchase model.
      id: '507f1f77bcf86cd799439011', // Sets test ObjectId.
      store_ref: 'heb', // Sets Phase 1 store key.
      canonical_name: 'Milk', // Sets normalized item name.
      category: 'Food and Grocery', // Sets product category.
      quantity: 1, // Sets quantity.
      purchase_date: '2026-06-02', // Sets purchase date.
      shelf_price: '4.99', // Sets shelf price as string.
      register_price: '3.99', // Sets register price as string.
      out_of_pocket: '3.99', // Sets out-of-pocket as string.
    }; // Ends typed purchase model.

    expect(purchase.out_of_pocket).toBe('3.99'); // Verifies Decimal-safe string value.
  }); // Ends purchase type test.
}); // Ends type test group.
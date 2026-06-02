/** 
 * File: frontend/src/types/base.ts
 * Description: This file contains the base types used across the frontend application.
 * Author: Anita Woodford
 * Created: 2024-06-01
 * License: MIT
 * Copyright (c) 2024 Anita Woodford. All rights reserved.
 * SRS Document: 
 * SDD Document: 
 * Revision History:
 */

// frontend/src/types/base.ts

export type ObjectId = string; // Represents MongoDB ObjectId values after JSON serialization.

export interface ApiErrorDetail { // Defines one normalized backend error item.
  field?: string; // Stores the optional field name that caused the error.
  message: string; // Stores the human-readable error message.
  code?: string; // Stores the optional machine-readable error code.
}

export interface ApiMeta { // Defines optional pagination or response metadata.
  count?: number; // Stores the number of records returned.
  page?: number; // Stores the current page number.
  limit?: number; // Stores the page size.
  total?: number; // Stores the total available record count.
}

export interface StandardResponse<T> { // Defines the generic API response wrapper.
  success: boolean; // Stores whether the backend request succeeded.
  data: T | null; // Stores typed response data or null on failure.
  errors: ApiErrorDetail[]; // Stores normalized backend error details.
  meta?: ApiMeta; // Stores optional metadata such as count or page.
}

export interface BaseDocument { // Defines fields shared by MongoDB-backed documents.
  id: ObjectId; // Stores the serialized MongoDB ObjectId.
  created_at?: string; // Stores the optional ISO created timestamp.
  updated_at?: string; // Stores the optional ISO updated timestamp.
}
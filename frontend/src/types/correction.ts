/** 
 * File: 
 * Description: T
 * Author: Anita Woodford
 * Created: 2024-06-01
 * License: MIT
 * Copyright (c) 2024 Anita Woodford. All rights reserved.
 * SRS Document: 
 * SDD Document: 
 * Revision History:
 */

import type { ObjectId, StandardResponse } from './base'; // Imports shared frontend types.

export interface CorrectionItem { // Defines one item in a correction session.
  item_id: string; // Stores temporary correction item id.
  raw_name: string; // Stores original parsed/raw item name.
  parsed_name: string; // Stores parser-produced item name.
  normalized_name: string; // Stores normalized product name.
  product_ref?: ObjectId | null; // Stores product reference when matched.
  quantity: string; // Stores quantity as Decimal-safe string.
  quantity_unit?: string | null; // Stores quantity unit when available.
  unit_price?: string | null; // Stores unit price as Decimal-safe string when available.
  line_total: string; // Stores line total as Decimal-safe string.
  purchase_date?: string | null; // Stores purchase date when available.
  parser_version?: string | null; // Stores parser version.
  normalizer_version?: string | null; // Stores normalizer version.
  confidence: number; // Stores match confidence.
  matched_rule_type?: string | null; // Stores how the item was matched.
  substituted?: boolean; // Stores whether item was substituted.
  out_of_stock?: boolean; // Stores whether item was out of stock.
  user_corrected?: boolean; // Stores whether user corrected item.
  skipped?: boolean; // Stores whether user skipped item.
  review_required: boolean; // Stores whether review is required.
  review_suggested: boolean; // Stores whether review is suggested.
  auto_accepted: boolean; // Stores whether item was auto accepted.
}

export interface CorrectionSession { // Defines a correction session.
  session_id: string; // Stores temporary session id.
  source_type: string; // Stores upload or paste source type.
  store: string; // Stores store key.
  raw_lines: string[]; // Stores raw extracted lines.
  items: CorrectionItem[]; // Stores parsed and normalized items.
  parse_errors: string[]; // Stores parser error messages.
  source_metadata: Record<string, unknown>; // Stores safe metadata without using any.
  created_at: string; // Stores session creation timestamp.
  expires_at: string; // Stores session expiration timestamp.
  approved: boolean; // Stores approval status.
}

export interface PasteReceiptRequest { // Defines request body for pasted receipt text.
  text: string; // Sends pasted receipt text.
}

export interface UploadReceiptResponseData { // Defines response after uploading a receipt.
  session_id: string; // Stores created correction session id.
  expires_at: string; // Stores session expiration timestamp.
}

export interface CorrectionItemUpdateRequest { // Defines editable correction item fields.
  raw_name?: string; // Updates raw item name.
  parsed_name?: string; // Updates parsed item name.
  normalized_name?: string; // Updates normalized item name.
  product_ref?: ObjectId | null; // Updates product reference.
  quantity?: string; // Updates quantity.
  quantity_unit?: string | null; // Updates quantity unit.
  unit_price?: string | null; // Updates unit price.
  line_total?: string; // Updates line total.
  skipped?: boolean; // Updates skipped flag.
}

export interface NormalizeCorrectionRequest { // Defines request body for saving a normalization correction.
  canonical_name: string; // Sends canonical product name.
  alias: string; // Sends raw alias to associate with canonical name.
}

export interface ApproveCorrectionSessionRequest { // Defines request body for approving a session.
  session_id: string; // Sends correction session id.
}

export type UploadReceiptResponse = StandardResponse<UploadReceiptResponseData>; // Defines upload response wrapper.
export type PasteReceiptResponse = StandardResponse<UploadReceiptResponseData>; // Defines paste response wrapper.
export type CorrectionSessionResponse = StandardResponse<CorrectionSession>; // Defines correction-session response wrapper.
import type { BaseDocument, ObjectId, StandardResponse } from './base'; // Imports shared document, ObjectId, and API response types.

export type InputType = // Defines allowed purchase input source values.
  | 'ONLINE_RECEIPT' // Represents an online receipt input.
  | 'EMAIL_RECEIPT' // Represents an email receipt input.
  | 'PDF' // Represents a PDF input.
  | 'PHOTO' // Represents a photo input.
  | 'CSV_IMPORT' // Represents a CSV import input.
  | 'MANUAL_ENTRY' // Represents manual user entry.
  | 'COPY_PASTE'; // Represents pasted text input.

export type CouponSource = // Defines allowed coupon source values.
  | 'WALGREENS_DIGITAL' // Represents a Walgreens digital coupon.
  | 'CVS_DIGITAL' // Represents a CVS digital coupon.
  | 'HEB_DIGITAL' // Represents an H-E-B digital coupon.
  | 'WALMART_DIGITAL' // Represents a Walmart digital coupon.
  | 'MANUFACTURER' // Represents a manufacturer coupon.
  | 'PAPER'; // Represents a paper coupon.

export interface RewardUsed { // Defines a reward amount used at checkout.
  used: boolean; // Stores whether the reward was used.
  amount: string; // Stores the reward amount as a Decimal-safe string.
}

export interface PurchaseModel extends BaseDocument { // Defines one saved purchase record.
  product_ref?: ObjectId | null; // Stores the linked product id when available.
  store_ref: ObjectId | string; // Stores the linked store id or Phase 1 store key.
  canonical_name: string; // Stores the normalized item name.
  raw_name?: string | null; // Stores the original parsed item name when available.
  category: string; // Stores the item category.
  brand?: string | null; // Stores the item brand when available.
  size?: string | null; // Stores the item size when available.
  quantity: number; // Stores the purchased quantity.
  purchase_date: string; // Stores the purchase date as YYYY-MM-DD.
  shelf_price: string; // Stores the regular shelf price as a Decimal-safe string.
  sale_price?: string | null; // Stores the sale price as a Decimal-safe string when available.
  register_price: string; // Stores the register price before rebates as a Decimal-safe string.
  subtotal_before_coupons?: string | null; // Stores basket subtotal before coupons when available.
  out_of_pocket: string; // Stores actual checkout cost as a Decimal-safe string.
  coupon_used?: boolean; // Stores whether a coupon was used.
  coupon_source?: CouponSource | null; // Stores the coupon source when applicable.
  input_type?: InputType | null; // Stores how the purchase entered the system.
  raw_input_ref?: ObjectId | null; // Stores the raw input archive reference.
  parser_version?: string | null; // Stores parser version for traceability.
  parse_confidence?: number | null; // Stores parse confidence when available.
  user_corrected?: boolean; // Stores whether the user corrected this purchase.
  notes?: string | null; // Stores optional user notes.
}

export interface CreatePurchaseRequest { // Defines request body for creating a purchase.
  store_ref: ObjectId | string; // Sends the store id or Phase 1 store key.
  canonical_name: string; // Sends the normalized item name.
  category: string; // Sends the product category.
  quantity: number; // Sends the purchase quantity.
  purchase_date: string; // Sends the purchase date as YYYY-MM-DD.
  shelf_price: string; // Sends shelf price as a Decimal-safe string.
  register_price: string; // Sends register price as a Decimal-safe string.
  out_of_pocket: string; // Sends out-of-pocket amount as a Decimal-safe string.
  sale_price?: string | null; // Sends sale price when available.
  brand?: string | null; // Sends brand when available.
  size?: string | null; // Sends size when available.
  coupon_used?: boolean; // Sends whether a coupon was used.
  coupon_source?: CouponSource | null; // Sends coupon source when available.
  notes?: string | null; // Sends optional notes.
}

export interface UpdatePurchaseRequest { // Defines request body for editing a purchase.
  canonical_name?: string; // Updates normalized item name.
  category?: string; // Updates category.
  quantity?: number; // Updates quantity.
  purchase_date?: string; // Updates purchase date.
  shelf_price?: string; // Updates shelf price.
  sale_price?: string | null; // Updates sale price.
  register_price?: string; // Updates register price.
  out_of_pocket?: string; // Updates out-of-pocket amount.
  brand?: string | null; // Updates brand.
  size?: string | null; // Updates size.
  coupon_used?: boolean; // Updates coupon-used flag.
  coupon_source?: CouponSource | null; // Updates coupon source.
  notes?: string | null; // Updates notes.
}

export type PurchaseResponse = StandardResponse<PurchaseModel>; // Defines one-purchase API response.
export type PurchaseListResponse = StandardResponse<PurchaseModel[]>; // Defines purchase-list API response.
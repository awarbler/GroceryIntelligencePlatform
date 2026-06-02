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

import type { BaseDocument, ObjectId } from './base'; // Imports shared frontend types.

export type CouponType = // Defines allowed coupon type values.
  | 'STORE_DIGITAL' // Represents a store digital coupon.
  | 'MANUFACTURER' // Represents a manufacturer coupon.
  | 'PAPER' // Represents a paper coupon.
  | 'MYW_EXCLUSIVE' // Represents a myWalgreens exclusive coupon or offer.
  | 'APP_ONLY'; // Represents an app-only coupon.

export type CouponScope = // Defines what the coupon applies to.
  | 'ITEM' // Applies to one item.
  | 'BASKET' // Applies to a basket threshold.
  | 'COMBO' // Applies to a combo deal.
  | 'REBATE'; // Represents rebate-style coupon input.

export interface Coupon extends BaseDocument { // Defines one coupon returned by the backend.
  store_ref: ObjectId; // Stores the related store id.
  item_name: string; // Stores the coupon item name.
  brand?: string; // Stores the optional brand.
  discount_amount: number; // Stores the coupon discount amount.
  discount_type: string; // Stores the discount type.
  min_qty: number; // Stores the minimum quantity required.
  description: string; // Stores the coupon description.
  expiration_date: string; // Stores the coupon expiration date.
  coupon_type: string; // Stores the coupon type.
  raw_text?: string; // Stores optional raw source text.
}

export interface CreateCouponRequest { // Defines the create coupon request body.
  store_ref: ObjectId; // Stores the related store id.
  item_name: string; // Stores the coupon item name.
  brand?: string; // Stores the optional brand.
  discount_amount: number; // Stores the coupon discount amount.
  discount_type: string; // Stores the discount type.
  min_qty: number; // Stores the minimum quantity required.
  description: string; // Stores the coupon description.
  expiration_date: string; // Stores the coupon expiration date.
  coupon_type: string; // Stores the coupon type.
  raw_text?: string; // Stores optional raw source text.
}


export interface UpdateCouponRequest { // Defines request body for editing a coupon.
  coupon_type?: CouponType; // Updates coupon type.
  coupon_scope?: CouponScope; // Updates coupon scope.
  is_store_coupon?: boolean; // Updates store-coupon flag.
  is_manufacturer_coupon?: boolean; // Updates manufacturer-coupon flag.
  item_name?: string; // Updates item name.
  expiration_date?: string; // Updates expiration date.
  store_name?: string | null; // Updates store name.
  coupon_date?: string | null; // Updates coupon date.
  item_size?: string | null; // Updates item size.
  brand?: string | null; // Updates brand.
  discount_amount?: string | null; // Updates dollar discount.
  discount_percent?: string | null; // Updates percent discount.
  terms?: string | null; // Updates terms.
}

export type CouponListResponse = Coupon[]; // Defines the coupon list response data.

export type CouponResponse = Coupon; // Defines a single coupon response data type
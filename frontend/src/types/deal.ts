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

import type { BaseDocument, ObjectId, StandardResponse } from './base'; // Imports shared frontend types.

export type DealType = // Defines supported deal classifications.
  | 'STANDARD' // Represents a standard sale deal.
  | 'BOGO' // Represents buy-one-get-one.
  | 'BUY_X_GET_Y' // Represents buy X get Y.
  | 'THRESHOLD' // Represents spend or quantity threshold deal.
  | 'REGISTER_REWARD' // Represents Walgreens Register Reward deal.
  | 'ECB' // Represents CVS ExtraBucks deal.
  | 'SPEND_BOOSTER' // Represents a spend booster deal.
  | 'MANUFACTURER_COUPON' // Represents manufacturer coupon deal.
  | 'COMBO_LOCO' // Represents H-E-B Combo Loco.
  | 'BASKET_COUPON' // Represents basket-level coupon.
  | 'PERCENT_OFF'; // Represents percent-off deal.

export interface DealItem { // Defines one item inside an ad or deal.
  item_name: string; // Stores deal item name.
  brand?: string | null; // Stores brand when available.
  size?: string | null; // Stores size when available.
  sale_price?: string | null; // Stores sale price as Decimal-safe string.
  regular_price?: string | null; // Stores regular price as Decimal-safe string.
  buy_qty?: number | null; // Stores required buy quantity.
  deal_type: DealType; // Stores deal type.
  store_coupon_amount?: string | null; // Stores store coupon amount.
  store_coupon_desc?: string | null; // Stores store coupon description.
  manufacturer_coupon_amount?: string | null; // Stores manufacturer coupon amount.
  manufacturer_coupon_desc?: string | null; // Stores manufacturer coupon description.
  register_reward?: string | null; // Stores Register Reward amount.
  raw_text?: string | null; // Stores original deal text when available.
}

export interface AdModel extends BaseDocument { // Defines one weekly ad record.
  store_ref: ObjectId | string; // Stores linked store id or Phase 1 store key.
  start_date: string; // Stores ad start date as YYYY-MM-DD.
  end_date: string; // Stores ad end date as YYYY-MM-DD.
  source_type?: string | null; // Stores source type when available.
  raw_input_ref?: ObjectId | null; // Stores raw input reference when available.
  items: DealItem[]; // Stores deal items in the ad.
}

export interface DealMatchItem { // Defines one matched deal report item.
  product_ref?: ObjectId | null; // Stores matched product reference when available.
  store_ref: ObjectId | string; // Stores matched store reference.
  deal_ref?: ObjectId | null; // Stores matched deal reference when available.
  coupon_refs?: ObjectId[]; // Stores related coupon references.
  rebate_refs?: ObjectId[]; // Stores related rebate references.
  shelf_price: string; // Stores shelf price as Decimal-safe string.
  register_price: string; // Stores register price as Decimal-safe string.
  oop: string; // Stores out-of-pocket value as Decimal-safe string.
  rr_earned?: string | null; // Stores Register Rewards earned separately.
  ecb_earned?: string | null; // Stores ExtraBucks earned separately.
  reward_value?: string | null; // Stores non-register reward value separately.
  total_rebates_back?: string | null; // Stores total rebate value separately.
  deal_type: DealType; // Stores matched deal type.
  is_money_maker: boolean; // Stores whether deal is a money maker.
  matched_as_substitute: boolean; // Stores whether matched as substitute.
}

export interface DealMatchModel extends BaseDocument { // Defines a generated weekly deal match document.
  week_of: string; // Stores week start date as YYYY-MM-DD.
  generated_at: string; // Stores generation timestamp.
  matches: DealMatchItem[]; // Stores matched deal items.
}

export interface CreateAdRequest { // Defines request body for manual ad entry.
  store_ref: ObjectId | string; // Sends store id or Phase 1 store key.
  start_date: string; // Sends ad start date.
  end_date: string; // Sends ad end date.
  source_type?: string | null; // Sends source type when available.
  items: DealItem[]; // Sends ad deal items.
}

export type AdResponse = StandardResponse<AdModel>; // Defines one-ad API response.
export type AdListResponse = StandardResponse<AdModel[]>; // Defines ad-list API response.
export type DealMatchResponse = StandardResponse<DealMatchModel>; // Defines deal-match API response.
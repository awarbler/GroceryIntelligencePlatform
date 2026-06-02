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

import type { StandardResponse } from './base'; // Imports shared API response type.
import type { DealMatchItem } from './deal'; // Imports matched deal item type.

export interface ReportStoreGroup { // Defines one store section in the report.
  store_name: string; // Stores readable store name.
  store_ref: string; // Stores store reference or store key.
  items: DealMatchItem[]; // Stores matched report items for the store.
  subtotal_register_price: string; // Stores register subtotal as Decimal-safe string.
  subtotal_out_of_pocket: string; // Stores out-of-pocket subtotal as Decimal-safe string.
  subtotal_rewards: string; // Stores rewards subtotal separately.
  subtotal_rebates: string; // Stores rebates subtotal separately.
}

export interface WeeklyReportSummary { // Defines report-level financial summary.
  week_of: string; // Stores week start date as YYYY-MM-DD.
  generated_at: string; // Stores report generation timestamp.
  total_register_price: string; // Stores total register price.
  total_out_of_pocket: string; // Stores total out-of-pocket cost.
  total_rewards: string; // Stores total rewards separately.
  total_rebates: string; // Stores total rebates separately.
  total_items: number; // Stores number of report items.
  money_maker_count: number; // Stores number of money-maker deals.
}

export interface WeeklyReport { // Defines full weekly deal report data.
  summary: WeeklyReportSummary; // Stores report summary.
  stores: ReportStoreGroup[]; // Stores report grouped by store.
}

export interface GenerateReportRequest { // Defines query data needed for report generation.
  week_of: string; // Sends week start date as YYYY-MM-DD.
}

export type WeeklyReportResponse = StandardResponse<WeeklyReport>; // Defines report API response.
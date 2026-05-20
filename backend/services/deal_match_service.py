# =============================================================================  # File header separator
# File: backend/services/deal_match_service.py  # Identifies the file path
# Project: Grocery Intelligence Platform  # Identifies the project
# Purpose: Generates saved deal matches from My Items, ads, coupons, and rewards.  # Explains service purpose
# SRS Traceability: Section 16, Section 17, Section 18, Section 23  # Links service to SRS sections
# SDD Traceability: Section 7.10, Section 9, Section 15  # Links service to SDD sections
# =============================================================================  # File header separator

from datetime import date  # Imports date for week_of
from decimal import Decimal  # Imports Decimal for financial calculations
from typing import Any  # Imports Any for Mongo document dictionaries

from backend.models.deal_match import DealMatchType  # Imports controlled deal match type enum
from backend.parsers.deal_matcher import (  # Imports pure helper functions
    calculate_financials,  # Imports financial calculator
    coupon_matches_product,  # Imports coupon matcher
    get_object_id,  # Imports ObjectId helper
    product_matches_deal,  # Imports ad/deal matcher
    reward_matches_product,  # Imports reward matcher
)


async def generate_deal_matches(  # Defines main matching service
    products_dal: Any,  # Receives products DAL
    ads_dal: Any,  # Receives ads DAL
    coupons_dal: Any,  # Receives coupons DAL
    reward_offers_dal: Any,  # Receives reward offers DAL
    deal_matches_dal: Any,  # Receives deal matches DAL
    week_of: date,  # Receives report week
) -> list[Any]:  # Returns inserted match ids
    products = await products_dal.find_my_items()  # Loads products marked as My Items
    ads = await ads_dal.list_active_heb_ads()  # Loads active H-E-B ads
    coupons = await coupons_dal.list_active_heb_coupons()  # Loads active H-E-B coupons
    reward_offers = await reward_offers_dal.list_active_offers(retailer="HEB")  # Loads active H-E-B reward offers

    generated_matches: list[dict[str, Any]] = []  # Creates container for generated match documents

    for product in products:  # Loops through My Items
        for ad in ads:  # Loops through active ads
            matched, matched_as_substitute = product_matches_deal(product, ad)  # Checks direct/substitute match

            if not matched:  # Skips unmatched ads
                continue  # Moves to next ad

            attached_coupons = [coupon for coupon in coupons if coupon_matches_product(product, coupon)]  # Finds matching coupons
            attached_rewards = [reward for reward in reward_offers if reward_matches_product(product, reward)]  # Finds matching rewards

            register_price = ad.get("sale_price") or ad.get("register_price") or product.get("avg_price") or Decimal("0.00")  # Chooses register price
            shelf_price = product.get("avg_price") or ad.get("shelf_price") or register_price  # Chooses shelf price

            register_coupon_total = sum(  # Starts coupon sum
                Decimal(str(coupon.get("discount_amount") or coupon.get("value") or "0.00"))  # Converts coupon amount
                for coupon in attached_coupons  # Iterates attached coupons
            )  # Ends coupon sum

            total_rewards_value = sum(  # Starts reward sum
                Decimal(str(reward.get("estimated_cash_value") or "0.00"))  # Converts estimated reward cash value
                for reward in attached_rewards  # Iterates attached rewards
            )  # Ends reward sum

            financials = calculate_financials(  # Calculates OOP and reward-separated fields
                register_price=register_price,  # Passes register price
                coupon_total=register_coupon_total,  # Passes register coupon total
                reward_total=total_rewards_value,  # Passes reward value
            )  # Ends financial calculation

            match_type = determine_deal_match_type(  # Determines match type
                has_ad=True,  # This branch has an ad
                has_coupon=bool(attached_coupons),  # Checks coupons
                has_reward=bool(attached_rewards),  # Checks rewards
            )  # Ends match type calculation

            generated_matches.append(  # Adds saved match document
                {  # Starts document
                    "product_ref": get_object_id(product),  # Stores product id
                    "store_ref": ad.get("store_ref") or product.get("store_ref"),  # Stores store id
                    "deal_ref": get_object_id(ad),  # Stores ad id
                    "coupon_refs": [get_object_id(coupon) for coupon in attached_coupons],  # Stores coupon ids
                    "reward_offer_refs": [get_object_id(reward) for reward in attached_rewards],  # Stores reward ids
                    "shelf_price": shelf_price,  # Stores shelf price
                    "register_price": register_price,  # Stores register price
                    "subtotal_before_coupons": register_price,  # Stores subtotal before coupons
                    "register_coupon_total": register_coupon_total,  # Stores register coupon total
                    "out_of_pocket": financials["out_of_pocket"],  # Stores OOP
                    "total_rewards_value": financials["total_rewards_value"],  # Stores rewards
                    "final_after_rewards": financials["final_after_rewards"],  # Stores net after rewards
                    "deal_type": match_type.value,  # Stores match type value
                    "is_money_maker": financials["is_money_maker"],  # Stores money maker flag
                    "matched_as_substitute": matched_as_substitute,  # Stores substitute flag
                    "week_of": week_of.isoformat(),  # Stores week date as ISO string
                }  # Ends document
            )  # Ends append

    await deal_matches_dal.delete_by_week(week_of=week_of)  # Removes previous generated matches for same week
    return await deal_matches_dal.insert_many_matches(generated_matches)  # Saves and returns inserted ids


def determine_deal_match_type(has_ad: bool, has_coupon: bool, has_reward: bool) -> DealMatchType:  # Determines match category
    if has_ad and (has_coupon or has_reward):  # Checks stacked opportunity
        return DealMatchType.STACKED  # Returns stacked type

    if has_ad:  # Checks ad-only opportunity
        return DealMatchType.AD  # Returns ad type

    if has_coupon:  # Checks coupon-only opportunity
        return DealMatchType.COUPON  # Returns coupon type

    return DealMatchType.REWARD  # Returns reward type
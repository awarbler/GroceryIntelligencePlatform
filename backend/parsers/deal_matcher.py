# =============================================================================  # File header separator
# File: backend/parsers/deal_matcher.py  # Identifies the file path
# Project: Grocery Intelligence Platform  # Identifies the project
# Purpose: Contains pure matching and financial calculation helpers.  # Explains the file purpose
# SRS Traceability: Section 16, Section 17, Section 18, Section 23  # Links parser to SRS sections
# SDD Traceability: Section 7.10, Section 9, Section 15  # Links parser to SDD sections
# =============================================================================  # File header separator

from decimal import Decimal  # Imports Decimal for currency-safe arithmetic
from typing import Any  # Imports Any for generic dictionaries


def normalize_text(value: str | None) -> str:  # Normalizes product and deal text for matching
    return (value or "").strip().lower()  # Converts None-safe text to lowercase trimmed text


def get_object_id(document: dict[str, Any]) -> Any:  # Reads Mongo id from possible field names
    return document.get("_id") or document.get("id")  # Returns Mongo _id or Pydantic id


def product_matches_deal(product: dict[str, Any], deal: dict[str, Any]) -> tuple[bool, bool]:  # Checks direct and substitute match
    product_name = normalize_text(product.get("canonical_name") or product.get("item_name"))  # Reads product name
    deal_name = normalize_text(deal.get("canonical_name") or deal.get("item_name") or deal.get("title"))  # Reads deal name

    if product_name and deal_name and product_name == deal_name:  # Checks direct canonical match
        return True, False  # Returns matched and not substitute

    substitutes = product.get("acceptable_substitutes") or []  # Reads acceptable substitute list

    for substitute in substitutes:  # Loops through substitutes
        if normalize_text(substitute) == deal_name:  # Checks substitute equality
            return True, True  # Returns matched and substitute

    return False, False  # Returns no match


def coupon_matches_product(product: dict[str, Any], coupon: dict[str, Any]) -> bool:  # Checks whether coupon applies
    product_name = normalize_text(product.get("canonical_name") or product.get("item_name"))  # Reads product name
    coupon_name = normalize_text(coupon.get("canonical_name") or coupon.get("item_name") or coupon.get("title"))  # Reads coupon name
    coupon_scope = normalize_text(coupon.get("coupon_scope"))  # Reads coupon scope

    if coupon_scope == "basket":  # Allows basket coupon attachment
        return True  # Basket coupon can apply to the opportunity

    return bool(product_name and coupon_name and product_name == coupon_name)  # Returns direct coupon match result


def reward_matches_product(product: dict[str, Any], reward: dict[str, Any]) -> bool:  # Checks whether reward applies
    product_name = normalize_text(product.get("canonical_name") or product.get("item_name"))  # Reads product name
    qualifying_products = reward.get("qualifying_products") or []  # Reads reward qualifying product names

    for qualifying_product in qualifying_products:  # Loops through qualifying products
        if product_name == normalize_text(qualifying_product):  # Checks exact reward product match
            return True  # Returns matched reward

    qualifying_categories = reward.get("qualifying_categories") or []  # Reads reward qualifying categories
    product_category = normalize_text(product.get("category"))  # Reads product category

    for qualifying_category in qualifying_categories:  # Loops through qualifying categories
        if product_category == normalize_text(qualifying_category):  # Checks category match
            return True  # Returns matched reward

    return False  # Returns no reward match


def decimal_value(value: Any) -> Decimal:  # Converts values to Decimal safely
    if value is None:  # Checks missing value
        return Decimal("0.00")  # Returns zero for missing value

    return Decimal(str(value))  # Converts value through string to avoid float artifacts


def calculate_financials(register_price: Any, coupon_total: Any, reward_total: Any) -> dict[str, Decimal | bool]:  # Calculates financial fields
    register_price_decimal = decimal_value(register_price)  # Converts register price to Decimal
    coupon_total_decimal = decimal_value(coupon_total)  # Converts coupon total to Decimal
    reward_total_decimal = decimal_value(reward_total)  # Converts reward total to Decimal

    out_of_pocket = register_price_decimal - coupon_total_decimal  # Calculates register payment after coupons
    final_after_rewards = out_of_pocket - reward_total_decimal  # Calculates net cost after rewards
    is_money_maker = reward_total_decimal > out_of_pocket  # Flags money maker when rewards exceed OOP

    return {  # Returns calculated values
        "out_of_pocket": out_of_pocket,  # Stores OOP value
        "total_rewards_value": reward_total_decimal,  # Stores reward value
        "final_after_rewards": final_after_rewards,  # Stores net after rewards
        "is_money_maker": is_money_maker,  # Stores money maker flag
    }  # Ends result dictionary
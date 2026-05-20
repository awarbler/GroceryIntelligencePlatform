# =============================================================================
# File: backend/services/report_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Builds weekly report JSON from saved deal_matches records.
# Security Note: Reads persisted deal matches only; no matching logic or direct MongoDB.
# SRS Traceability: SRS Section 16 DR-001 through DR-021; SRS Section 20 TS-005; SRS Section 23.
# SDD Traceability: SDD Section 7.10; SDD Section 8; SDD Section 9; SDD Section 15.
# =============================================================================

from __future__ import annotations  # Enables modern type-hint behavior.

from collections import defaultdict  # Supports grouped store/category buckets.
from datetime import UTC, date, datetime  # Supports report dates and UTC timestamps.
from decimal import Decimal, InvalidOperation  # Supports safe money calculations.
from typing import Any  # Supports MongoDB document dictionaries.

from backend.data_access.deal_matches import DealMatchesDataAccess  # Uses the approved DAL boundary.


class ReportService:  # Defines the report business service.
    """Builds report JSON from saved deal_matches only."""  # Documents the service purpose.

    def __init__(self, deal_matches_access: DealMatchesDataAccess) -> None:  # Injects DAL dependency.
        self._deal_matches_access = deal_matches_access  # Stores the DAL dependency.

    async def generate_weekly_report(  # Generates one weekly report.
        self,  # Receives the service instance.
        week_of: date,  # Receives the requested report week.
        store_ref: str | None = None,  # Receives an optional store filter.
    ) -> dict[str, Any]:  # Returns JSON-ready report data.
        matches = await self._deal_matches_access.list_by_week_and_store(  # Reads saved matches only.
            week_of=week_of,  # Passes the week filter.
            store_ref=store_ref,  # Passes the optional store filter.
        )  # Ends DAL call.

        summary = _calculate_summary(matches)  # Calculates weekly display totals.
        grouped_stores = _group_by_store(matches)  # Groups matches by store.
        stores = [_build_store_report(store_ref=key, matches=value) for key, value in grouped_stores.items()]  # Builds store sections.

        return {  # Starts final report payload.
            "week_of": week_of.isoformat(),  # Stores requested week.
            "generated_at": datetime.now(UTC).isoformat(),  # Stores UTC generation time.
            "summary": summary,  # Stores weekly totals.
            "stores": stores,  # Stores grouped store reports.
            "match_count": len(matches),  # Stores total matched opportunity count.
        }  # Ends final report payload.


def _group_by_store(matches: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:  # Groups matches by store.
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)  # Creates grouped storage.
    for match in matches:  # Iterates through saved matches.
        store_key = str(match.get("store_ref", "unknown"))  # Reads store reference safely.
        grouped[store_key].append(match)  # Adds match to the store group.
    return dict(grouped)  # Returns a normal dictionary.


def _calculate_summary(matches: list[dict[str, Any]]) -> dict[str, Any]:  # Calculates weekly totals.
    total_oop = Decimal("0.00")  # Tracks total out-of-pocket.
    total_register_savings = Decimal("0.00")  # Tracks shelf-to-register savings.
    total_rewards_value = Decimal("0.00")  # Tracks rewards earned.
    total_rebates_back = Decimal("0.00")  # Tracks rebates expected back.
    money_maker_count = 0  # Tracks money-maker count.

    for match in matches:  # Iterates through saved matches.
        shelf_price = _to_decimal(match.get("shelf_price"))  # Reads shelf price.
        register_price = _to_decimal(match.get("register_price"))  # Reads register price.
        oop = _to_decimal(match.get("oop"))  # Reads out-of-pocket without reducing it.
        rr_earned = _to_decimal(match.get("rr_earned"))  # Reads Register Rewards.
        ecb_earned = _to_decimal(match.get("ecb_earned"))  # Reads ExtraBucks.
        rebates_back = _to_decimal(match.get("total_rebates_back"))  # Reads rebates.

        total_oop += oop  # Adds OOP separately.
        total_register_savings += shelf_price - register_price  # Adds register-level savings.
        total_rewards_value += rr_earned + ecb_earned  # Adds reward value separately.
        total_rebates_back += rebates_back  # Adds rebate value separately.

        if bool(match.get("is_money_maker", False)):  # Checks saved money-maker flag.
            money_maker_count += 1  # Counts money-maker match.

    final_after_rewards = total_oop - total_rewards_value - total_rebates_back  # Calculates display-only final value.

    return {  # Starts summary payload.
        "total_opportunities": len(matches),  # Stores opportunity count.
        "total_oop": _to_float(total_oop),  # Stores OOP separately.
        "total_register_savings": _to_float(total_register_savings),  # Stores register savings.
        "total_rewards_value": _to_float(total_rewards_value),  # Stores rewards separately.
        "total_rebates_back": _to_float(total_rebates_back),  # Stores rebates separately.
        "final_after_rewards": _to_float(final_after_rewards),  # Stores display-only final value.
        "money_maker_count": money_maker_count,  # Stores money-maker count.
    }  # Ends summary payload.


def _build_store_report(store_ref: str, matches: list[dict[str, Any]]) -> dict[str, Any]:  # Builds one store section.
    store_oop = Decimal("0.00")  # Tracks store OOP.
    store_rewards = Decimal("0.00")  # Tracks store rewards.
    store_rebates = Decimal("0.00")  # Tracks store rebates.
    money_maker_count = 0  # Tracks store money-maker count.
    deal_cards = []  # Stores deal card rows.

    for match in matches:  # Iterates through store matches.
        oop = _to_decimal(match.get("oop"))  # Reads OOP.
        rr_earned = _to_decimal(match.get("rr_earned"))  # Reads Register Rewards.
        ecb_earned = _to_decimal(match.get("ecb_earned"))  # Reads ExtraBucks.
        rebates_back = _to_decimal(match.get("total_rebates_back"))  # Reads rebates.

        store_oop += oop  # Adds OOP separately.
        store_rewards += rr_earned + ecb_earned  # Adds rewards separately.
        store_rebates += rebates_back  # Adds rebates separately.

        if bool(match.get("is_money_maker", False)):  # Checks money-maker flag.
            money_maker_count += 1  # Counts store money maker.

        deal_cards.append(_build_deal_card(match))  # Adds formatted deal card.

    store_final_after_rewards = store_oop - store_rewards - store_rebates  # Calculates display-only store final value.

    return {  # Starts store payload.
        "store_ref": store_ref,  # Stores store reference.
        "totals": {  # Starts store totals.
            "total_opportunities": len(matches),  # Stores store opportunity count.
            "total_oop": _to_float(store_oop),  # Stores store OOP.
            "total_rewards_value": _to_float(store_rewards),  # Stores store rewards.
            "total_rebates_back": _to_float(store_rebates),  # Stores store rebates.
            "final_after_rewards": _to_float(store_final_after_rewards),  # Stores display-only final value.
            "money_maker_count": money_maker_count,  # Stores money-maker count.
        },  # Ends store totals.
        "deals": deal_cards,  # Stores deal cards.
    }  # Ends store payload.


def _build_deal_card(match: dict[str, Any]) -> dict[str, Any]:  # Builds one report card.
    oop = _to_decimal(match.get("oop"))  # Reads OOP.
    rr_earned = _to_decimal(match.get("rr_earned"))  # Reads Register Rewards.
    ecb_earned = _to_decimal(match.get("ecb_earned"))  # Reads ExtraBucks.
    rebates_back = _to_decimal(match.get("total_rebates_back"))  # Reads rebates.
    total_rewards = rr_earned + ecb_earned  # Calculates reward value only.
    final_after_rewards = oop - total_rewards - rebates_back  # Calculates display-only final value.

    return {  # Starts deal card payload.
        "product_ref": str(match.get("product_ref", "")),  # Stores product reference.
        "deal_ref": str(match.get("deal_ref")) if match.get("deal_ref") else None,  # Stores optional deal reference.
        "deal_type": match.get("deal_type", "STANDARD"),  # Stores saved deal type.
        "matched_as_substitute": bool(match.get("matched_as_substitute", False)),  # Stores substitute flag.
        "shelf_price": _to_float(_to_decimal(match.get("shelf_price"))),  # Stores shelf price.
        "register_price": _to_float(_to_decimal(match.get("register_price"))),  # Stores register price.
        "out_of_pocket": _to_float(oop),  # Stores OOP as primary cost.
        "rr_earned": _to_float(rr_earned),  # Stores Register Rewards separately.
        "ecb_earned": _to_float(ecb_earned),  # Stores ExtraBucks separately.
        "total_rewards_value": _to_float(total_rewards),  # Stores reward total separately.
        "total_rebates_back": _to_float(rebates_back),  # Stores rebates separately.
        "final_after_rewards": _to_float(final_after_rewards),  # Stores display-only final value.
        "is_money_maker": bool(match.get("is_money_maker", False)),  # Stores money-maker flag.
        "coupon_refs": [str(ref) for ref in match.get("coupon_refs", [])],  # Stores coupon references separately.
        "rebate_refs": [str(ref) for ref in match.get("rebate_refs", [])],  # Stores rebate references separately.
        "reward_offers": match.get("reward_offers", []),  # Stores reward offers separately.
    }  # Ends deal card payload.


def _to_decimal(value: Any) -> Decimal:  # Converts values to Decimal safely.
    if value is None:  # Handles missing values.
        return Decimal("0.00")  # Returns zero for missing values.
    try:  # Starts safe conversion block.
        return Decimal(str(value))  # Converts through string to reduce float precision problems.
    except (InvalidOperation, ValueError, TypeError):  # Handles unsafe numeric input.
        return Decimal("0.00")  # Returns zero for invalid values.


def _to_float(value: Decimal) -> float:  # Converts Decimal to JSON-safe float.
    return float(value.quantize(Decimal("0.01")))  # Returns two-decimal float.
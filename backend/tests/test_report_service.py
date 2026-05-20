# =============================================================================
# File: backend/tests/test_report_service.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests P1-19B report service grouping, totals, and financial separation.
# SRS Traceability: SRS Section 16 DR-001 through DR-021; SRS Section 20 TS-005.
# SDD Traceability: SDD Section 9 Spending Analytics Design.
# =============================================================================

from __future__ import annotations  # Enables modern type hints.

from datetime import date  # Supports report week dates.
from unittest.mock import AsyncMock, MagicMock  # Supports service dependency mocking.

import pytest  # Supports assertions and async tests.

from backend.data_access.deal_matches import DealMatchesDataAccess  # Supports typed DAL mock.
from backend.services.report_service import ReportService  # Imports service under test.
from backend.services.report_service import _build_deal_card  # Imports helper for focused tests.
from backend.services.report_service import _calculate_summary  # Imports helper for summary tests.
from backend.services.report_service import _group_by_store  # Imports helper for grouping tests.


def _make_match(  # Creates a fake saved deal_match document.
    store_ref: str = "heb",  # Sets default store reference.
    shelf_price: float = 5.00,  # Sets default shelf price.
    register_price: float = 3.99,  # Sets default register price.
    oop: float = 2.99,  # Sets default out-of-pocket.
    rr_earned: float = 0.00,  # Sets default Register Rewards.
    ecb_earned: float = 0.00,  # Sets default ExtraBucks.
    total_rebates_back: float = 0.00,  # Sets default rebates.
    is_money_maker: bool = False,  # Sets default money-maker flag.
    matched_as_substitute: bool = False,  # Sets default substitute flag.
) -> dict:  # Returns a fake match dictionary.
    return {  # Starts fake saved match.
        "store_ref": store_ref,  # Stores store reference.
        "shelf_price": shelf_price,  # Stores shelf price.
        "register_price": register_price,  # Stores register price.
        "oop": oop,  # Stores model field for out-of-pocket.
        "rr_earned": rr_earned,  # Stores Register Rewards.
        "ecb_earned": ecb_earned,  # Stores ExtraBucks.
        "total_rebates_back": total_rebates_back,  # Stores rebates.
        "is_money_maker": is_money_maker,  # Stores money-maker flag.
        "deal_type": "STANDARD",  # Stores deal type.
        "matched_as_substitute": matched_as_substitute,  # Stores substitute flag.
        "coupon_refs": [],  # Stores coupon references.
        "rebate_refs": [],  # Stores rebate references.
        "reward_offers": [],  # Stores reward offers.
        "product_ref": "product-abc",  # Stores product reference.
        "deal_ref": None,  # Stores optional deal reference.
    }  # Ends fake saved match.


def test_group_by_store_groups_matches_by_store_ref() -> None:  # Tests store grouping.
    matches = [_make_match("heb"), _make_match("heb"), _make_match("walmart")]  # Creates mixed-store matches.
    grouped = _group_by_store(matches)  # Groups by store.
    assert len(grouped["heb"]) == 2  # Verifies H-E-B count.
    assert len(grouped["walmart"]) == 1  # Verifies Walmart count.


def test_group_by_store_handles_empty_list() -> None:  # Tests empty grouping.
    grouped = _group_by_store([])  # Groups empty list.
    assert grouped == {}  # Verifies empty result.


def test_calculate_summary_keeps_oop_separate_from_rewards() -> None:  # Tests financial separation.
    matches = [_make_match(oop=5.00, rr_earned=2.00, ecb_earned=1.00)]  # Creates reward match.
    summary = _calculate_summary(matches)  # Calculates summary.
    assert summary["total_oop"] == pytest.approx(5.00)  # Verifies OOP remains unchanged.
    assert summary["total_rewards_value"] == pytest.approx(3.00)  # Verifies rewards separate.
    assert summary["final_after_rewards"] == pytest.approx(2.00)  # Verifies display-only final value.


def test_calculate_summary_keeps_rebates_separate_from_oop() -> None:  # Tests rebate separation.
    matches = [_make_match(oop=10.00, total_rebates_back=5.00)]  # Creates rebate match.
    summary = _calculate_summary(matches)  # Calculates summary.
    assert summary["total_oop"] == pytest.approx(10.00)  # Verifies OOP unchanged.
    assert summary["total_rebates_back"] == pytest.approx(5.00)  # Verifies rebates separate.


def test_calculate_summary_counts_money_makers() -> None:  # Tests money-maker count.
    matches = [_make_match(is_money_maker=True), _make_match(is_money_maker=False)]  # Creates mixed flags.
    summary = _calculate_summary(matches)  # Calculates summary.
    assert summary["money_maker_count"] == 1  # Verifies one money maker.


def test_calculate_summary_handles_empty_report() -> None:  # Tests empty summary.
    summary = _calculate_summary([])  # Calculates empty summary.
    assert summary["total_opportunities"] == 0  # Verifies zero opportunities.
    assert summary["total_oop"] == 0.0  # Verifies zero OOP.
    assert summary["money_maker_count"] == 0  # Verifies zero money makers.


def test_build_deal_card_outputs_required_financial_fields() -> None:  # Tests deal card shape.
    card = _build_deal_card(_make_match(oop=2.99, rr_earned=1.00, total_rebates_back=0.50))  # Builds card.
    assert "out_of_pocket" in card  # Verifies frontend OOP field.
    assert "rr_earned" in card  # Verifies RR field.
    assert "ecb_earned" in card  # Verifies ECB field.
    assert "total_rewards_value" in card  # Verifies rewards field.
    assert "total_rebates_back" in card  # Verifies rebates field.
    assert "final_after_rewards" in card  # Verifies display-only final field.
    assert "is_money_maker" in card  # Verifies money-maker flag.


def test_build_deal_card_keeps_coupon_refs_separate_from_reward_offers() -> None:  # Tests field separation.
    match = _make_match()  # Creates base match.
    match["coupon_refs"] = ["coupon-1"]  # Adds coupon reference.
    match["reward_offers"] = [{"reward_provider": "ibotta", "estimated_cash_value": 1.00}]  # Adds reward offer.
    card = _build_deal_card(match)  # Builds card.
    assert card["coupon_refs"] == ["coupon-1"]  # Verifies coupon refs.
    assert card["reward_offers"] == [{"reward_provider": "ibotta", "estimated_cash_value": 1.00}]  # Verifies reward offers.


def test_build_deal_card_preserves_money_maker_flag() -> None:  # Tests flag preservation.
    card = _build_deal_card(_make_match(is_money_maker=True))  # Builds money-maker card.
    assert card["is_money_maker"] is True  # Verifies flag.


def test_build_deal_card_preserves_substitute_flag() -> None:  # Tests substitute flag.
    card = _build_deal_card(_make_match(matched_as_substitute=True))  # Builds substitute card.
    assert card["matched_as_substitute"] is True  # Verifies flag.


@pytest.mark.asyncio  # Marks async pytest.
async def test_generate_weekly_report_returns_expected_structure() -> None:  # Tests service output structure.
    mock_access = MagicMock(spec=DealMatchesDataAccess)  # Creates DAL mock.
    mock_access.list_by_week_and_store = AsyncMock(return_value=[_make_match("heb"), _make_match("heb")])  # Mocks saved matches.
    service = ReportService(mock_access)  # Creates service.
    report = await service.generate_weekly_report(date(2026, 5, 18))  # Generates report.
    assert report["week_of"] == "2026-05-18"  # Verifies week.
    assert "generated_at" in report  # Verifies timestamp.
    assert "summary" in report  # Verifies summary.
    assert "stores" in report  # Verifies stores.
    assert report["match_count"] == 2  # Verifies match count.


@pytest.mark.asyncio  # Marks async pytest.
async def test_generate_weekly_report_empty_matches_returns_empty_stores() -> None:  # Tests empty report.
    mock_access = MagicMock(spec=DealMatchesDataAccess)  # Creates DAL mock.
    mock_access.list_by_week_and_store = AsyncMock(return_value=[])  # Mocks no saved matches.
    service = ReportService(mock_access)  # Creates service.
    report = await service.generate_weekly_report(date(2026, 5, 18))  # Generates report.
    assert report["stores"] == []  # Verifies no stores.
    assert report["summary"]["total_opportunities"] == 0  # Verifies zero opportunities.
    assert report["match_count"] == 0  # Verifies zero matches.


@pytest.mark.asyncio  # Marks async pytest.
async def test_generate_weekly_report_passes_store_ref_to_dal() -> None:  # Tests store filter.
    mock_access = MagicMock(spec=DealMatchesDataAccess)  # Creates DAL mock.
    mock_access.list_by_week_and_store = AsyncMock(return_value=[])  # Mocks empty result.
    service = ReportService(mock_access)  # Creates service.
    await service.generate_weekly_report(date(2026, 5, 18), store_ref="heb")  # Calls with filter.
    mock_access.list_by_week_and_store.assert_called_once_with(week_of=date(2026, 5, 18), store_ref="heb")  # Verifies DAL call.


def test_report_service_has_no_direct_mongodb_calls() -> None:  # Tests architecture boundary.
    source = open("backend/services/report_service.py", encoding="utf-8").read()  # Reads service source.
    assert "motor" not in source  # Verifies no Motor import.
    assert "pymongo" not in source  # Verifies no PyMongo import.
    assert ".find(" not in source  # Verifies no direct find call.
    assert "insert_one" not in source  # Verifies no direct insert call.
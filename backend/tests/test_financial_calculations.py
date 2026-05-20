from decimal import Decimal  # Imports exact decimal money arithmetic.

from backend.parsers.deal_matcher import calculate_financials  # Imports deal matching financial calculation helper.
from backend.services.report_service import _build_deal_card  # Imports report card formatter for financial separation checks.
from backend.services.report_service import _calculate_summary  # Imports report summary calculator for weekly totals.

from backend.parsers.deal_matcher import decimal_value
from backend.parsers.deal_matcher import get_object_id
from backend.parsers.deal_matcher import reward_matches_product

def test_oop_equals_register_price_minus_register_coupons_only() -> None:  # Verifies coupons reduce checkout OOP.
    result = calculate_financials("10.00", "2.00", "7.00")  # Calculates OOP with rewards present.
    assert result["out_of_pocket"] == Decimal("8.00")  # Confirms rewards did not reduce checkout OOP.


def test_rewards_are_never_subtracted_from_oop() -> None:  # Verifies earned rewards are not register discounts.
    result = calculate_financials("20.00", "5.00", "10.00")  # Calculates financial fields with large rewards.
    assert result["out_of_pocket"] == Decimal("15.00")  # Confirms OOP only subtracts coupons.


def test_money_maker_true_when_rewards_exceed_oop() -> None:  # Verifies money-maker true case.
    result = calculate_financials("5.00", "1.00", "6.00")  # Creates reward value greater than OOP.
    assert result["is_money_maker"] is True  # Confirms rewards greater than OOP create money maker.


def test_money_maker_false_when_oop_exceeds_rewards() -> None:  # Verifies money-maker false case.
    result = calculate_financials("10.00", "1.00", "2.00")  # Creates OOP greater than reward value.
    assert result["is_money_maker"] is False  # Confirms OOP greater than rewards is not money maker.


def test_report_deal_card_keeps_coupons_rewards_and_rebates_separate() -> None:  # Verifies report card field separation.
    match = {  # Creates one saved deal match record.
        "product_name": "Test Product",  # Provides display product name.
        "store_ref": "heb",  # Provides store grouping key.
        "register_price": Decimal("10.00"),  # Provides checkout register price.
        "coupon_total": Decimal("2.00"),  # Provides register-applied coupon amount.
        "oop": Decimal("8.00"),  # Provides out-of-pocket after coupons only.
        "total_rebates_back": Decimal("3.00"),  # Provides rebate value separate from OOP.
        "rr_earned": Decimal("4.00"),  # Provides Register Rewards earned separate from OOP.
        "ecb_earned": Decimal("5.00"),  # Provides ExtraBucks earned separate from OOP.
        "total_rewards_value": Decimal("9.00"),  # Provides total reward value separate from OOP.
        "final_after_rewards": Decimal("-4.00"),  # Provides informational post-reward final value.
        "is_money_maker": True,  # Provides money-maker flag.
    }  # Ends test record.
    card = _build_deal_card(match)  # Builds report JSON deal card.
    assert card["out_of_pocket"] == 8.0  # Confirms OOP remains separate.
    assert card["total_rebates_back"] == 3.0  # Confirms rebates remain separate.
    assert card["rr_earned"] == 4.0  # Confirms RR remains separate.
    assert card["ecb_earned"] == 5.0  # Confirms ECB remains separate.
    
    assert card["final_after_rewards"] == -4.0  # Confirms informational final value is preserved.


def test_report_summary_keeps_rewards_and_rebates_out_of_oop() -> None:  # Verifies weekly summary field separation.
    matches = [  # Creates saved deal match records.
        {  # Creates first match.
            "oop": Decimal("8.00"),  # Provides OOP after coupons.
            "total_rebates_back": Decimal("3.00"),  # Provides rebate value.
            "rr_earned": Decimal("4.00"),  # Provides RR value.
            "ecb_earned": Decimal("0.00"),  # Provides ECB value.
            "total_rewards_value": Decimal("4.00"),  # Provides reward value.
            "final_after_rewards": Decimal("1.00"),  # Provides final informational value.
            "is_money_maker": False,  # Provides money-maker status.
        },  # Ends first match.
        {  # Creates second match.
            "oop": Decimal("2.00"),  # Provides OOP after coupons.
            "total_rebates_back": Decimal("0.00"),  # Provides rebate value.
            "rr_earned": Decimal("5.00"),  # Provides RR value.
            "ecb_earned": Decimal("1.00"),  # Provides ECB value.
            "total_rewards_value": Decimal("6.00"),  # Provides reward value.
            "final_after_rewards": Decimal("-4.00"),  # Provides final informational value.
            "is_money_maker": True,  # Provides money-maker status.
        },  # Ends second match.
    ]  # Ends saved deal match records.
    summary = _calculate_summary(matches)  # Calculates weekly report summary.
    assert summary["total_oop"] == 10.0  # Confirms total OOP is only OOP fields.
    assert summary["total_rebates_back"] == 3.0  # Confirms rebates are separate.
    assert summary["total_rewards_value"] == 10.0  # Confirms all rewards aggregate separately from OOP.
    assert summary["final_after_rewards"] == -3.0  # Confirms final reward-adjusted value remains separate.
    assert summary["money_maker_count"] == 1  # Confirms money-maker count is preserved.


def test_cash_back_reward_affects_final_after_rewards_not_oop() -> None:  # Verifies cash reward behavior.
    result = calculate_financials("12.00", "2.00", "5.00")  # Calculates with cash-back reward value.
    assert result["out_of_pocket"] == Decimal("10.00")  # Confirms cash reward does not reduce OOP.
    assert result["final_after_rewards"] == Decimal("5.00")  # Confirms reward affects final-after-rewards.


def test_points_reward_uses_estimated_cash_value_not_original_points_as_oop_discount() -> None:  # Verifies points separation.
    result = calculate_financials("10.00", "0.00", "1.50")  # Uses estimated cash value for points reward.
    assert result["out_of_pocket"] == Decimal("10.00")  # Confirms points do not reduce OOP.
    assert result["final_after_rewards"] == Decimal("8.50")  # Confirms estimated value affects final-after-rewards only.


def test_claim_required_reward_is_not_treated_as_register_discount() -> None:  # Verifies claim-required reward separation.
    result = calculate_financials("9.00", "1.00", "4.00")  # Calculates with claim-style reward value.
    assert result["out_of_pocket"] == Decimal("8.00")  # Confirms claim reward is not a coupon.
    assert result["final_after_rewards"] == Decimal("4.00")  # Confirms claim reward affects final-after-rewards only.


def test_receipt_required_reward_is_not_treated_as_register_discount() -> None:  # Verifies receipt-required reward separation.
    result = calculate_financials("15.00", "3.00", "6.00")  # Calculates with receipt-submission reward value.
    assert result["out_of_pocket"]== Decimal("12.00")  # Confirms receipt reward is not deducted at register.
    assert result["final_after_rewards"] == Decimal("6.00")  # Confirms receipt reward affects final-after-rewards only.
    
def test_get_object_id_reads_id_field() -> None:  # Verifies id fallback branch.
    document = {"id": "abc123"}  # Creates alternate id field.
    assert get_object_id(document) == "abc123"  # Confirms fallback path works.


def test_reward_match_returns_false_for_non_matching_product() -> None:  # Verifies reward mismatch branch.
    product = {"canonical_name": "Milk"}  # Creates normalized product.
    reward = {"qualifying_products": ["Bread"]}  # Creates unrelated reward.
    assert reward_matches_product(product, reward) is False  # Confirms mismatch branch.


def test_decimal_value_returns_zero_for_invalid_input() -> None:  # Verifies Decimal fallback branch.
    assert decimal_value(None) == Decimal("0")  # Confirms invalid input becomes zero.
# =============================================================================  # File header separator
# File: backend/tests/test_deal_matcher.py  # Identifies the test file path
# Project: Grocery Intelligence Platform  # Identifies the project
# Purpose: Tests P1-19A matching and financial helper logic.  # Explains test purpose
# =============================================================================  # File header separator

from decimal import Decimal  # Imports Decimal for exact money assertions

from backend.parsers.deal_matcher import (  # Imports helper functions under test
    calculate_financials,  # Imports financial calculator
    coupon_matches_product,  # Imports coupon matcher
    product_matches_deal,  # Imports product-to-deal matcher
    reward_matches_product,  # Imports reward matcher
)


def test_direct_product_to_deal_match() -> None:  # Tests canonical product direct match
    product = {"canonical_name": "HEB Milk"}  # Creates product fixture
    deal = {"canonical_name": "HEB Milk"}  # Creates deal fixture

    matched, substitute = product_matches_deal(product, deal)  # Runs matcher

    assert matched is True  # Verifies product matched deal
    assert substitute is False  # Verifies match was not substitute


def test_acceptable_substitute_match() -> None:  # Tests acceptable substitute matching
    product = {"canonical_name": "Milk", "acceptable_substitutes": ["Mootopia Milk"]}  # Creates product fixture
    deal = {"canonical_name": "Mootopia Milk"}  # Creates substitute deal fixture

    matched, substitute = product_matches_deal(product, deal)  # Runs matcher

    assert matched is True  # Verifies substitute matched
    assert substitute is True  # Verifies substitute flag


def test_coupon_attachment_direct_match() -> None:  # Tests coupon product match
    product = {"canonical_name": "HEB Yogurt"}  # Creates product fixture
    coupon = {"canonical_name": "HEB Yogurt", "discount_amount": "1.00"}  # Creates coupon fixture

    result = coupon_matches_product(product, coupon)  # Runs coupon matcher

    assert result is True  # Verifies coupon attaches


def test_basket_coupon_attachment() -> None:  # Tests basket coupon match
    product = {"canonical_name": "HEB Yogurt"}  # Creates product fixture
    coupon = {"coupon_scope": "basket", "discount_amount": "5.00"}  # Creates basket coupon fixture

    result = coupon_matches_product(product, coupon)  # Runs coupon matcher

    assert result is True  # Verifies basket coupon attaches


def test_reward_offer_attachment_by_product() -> None:  # Tests reward product match
    product = {"canonical_name": "HEB Eggs"}  # Creates product fixture
    reward = {"qualifying_products": ["HEB Eggs"], "estimated_cash_value": "2.00"}  # Creates reward fixture

    result = reward_matches_product(product, reward)  # Runs reward matcher

    assert result is True  # Verifies reward attaches


def test_reward_offer_attachment_by_category() -> None:  # Tests reward category match
    product = {"canonical_name": "HEB Eggs", "category": "Dairy"}  # Creates categorized product fixture
    reward = {"qualifying_categories": ["Dairy"], "estimated_cash_value": "2.00"}  # Creates category reward fixture

    result = reward_matches_product(product, reward)  # Runs reward matcher

    assert result is True  # Verifies category reward attaches


def test_out_of_pocket_excludes_rewards() -> None:  # Tests rewards do not reduce OOP
    result = calculate_financials(  # Runs financial calculation
        register_price=Decimal("5.00"),  # Sets register price
        coupon_total=Decimal("1.00"),  # Sets register coupon amount
        reward_total=Decimal("3.00"),  # Sets reward amount
    )  # Ends calculation

    assert result["out_of_pocket"] == Decimal("4.00")  # Verifies OOP only subtracts coupon
    assert result["final_after_rewards"] == Decimal("1.00")  # Verifies rewards affect final net


def test_money_maker_true_when_rewards_exceed_oop() -> None:  # Tests true money maker case
    result = calculate_financials(  # Runs financial calculation
        register_price=Decimal("3.00"),  # Sets register price
        coupon_total=Decimal("1.00"),  # Sets coupon amount
        reward_total=Decimal("3.00"),  # Sets reward amount
    )  # Ends calculation

    assert result["out_of_pocket"] == Decimal("2.00")  # Verifies OOP
    assert result["final_after_rewards"] == Decimal("-1.00")  # Verifies negative net cost
    assert result["is_money_maker"] is True  # Verifies money maker flag


def test_money_maker_false_when_rewards_do_not_exceed_oop() -> None:  # Tests false money maker case
    result = calculate_financials(  # Runs financial calculation
        register_price=Decimal("5.00"),  # Sets register price
        coupon_total=Decimal("1.00"),  # Sets coupon amount
        reward_total=Decimal("2.00"),  # Sets reward amount
    )  # Ends calculation

    assert result["out_of_pocket"] == Decimal("4.00")  # Verifies OOP
    assert result["final_after_rewards"] == Decimal("2.00")  # Verifies positive net cost
    assert result["is_money_maker"] is False  # Verifies money maker flag is false
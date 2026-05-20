# =============================================================================  # File header separator
# File: backend/tests/test_deal_match_service.py  # Identifies the test file path
# Project: Grocery Intelligence Platform  # Identifies the project
# Purpose: Tests P1-19A service orchestration using fake DALs.  # Explains test purpose
# =============================================================================  # File header separator

from datetime import date  # Imports date for week_of
from decimal import Decimal  # Imports Decimal for money assertions

import pytest  # Imports pytest for async test support

from backend.services.deal_match_service import generate_deal_matches  # Imports service under test


class FakeProductsDal:  # Defines fake products DAL
    async def find_my_items(self) -> list[dict]:  # Returns fake My Items
        return [  # Starts product list
            {  # Starts product fixture
                "_id": "product-1",  # Sets fake product id
                "canonical_name": "HEB Milk",  # Sets canonical product name
                "avg_price": Decimal("4.00"),  # Sets shelf price
                "acceptable_substitutes": ["Mootopia Milk"],  # Sets substitute list
            }  # Ends product fixture
        ]  # Ends product list


class FakeAdsDal:  # Defines fake ads DAL
    async def list_active_heb_ads(self) -> list[dict]:  # Returns fake active H-E-B ads
        return [  # Starts ad list
            {  # Starts ad fixture
                "_id": "ad-1",  # Sets fake ad id
                "canonical_name": "HEB Milk",  # Sets matching ad name
                "store_ref": "store-1",  # Sets fake store id
                "sale_price": Decimal("3.00"),  # Sets sale/register price
            }  # Ends ad fixture
        ]  # Ends ad list


class FakeCouponsDal:  # Defines fake coupons DAL
    async def list_active_heb_coupons(self) -> list[dict]:  # Returns fake active H-E-B coupons
        return [  # Starts coupon list
            {  # Starts coupon fixture
                "_id": "coupon-1",  # Sets fake coupon id
                "canonical_name": "HEB Milk",  # Sets matching coupon name
                "discount_amount": Decimal("1.00"),  # Sets coupon value
            }  # Ends coupon fixture
        ]  # Ends coupon list


class FakeRewardOffersDal:  # Defines fake reward offers DAL
    async def list_active_offers(self, retailer: str) -> list[dict]:  # Returns fake active rewards
        return [  # Starts reward list
            {  # Starts reward fixture
                "_id": "reward-1",  # Sets fake reward id
                "retailer": retailer,  # Stores retailer passed to DAL
                "qualifying_products": ["HEB Milk"],  # Sets qualifying products
                "estimated_cash_value": Decimal("3.00"),  # Sets reward value
            }  # Ends reward fixture
        ]  # Ends reward list


class FakeDealMatchesDal:  # Defines fake deal matches DAL
    def __init__(self) -> None:  # Initializes fake DAL state
        self.deleted_week = None  # Tracks deleted week
        self.saved_matches = []  # Tracks inserted matches

    async def delete_by_week(self, week_of: date) -> int:  # Fakes deletion by week
        self.deleted_week = week_of  # Saves deleted week
        return 0  # Returns zero deleted records

    async def insert_many_matches(self, matches: list[dict]) -> list[str]:  # Fakes insert many
        self.saved_matches = matches  # Stores saved matches
        return ["match-1"] if matches else []  # Returns fake inserted ids


@pytest.mark.asyncio  # Marks test as async
async def test_generate_deal_matches_saves_reward_aware_match() -> None:  # Tests full service orchestration
    deal_matches_dal = FakeDealMatchesDal()  # Creates fake deal matches DAL
    week_of = date(2026, 5, 18)  # Creates report week date

    inserted_ids = await generate_deal_matches(  # Runs service
        products_dal=FakeProductsDal(),  # Passes fake products DAL
        ads_dal=FakeAdsDal(),  # Passes fake ads DAL
        coupons_dal=FakeCouponsDal(),  # Passes fake coupons DAL
        reward_offers_dal=FakeRewardOffersDal(),  # Passes fake reward offers DAL
        deal_matches_dal=deal_matches_dal,  # Passes fake deal matches DAL
        week_of=week_of,  # Passes report week
    )  # Ends service call

    assert inserted_ids == ["match-1"]  # Verifies fake inserted id
    assert deal_matches_dal.deleted_week == week_of  # Verifies old week was cleared
    assert len(deal_matches_dal.saved_matches) == 1  # Verifies one match saved

    saved_match = deal_matches_dal.saved_matches[0]  # Reads saved match

    assert saved_match["product_ref"] == "product-1"  # Verifies product reference
    assert saved_match["deal_ref"] == "ad-1"  # Verifies ad reference
    assert saved_match["coupon_refs"] == ["coupon-1"]  # Verifies coupon reference
    assert saved_match["reward_offer_refs"] == ["reward-1"]  # Verifies reward reference
    assert saved_match["out_of_pocket"] == Decimal("2.00")  # Verifies OOP excludes reward
    assert saved_match["total_rewards_value"] == Decimal("3.00")  # Verifies reward value
    assert saved_match["final_after_rewards"] == Decimal("-1.00")  # Verifies final net cost
    assert saved_match["is_money_maker"] is True  # Verifies money maker flag
    assert saved_match["week_of"] == "2026-05-18"  # Verifies week_of value
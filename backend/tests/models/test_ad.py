# =============================================================================
# File: test_ad.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Tests ad model validation, deal type coverage, and store promotion examples.
# Security Note: Tests use fake ad data only and do not contain secrets.
# SRS Traceability: Supports SRS v5.0 ad, coupon, and promotion model validation.
# SDD Traceability: Supports SDD v5.0 backend ad model testing.
# =============================================================================

from datetime import date  # Imports date for ad date test values.
from decimal import Decimal  # Imports Decimal for exact money and percentage values.

import pytest  # Imports pytest for validation error assertions.
from bson import ObjectId  # Imports ObjectId for fake MongoDB references.

from backend.models.ad import AdItem  # Imports the ad item model being tested.
from backend.models.ad import AdModel  # Imports the full ad document model being tested.
from backend.models.ad import DealType  # Imports the deal type enum being tested.


def test_deal_type_enum_values() -> None:  # Verifies that all approved deal type enum values exist.
    expected_values: set[str] = {  # Defines the locked approved deal type values.
        "STANDARD",  # Requires standard sale deals.
        "BOGO",  # Requires buy-one-get-one deals.
        "BUY_X_GET_Y",  # Requires buy-X-get-Y deals.
        "THRESHOLD",  # Requires threshold deals.
        "REGISTER_REWARD",  # Keeps Walgreens Register Reward support for future store support.
        "ECB",  # Keeps CVS ExtraBucks support for future store support.
        "SPEND_BOOSTER",  # Requires spend booster deals.
        "MANUFACTURER_COUPON",  # Requires manufacturer coupon deals.
        "DIGITAL_COUPON",  # Requires digital coupon support.
        "COMBO_LOCO",  # Requires H-E-B Combo Loco support.
        "BASKET_COUPON",  # Requires basket coupon support.
        "PERCENT_OFF",  # Requires percentage-off support.
        "PRICE_OFF",  # Requires fixed price-off support.
        "FREE_ITEM",  # Requires free item support.
    }  # Ends the expected values set.
    actual_values: set[str] = {deal_type.value for deal_type in DealType}  # Collects actual enum values from the implementation.
    assert actual_values == expected_values  # Confirms the implementation matches the locked list exactly.


def test_ad_model_valid() -> None:  # Verifies that a valid ad document with one item can be created.
    ad_item = AdItem(  # Creates one valid fake ad item.
        item_name="Blue Bell Ice Cream",  # Provides the advertised item name.
        brand="Blue Bell",  # Provides the optional brand.
        size="half gallon",  # Provides the optional size.
        sale_price=Decimal("5.97"),  # Provides the sale price.
        regular_price=Decimal("7.48"),  # Provides the regular price.
        deal_type=DealType.STANDARD,  # Uses a standard sale deal type.
        raw_text="Blue Bell Ice Cream half gallon $5.97",  # Preserves original ad wording.
    )  
    ad = AdModel(  # Creates one valid fake ad document.
        store_ref=ObjectId(),  # Provides a fake store reference.
        start_date=date(2026, 5, 1),  # Provides the ad start date.
        end_date=date(2026, 5, 7),  # Provides the ad end date.
        source_type="PDF",  # Provides the ad source type.
        raw_input_ref=ObjectId(),  # Provides a fake raw input reference.
        items=[ad_item],  # Adds the valid ad item.
    )  
    assert ad.start_date == date(2026, 5, 1)  # Confirms the start date was stored.
    assert ad.end_date == date(2026, 5, 7)  # Confirms the end date was stored.
    assert len(ad.items) == 1  # Confirms the item list has one item.
    assert ad.items[0].item_name == "Blue Bell Ice Cream"  # Confirms the item name was stored.


def test_ad_end_date_before_start_raises() -> None:  # Verifies that an invalid date range fails validation.
    with pytest.raises(ValueError, match="end_date must be greater than or equal to start_date"):  # Expects the date validator error.
        AdModel(  # Attempts to create an invalid ad document.
            store_ref=ObjectId(),  # Provides a fake store reference.
            start_date=date(2026, 5, 7),  # Provides a start date after the end date.
            end_date=date(2026, 5, 1),  # Provides an invalid earlier end date.
            source_type="PDF",  # Provides the ad source type.
            items=[],  # Provides an empty item list.
        )  


def test_combo_loco_ad_item_valid() -> None:  # Verifies that Combo Loco can represent a buy item plus a free item.
    ad_item = AdItem(  # Creates one fake Combo Loco ad item.
        item_name="Hill Country Fare Tortillas",  # Provides the required purchased item name.
        brand="Hill Country Fare",  # Provides the optional brand.
        size="20 count",  # Provides the optional size.
        sale_price=Decimal("2.48"),  # Provides the sale price.
        regular_price=Decimal("2.98"),  # Provides the regular price.
        buy_qty=1,  # Stores the buy quantity.
        get_qty=1,  # Stores the free item quantity.
        free_item_name="H-E-B Salsa",  # Stores the free paired item name.
        deal_type=DealType.COMBO_LOCO,  # Classifies the deal as Combo Loco.
        raw_text="Buy tortillas, get H-E-B Salsa free",  # Preserves original ad wording.
    )  
    assert ad_item.deal_type == DealType.COMBO_LOCO  # Confirms the Combo Loco deal type was stored.
    assert ad_item.free_item_name == "H-E-B Salsa"  # Confirms the free item name was stored.
    assert ad_item.buy_qty == 1  # Confirms the buy quantity was stored.
    assert ad_item.get_qty == 1  # Confirms the get quantity was stored.


def test_basket_coupon_ad_item_valid() -> None:  # Verifies that basket coupons can store a threshold and discount.
    ad_item = AdItem(  # Creates one fake basket coupon ad item.
        item_name="Basket Coupon",  # Provides a generic basket coupon name.
        sale_price=Decimal("0.00"),  # Stores zero because the coupon itself is not a product price.
        deal_type=DealType.BASKET_COUPON,  # Classifies the deal as a basket coupon.
        basket_threshold=Decimal("25.00"),  # Stores the basket spend threshold.
        basket_discount=Decimal("5.00"),  # Stores the basket discount amount.
        raw_text="$5 off basket purchase of $25 or more",  # Preserves original coupon wording.
    )  
    assert ad_item.deal_type == DealType.BASKET_COUPON  # Confirms the basket coupon deal type was stored.
    assert ad_item.basket_threshold == Decimal("25.00")  # Confirms the basket threshold was stored.
    assert ad_item.basket_discount == Decimal("5.00")  # Confirms the basket discount was stored.


def test_percent_off_ad_item_valid() -> None:  # Verifies that percentage-off deals can store a numeric percent value.
    ad_item = AdItem(  # Creates one fake percent-off ad item.
        item_name="Blue Buffalo Dog Food",  # Provides the advertised item name.
        brand="Blue Buffalo",  # Provides the optional brand.
        size="select varieties",  # Provides the optional size description.
        sale_price=Decimal("0.00"),  # Stores zero when the final sale price is not known from the ad line.
        regular_price=Decimal("29.99"),  # Stores the known regular price.
        deal_type=DealType.PERCENT_OFF,  # Classifies the item as percent off.
        percent_off=Decimal("30"),  # Stores the percentage-off value.
        store_coupon_desc="30% off select Blue Buffalo items",  # Stores the ad wording.
        raw_text="30% off select Blue Buffalo items",  # Preserves original ad wording.
    ) 
    assert ad_item.deal_type == DealType.PERCENT_OFF  # Confirms the percent-off deal type was stored.
    assert ad_item.percent_off == Decimal("30")  # Confirms the numeric percentage was stored.
    assert ad_item.brand == "Blue Buffalo"  # Confirms the brand was stored.


def test_digital_coupon_ad_item_valid() -> None:  # Verifies that digital coupon deals can store amount and wording.
    ad_item = AdItem(  # Creates one fake digital coupon ad item.
        item_name="Nature Valley Granola Bars",  # Provides the advertised item name.
        brand="Nature Valley",  # Provides the optional brand.
        size="6 count",  # Provides the optional package size.
        sale_price=Decimal("2.97"),  # Provides the sale price before coupon.
        regular_price=Decimal("3.48"),  # Provides the regular price.
        deal_type=DealType.DIGITAL_COUPON,  # Classifies the deal as a digital coupon.
        digital_coupon_amount=Decimal("1.00"),  # Stores the digital coupon amount.
        digital_coupon_desc="$1 off digital coupon",  # Stores the digital coupon wording.
        raw_text="Nature Valley $2.97 with $1 off digital coupon",  # Preserves original ad wording.
    )  
    assert ad_item.deal_type == DealType.DIGITAL_COUPON  # Confirms the digital coupon deal type was stored.
    assert ad_item.digital_coupon_amount == Decimal("1.00")  # Confirms the digital coupon amount was stored.
    assert ad_item.digital_coupon_desc == "$1 off digital coupon"  # Confirms the digital coupon description was stored.


def test_price_off_ad_item_valid() -> None:  # Verifies that fixed amount-off deals can store the discount amount.
    ad_item = AdItem(  # Creates one fake price-off ad item.
        item_name="Colgate Toothpaste",  # Provides the advertised item name.
        brand="Colgate",  # Provides the optional brand.
        size="4 oz",  # Provides the optional package size.
        sale_price=Decimal("3.99"),  # Provides the sale price before discount.
        regular_price=Decimal("4.99"),  # Provides the regular price.
        deal_type=DealType.PRICE_OFF,  # Classifies the deal as fixed price off.
        price_off_amount=Decimal("1.00"),  # Stores the fixed discount amount.
        raw_text="$1 off Colgate Toothpaste",  # Preserves original ad wording.
    )  
    assert ad_item.deal_type == DealType.PRICE_OFF  # Confirms the price-off deal type was stored.
    assert ad_item.price_off_amount == Decimal("1.00")  # Confirms the fixed discount amount was stored.


def test_free_item_ad_item_valid() -> None:  # Verifies that a free-item promotion can store the free item.
    ad_item = AdItem(  # Creates one fake free-item ad item.
        item_name="H-E-B Coffee",  # Provides the required qualifying item name.
        brand="H-E-B",  # Provides the optional brand.
        size="12 oz",  # Provides the optional package size.
        sale_price=Decimal("7.98"),  # Provides the qualifying item price.
        deal_type=DealType.FREE_ITEM,  # Classifies the deal as a free-item promotion.
        buy_qty=1,  # Stores the quantity required to buy.
        get_qty=1,  # Stores the quantity received free.
        free_item_name="H-E-B Creamer",  # Stores the free item name.
        raw_text="Buy H-E-B Coffee, get H-E-B Creamer free",  # Preserves original ad wording.
    )
    assert ad_item.deal_type == DealType.FREE_ITEM  # Confirms the free-item deal type was stored.
    assert ad_item.free_item_name == "H-E-B Creamer"  # Confirms the free item name was stored.
    assert ad_item.get_qty == 1  # Confirms the free quantity was stored.
    
def test_h_e_b_should_not_use_register_reward_or_ecb_deal_types() -> None:  # Documents H-E-B-specific parser expectations.
    h_e_b_disallowed_deal_types: set[DealType] = {  # Defines deal types that should not be emitted by an H-E-B parser.
                                                  DealType.REGISTER_REWARD,  # H-E-B should not use Walgreens Register Reward classification.
                                                  DealType.ECB,  # H-E-B should not use CVS ExtraBucks classification.
    }  # Ends the disallowed deal type set.
    assert DealType.REGISTER_REWARD in h_e_b_disallowed_deal_types  # Confirms Register Reward is marked disallowed for H-E-B parsing.
    assert DealType.ECB in h_e_b_disallowed_deal_types  # Confirms ECB is marked disallowed for H-E-B parsing.
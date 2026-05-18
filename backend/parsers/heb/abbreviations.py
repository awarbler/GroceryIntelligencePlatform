from __future__ import annotations  # Enables modern type hint behavior.

from dataclasses import dataclass  # Imports dataclass for immutable seed records.


ABBREVIATIONS_VERSION: str = "heb-abbrev-v1.0"  # Stores the HEB alias seed version for traceability.


@dataclass(frozen=True)  # Makes each seed mapping immutable.
class HebProductSeed:  # Defines one product seed mapping.
    canonical_name: str  # Stores the canonical product catalog name.
    aliases: tuple[str, ...]  # Stores receipt names that map to the canonical product.
    brand: str | None = None  # Stores optional brand metadata.
    category: str | None = None  # Stores optional product category metadata.


HEB_PRODUCT_SEEDS: tuple[HebProductSeed, ...] = (  # Defines Phase 1 HEB online receipt alias seeds.
    HebProductSeed("Mission Yellow Corn Tortillas 30 ct", ("Mission 25 Calories Yellow Corn Tortillas, 30 ct",), "Mission", "Food and Grocery"),  # Seed 1.
    HebProductSeed("H-E-B Bakery Banana Nut Mini Muffins 12 ct", ("H-E-B Bakery Banana Nut Mini Muffins, 12 ct",), "H-E-B", "Food and Grocery"),  # Seed 2.
    HebProductSeed("H-E-B Bakery Chocolate Chip Mini Muffins 12 ct", ("H-E-B Bakery Chocolate Chip Mini Muffins, 12 ct",), "H-E-B", "Food and Grocery"),  # Seed 3.
    HebProductSeed("Thomas Plain Bagels 6 ct", ("Thomas' Plain Bagels, 6 ct",), "Thomas", "Food and Grocery"),  # Seed 4.
    HebProductSeed("H-E-B Mi Tienda Baked Corn Tostadas 18 ct", ("H-E-B Mi Tienda Baked Corn Tostadas, 18 ct",), "H-E-B Mi Tienda", "Food and Grocery"),  # Seed 5.
    HebProductSeed("H-E-B Mi Tienda Agua Fresca Lemonade 32 fl oz", ("H-E-B Mi Tienda Agua Fresca - Lemonade (Limonada), 32 fl oz",), "H-E-B Mi Tienda", "Food and Grocery"),  # Seed 6.
    HebProductSeed("H-E-B Mi Tienda Mango Nectar 11.16 oz", ("H-E-B Mi Tienda Mango Nectar, 11.16 oz",), "H-E-B Mi Tienda", "Food and Grocery"),  # Seed 7.
    HebProductSeed("H-E-B Colby Monterey Jack Sliced Cheese 10 ct", ("H-E-B Colby & Monterey Jack Sliced Cheese, 10 ct",), "H-E-B", "Food and Grocery"),  # Seed 8.
    HebProductSeed("H-E-B Mootopia Lactose Free 2 Percent Milk 1/2 gal", ("H-E-B Mootopia 13g Protein Lactose Free 2% Reduced Fat Milk, 1/2 gal",), "H-E-B", "Food and Grocery"),  # Seed 9.
    HebProductSeed("H-E-B Mexican Style Shredded Cheese Blend 16 oz", ("H-E-B Mexican Style Shredded Cheese Blend, 16 oz",), "H-E-B", "Food and Grocery"),  # Seed 10.
    HebProductSeed("H-E-B Provolone Sliced Cheese 10 ct", ("H-E-B Provolone Sliced Cheese, 10 ct",), "H-E-B", "Food and Grocery"),  # Seed 11.
    HebProductSeed("H-E-B Mi Tienda Salsa Tradicional Mild 16 oz", ("H-E-B Mi Tienda Salsa Tradicional – Mild, 16 oz",), "H-E-B Mi Tienda", "Food and Grocery"),  # Seed 12.
    HebProductSeed("H-E-B Mi Tienda Arroz Mexicano Rice 15 oz", ("H-E-B Mi Tienda Arroz Mexicano Rice, 15 oz",), "H-E-B Mi Tienda", "Food and Grocery"),  # Seed 13.
    HebProductSeed("Oscar Mayer Deli Fresh Oven Roasted Turkey Breast 16 oz", ("Oscar Mayer Deli Fresh Oven Roasted Turkey Breast, 16 oz",), "Oscar Mayer", "Food and Grocery"),  # Seed 14.
    HebProductSeed("H-E-B Mi Tienda Frijoles con Chorizo Refried Pinto Beans 17.6 oz", ("H-E-B Mi Tienda Frijoles con Chorizo Refried Pinto Beans, 17.6 oz",), "H-E-B Mi Tienda", "Food and Grocery"),  # Seed 15.
    HebProductSeed("Yasso Chocolate Fudge Frozen Greek Yogurt Bars 4 ct", ("Yasso Chocolate Fudge Frozen Greek Yogurt Bars, 4 ct",), "Yasso", "Food and Grocery"),  # Seed 16.
    HebProductSeed("Yasso Vanilla Bean Frozen Greek Yogurt Sandwiches 3 ct", ("Yasso Vanilla Bean Frozen Greek Yogurt Sandwiches, 3 ct",), "Yasso", "Food and Grocery"),  # Seed 17.
    HebProductSeed("Yasso Mint Chocolate Chip Frozen Greek Yogurt Bars 4 ct", ("Yasso Mint Chocolate Chip Frozen Greek Yogurt Bars, 4 ct",), "Yasso", "Food and Grocery"),  # Seed 18.
    HebProductSeed("Yasso Chocolate Chip Cookie Dough Frozen Greek Yogurt Bars 4 ct", ("Yasso Chocolate Chip Cookie Dough Frozen Greek Yogurt Bars, 4 ct",), "Yasso", "Food and Grocery"),  # Seed 19.
    HebProductSeed("Fresh Bunch of Bananas 4-7 Bananas Avg 2.4 lbs", ("Fresh Bunch of Bananas, 4-7 Bananas, Avg. 2.4 lbs",), None, "Food and Grocery"),  # Seed 20.
    HebProductSeed("Fresh Jumbo Hass Avocado Each", ("Fresh Jumbo Hass Avocado, Each",), None, "Food and Grocery"),  # Seed 21.
    HebProductSeed("H-E-B Premium Fresh Hydroponic Strawberries 1 lb", ("H-E-B Premium Fresh Hydroponic Strawberries, 1 lb",), "H-E-B", "Food and Grocery"),  # Seed 22.
    HebProductSeed("Fresh Large Mango Each", ("Fresh Large Mango, Each",), None, "Food and Grocery"),  # Seed 23.
    HebProductSeed("Fresh Green Bell Pepper Each", ("Fresh Green Bell Pepper, Each",), None, "Food and Grocery"),  # Seed 24.
    HebProductSeed("Fresh Jumbo Blueberries 9.8 oz", ("Fresh Jumbo Blueberries, 9.8 oz",), None, "Food and Grocery"),  # Seed 25.
    HebProductSeed("Fresh Aloha Bell Pepper Each", ("Fresh Aloha Bell Pepper, Each",), None, "Food and Grocery"),  # Seed 26.
    HebProductSeed("Fresh Raspberries 6 oz", ("Fresh Raspberries, 6 oz",), None, "Food and Grocery"),  # Seed 27.
    HebProductSeed("H-E-B Fresh Sweet Karoline Blackberries 12 oz", ("H-E-B Fresh Sweet Karoline Blackberries, 12 oz",), "H-E-B", "Food and Grocery"),  # Seed 28.
    HebProductSeed("H-E-B Premium Fresh Sweet Karoline Blackberries 6 oz", ("H-E-B Premium Fresh Sweet Karoline Blackberries, 6 oz",), "H-E-B", "Food and Grocery"),  # Seed 29.
    HebProductSeed("H-E-B Shaved Beef Steak 16 oz", ("H-E-B Shaved Beef Steak, 16 oz",), "H-E-B", "Food and Grocery"),  # Seed 30.
    HebProductSeed("H-E-B Mi Tienda Cantinero Botana Mixta Snack Mix 3 oz", ("H-E-B Mi Tienda Cantinero Botana Mixta Snack Mix - Peanuts & Tortilla Chips, 3 oz",), "H-E-B Mi Tienda", "Food and Grocery"),  # Seed 31.
    HebProductSeed("H-E-B Classic Granola 14 oz", ("H-E-B Classic Granola, 14 oz",), "H-E-B", "Food and Grocery"),  # Seed 32.
)  # Ends Phase 1 HEB seed tuple.
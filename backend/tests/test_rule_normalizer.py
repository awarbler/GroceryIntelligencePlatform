from __future__ import annotations  # Enables modern type hint behavior.

from pathlib import Path  # Imports Path for source file inspection.
from typing import Any  # Imports Any for fake product document typing.

import pytest  # Imports pytest for async test execution.

from backend.normalizer.rule_normalizer import EXACT_ALIAS_MATCH  # Imports exact alias match label.
from backend.normalizer.rule_normalizer import EXACT_CANONICAL_MATCH  # Imports exact canonical match label.
from backend.normalizer.rule_normalizer import NO_MATCH  # Imports no-match label.
from backend.normalizer.rule_normalizer import NORMALIZER_VERSION  # Imports normalizer version.
from backend.normalizer.rule_normalizer import PARTIAL_TOKEN_MATCH  # Imports partial token match label.
from backend.normalizer.rule_normalizer import normalize_product_name  # Imports normalizer function.
from backend.normalizer.rule_normalizer import seed_heb_product_aliases  # Imports seed function.
from backend.parsers.heb.abbreviations import HEB_PRODUCT_SEEDS  # Imports seed data.


class FakeProductAccess:  # Defines fake data access for tests.
    def __init__(self) -> None:  # Initializes fake access object.
        self.products: list[dict[str, Any]] = []  # Stores fake product documents.

    async def find_all_products(self) -> list[dict[str, Any]]:  # Defines fake find-all method.
        return self.products  # Returns fake products.

    async def upsert_product_alias_seed(  # Defines fake idempotent seed upsert.
        self,  # Receives fake access instance.
        canonical_name: str,  # Receives canonical name.
        aliases: list[str],  # Receives aliases.
        brand: str | None,  # Receives brand.
        category: str | None,  # Receives category.
    ) -> None:  # Returns no value.
        for product in self.products:  # Iterates existing products.
            if product["canonical_name"] == canonical_name:  # Checks for existing canonical product.
                merged_aliases: set[str] = set(product.get("aliases", []))  # Reads existing aliases.
                merged_aliases.update(aliases)  # Adds new aliases.
                product["aliases"] = sorted(merged_aliases)  # Stores deterministic alias list.
                return  # Stops after update.
        self.products.append(  # Adds a new fake product.
            {  # Starts fake product document.
                "_id": f"product-{len(self.products) + 1}",  # Creates deterministic fake id.
                "canonical_name": canonical_name,  # Stores canonical name.
                "aliases": sorted(set(aliases)),  # Stores unique aliases.
                "brand": brand,  # Stores brand.
                "category": category,  # Stores category.
            }  # Ends fake product document.
        )  # Ends append.


@pytest.mark.asyncio  # Marks test as async.
async def test_heb_seed_has_at_least_30_mappings() -> None:  # Tests seed count.
    assert len(HEB_PRODUCT_SEEDS) >= 30  # Verifies acceptance criterion.


@pytest.mark.asyncio  # Marks test as async.
async def test_seed_is_idempotent() -> None:  # Tests idempotent seeding.
    product_access: FakeProductAccess = FakeProductAccess()  # Creates fake product access.
    first_count: int = await seed_heb_product_aliases(product_access)  # Runs first seed.
    second_count: int = await seed_heb_product_aliases(product_access)  # Runs second seed.

    assert first_count == len(HEB_PRODUCT_SEEDS)  # Verifies first processed count.
    assert second_count == len(HEB_PRODUCT_SEEDS)  # Verifies second processed count.
    assert len(product_access.products) == len(HEB_PRODUCT_SEEDS)  # Verifies no duplicate products.


@pytest.mark.asyncio  # Marks test as async.
async def test_exact_canonical_name_match_works() -> None:  # Tests exact canonical match.
    product_access: FakeProductAccess = FakeProductAccess()  # Creates fake product access.
    await seed_heb_product_aliases(product_access)  # Seeds fake products.

    result = await normalize_product_name("Mission Yellow Corn Tortillas 30 ct", product_access)  # Normalizes canonical name.

    assert result.normalized_name == "Mission Yellow Corn Tortillas 30 ct"  # Verifies canonical result.
    assert result.product_ref is not None  # Verifies product reference.
    assert result.confidence == 1.0  # Verifies exact confidence.
    assert result.matched_rule_type == EXACT_CANONICAL_MATCH  # Verifies match type.
    assert result.normalizer_version == NORMALIZER_VERSION  # Verifies version traceability.


@pytest.mark.asyncio  # Marks test as async.
async def test_exact_alias_match_works_for_real_heb_parser_name() -> None:  # Tests exact alias match.
    product_access: FakeProductAccess = FakeProductAccess()  # Creates fake product access.
    await seed_heb_product_aliases(product_access)  # Seeds fake products.

    result = await normalize_product_name("Mission 25 Calories Yellow Corn Tortillas, 30 ct", product_access)  # Normalizes P1-08-style name.

    assert result.normalized_name == "Mission Yellow Corn Tortillas 30 ct"  # Verifies alias normalization.
    assert result.product_ref is not None  # Verifies product reference.
    assert result.confidence == 1.0  # Verifies exact alias confidence.
    assert result.matched_rule_type == EXACT_ALIAS_MATCH  # Verifies match type.


@pytest.mark.asyncio  # Marks test as async.
async def test_partial_token_match_returns_expected_candidate() -> None:  # Tests partial token match.
    product_access: FakeProductAccess = FakeProductAccess()  # Creates fake product access.
    await seed_heb_product_aliases(product_access)  # Seeds fake products.

    result = await normalize_product_name("Mission Corn Tortillas 30 ct", product_access)  # Normalizes partial product name.

    assert result.normalized_name == "Mission Yellow Corn Tortillas 30 ct"  # Verifies partial candidate.
    assert result.product_ref is not None  # Verifies product reference.
    assert result.confidence == 0.70  # Verifies partial confidence.
    assert result.matched_rule_type == PARTIAL_TOKEN_MATCH  # Verifies match type.


@pytest.mark.asyncio  # Marks test as async.
async def test_no_match_returns_raw_name_and_zero_confidence() -> None:  # Tests no-match behavior.
    product_access: FakeProductAccess = FakeProductAccess()  # Creates fake product access.
    await seed_heb_product_aliases(product_access)  # Seeds fake products.

    result = await normalize_product_name("Unknown Mystery Product 99 oz", product_access)  # Normalizes unknown item.

    assert result.normalized_name == "Unknown Mystery Product 99 oz"  # Verifies raw name preserved.
    assert result.product_ref is None  # Verifies no product reference.
    assert result.confidence == 0.0  # Verifies zero confidence.
    assert result.matched_rule_type == NO_MATCH  # Verifies no-match type.


@pytest.mark.asyncio  # Marks test as async.
async def test_empty_input_returns_safe_no_match() -> None:  # Tests empty input.
    product_access: FakeProductAccess = FakeProductAccess()  # Creates fake product access.

    result = await normalize_product_name("   ", product_access)  # Normalizes whitespace input.

    assert result.normalized_name == ""  # Verifies stripped empty output.
    assert result.product_ref is None  # Verifies no product reference.
    assert result.confidence == 0.0  # Verifies zero confidence.
    assert result.matched_rule_type == NO_MATCH  # Verifies no-match type.


def test_rule_normalizer_has_no_forbidden_imports() -> None:  # Tests architecture boundary.
    source_text: str = Path("backend/normalizer/rule_normalizer.py").read_text(encoding="utf-8")  # Reads normalizer source.
    forbidden_tokens: list[str] = [  # Defines forbidden tokens.
        "motor",  # Blocks Motor import.
        "pymongo",  # Blocks PyMongo import.
        "normalization_rules",  # Blocks forbidden Phase 1 collection.
        "from backend.data_access",  # Blocks direct Data Access Layer import.
        "import backend.data_access",  # Blocks direct Data Access Layer package import.
        "from backend.dal",  # Blocks old DAL import.
        "import backend.dal",  # Blocks old DAL package import.
        "from fastapi",  # Blocks API route dependency.
        "import fastapi",  # Blocks FastAPI package dependency.
    ]  # Ends forbidden token list.

    for token in forbidden_tokens:  # Iterates forbidden tokens.
        assert token not in source_text  # Verifies forbidden token is absent.
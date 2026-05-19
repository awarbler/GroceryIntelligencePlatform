# =============================================================================
# File: normalizer/rule_normalizer.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Description: Implements a rule-based product name normalizer for mapping parsed item names to canonical product
# SRS Traceability: Supports SRS v5.0 Section 12 ET-003 and Section 13 HC-001 through HC-009.
# SDD Traceability: Supports SDD v5.0 Section 4 ETL Pipeline Design and Section 8 API Endpoint Design.
# =============================================================================
from __future__ import annotations  # Enables modern type hint behavior.

import re  # Imports regular expressions for text cleanup and tokenization.
from dataclasses import dataclass  # Imports dataclass for structured normalizer output.
from typing import Any, Protocol  # Imports protocol typing for dependency inversion.

from backend.parsers.heb.abbreviations import HEB_PRODUCT_SEEDS  # Imports HEB seed mappings.


NORMALIZER_VERSION: str = "rule-normalizer-v1.0"  # Stores normalizer version for traceability.
EXACT_CANONICAL_MATCH: str = "exact_canonical_name"  # Stores exact canonical match label.
EXACT_ALIAS_MATCH: str = "exact_alias"  # Stores exact alias match label.
PARTIAL_TOKEN_MATCH: str = "partial_token"  # Stores partial token match label.
NO_MATCH: str = "no_match"  # Stores no-match label.
EXACT_CONFIDENCE: float = 1.0  # Stores confidence for exact matches.
PARTIAL_CONFIDENCE: float = 0.70  # Stores confidence for partial token matches.
NO_MATCH_CONFIDENCE: float = 0.0  # Stores confidence for unmatched items.


class ProductDataAccessProtocol(Protocol):  # Defines the product access behavior the normalizer needs.
    async def find_all_products(self) -> list[dict[str, Any]]:  # Requires a method to retrieve product documents.
        ...  # Marks the protocol method as intentionally unimplemented.

    async def upsert_product_alias_seed(  # Requires a method to upsert alias seed mappings.
        self,  # Receives the product access object.
        canonical_name: str,  # Receives the canonical product name.
        aliases: list[str],  # Receives aliases to store in products.aliases[].
        brand: str | None,  # Receives optional brand metadata.
        category: str | None,  # Receives optional category metadata.
    ) -> None:  # Declares no return value.
        ...  # Marks the protocol method as intentionally unimplemented.


@dataclass(frozen=True)  # Makes normalization result immutable.
class NormalizationResult:  # Defines the output from one normalization lookup.
    raw_name: str  # Stores the original parsed item name.
    normalized_name: str  # Stores the canonical name or raw name when unmatched.
    product_ref: str | None  # Stores the product id when matched.
    confidence: float  # Stores the confidence score.
    matched_rule_type: str  # Stores the match type.
    normalizer_version: str = NORMALIZER_VERSION  # Stores normalizer version for traceability.


async def seed_heb_product_aliases(product_access: ProductDataAccessProtocol) -> int:  # Defines idempotent HEB alias seed function.
    seeded_count: int = 0  # Tracks how many seed records were processed.
    for seed in HEB_PRODUCT_SEEDS:  # Iterates through all HEB seed mappings.
        await product_access.upsert_product_alias_seed(  # Calls Data Access Layer through dependency injection.
            canonical_name=seed.canonical_name,  # Passes canonical product name.
            aliases=list(seed.aliases),  # Converts aliases tuple to list for storage.
            brand=seed.brand,  # Passes brand metadata.
            category=seed.category,  # Passes category metadata.
        )  # Ends seed upsert call.
        seeded_count += 1  # Counts the processed seed.
    return seeded_count  # Returns processed seed count.


async def normalize_product_name(raw_name: str, product_access: ProductDataAccessProtocol) -> NormalizationResult:  # Defines public normalizer function.
    cleaned_raw_name: str = raw_name.strip()  # Removes leading and trailing whitespace.
    if cleaned_raw_name == "":  # Checks for empty input.
        return _build_no_match(cleaned_raw_name)  # Returns safe no-match result.

    products: list[dict[str, Any]] = await product_access.find_all_products()  # Loads products through injected access object.

    exact_canonical_match: dict[str, Any] | None = _find_exact_canonical(cleaned_raw_name, products)  # Runs exact canonical lookup.
    if exact_canonical_match is not None:  # Checks if exact canonical match was found.
        return _build_match(cleaned_raw_name, exact_canonical_match, EXACT_CONFIDENCE, EXACT_CANONICAL_MATCH)  # Returns exact canonical result.

    exact_alias_match: dict[str, Any] | None = _find_exact_alias(cleaned_raw_name, products)  # Runs exact alias lookup.
    if exact_alias_match is not None:  # Checks if exact alias match was found.
        return _build_match(cleaned_raw_name, exact_alias_match, EXACT_CONFIDENCE, EXACT_ALIAS_MATCH)  # Returns exact alias result.

    partial_token_match: dict[str, Any] | None = _find_partial_token(cleaned_raw_name, products)  # Runs partial token lookup.
    if partial_token_match is not None:  # Checks if partial token match was found.
        return _build_match(cleaned_raw_name, partial_token_match, PARTIAL_CONFIDENCE, PARTIAL_TOKEN_MATCH)  # Returns partial token result.

    return _build_no_match(cleaned_raw_name)  # Returns no-match result when nothing matched.


def _find_exact_canonical(raw_name: str, products: list[dict[str, Any]]) -> dict[str, Any] | None:  # Defines exact canonical lookup helper.
    normalized_raw: str = _normalize_text(raw_name)  # Normalizes raw name.
    for product in products:  # Iterates over product documents.
        canonical_name: str = str(product.get("canonical_name", ""))  # Reads canonical name safely.
        if _normalize_text(canonical_name) == normalized_raw:  # Compares normalized canonical to normalized raw.
            return product  # Returns matched product.
    return None  # Returns no match.


def _find_exact_alias(raw_name: str, products: list[dict[str, Any]]) -> dict[str, Any] | None:  # Defines exact alias lookup helper.
    normalized_raw: str = _normalize_text(raw_name)  # Normalizes raw name.
    for product in products:  # Iterates over product documents.
        aliases: list[str] = [str(alias) for alias in product.get("aliases", [])]  # Reads aliases safely.
        for alias in aliases:  # Iterates over aliases.
            if _normalize_text(alias) == normalized_raw:  # Compares normalized alias to normalized raw.
                return product  # Returns matched product.
    return None  # Returns no match.


def _find_partial_token(raw_name: str, products: list[dict[str, Any]]) -> dict[str, Any] | None:  # Defines partial token lookup helper.
    raw_tokens: set[str] = _tokenize(raw_name)  # Tokenizes the raw name.
    best_product: dict[str, Any] | None = None  # Stores current best candidate.
    best_score: float = 0.0  # Stores current best score.
    for product in products:  # Iterates over product documents.
        candidate_names: list[str] = [str(product.get("canonical_name", ""))]  # Starts candidates with canonical name.
        candidate_names.extend(str(alias) for alias in product.get("aliases", []))  # Adds aliases as candidates.
        for candidate_name in candidate_names:  # Iterates over candidate names.
            candidate_tokens: set[str] = _tokenize(candidate_name)  # Tokenizes candidate name.
            score: float = _token_overlap_score(raw_tokens, candidate_tokens)  # Computes overlap score.
            if score > best_score:  # Checks whether this is the best score.
                best_score = score  # Saves the best score.
                best_product = product  # Saves the best product.
    if best_score >= 0.50:  # Requires at least half of raw tokens to overlap.
        return best_product  # Returns best product.
    return None  # Returns no partial match.


def _build_match(raw_name: str, product: dict[str, Any], confidence: float, matched_rule_type: str) -> NormalizationResult:  # Builds matched result.
    return NormalizationResult(  # Returns structured match output.
        raw_name=raw_name,  # Stores raw input.
        normalized_name=str(product.get("canonical_name", raw_name)),  # Stores canonical name.
        product_ref=_get_product_ref(product),  # Stores product reference.
        confidence=confidence,  # Stores confidence.
        matched_rule_type=matched_rule_type,  # Stores rule type.
    )  # Ends result construction.


def _build_no_match(raw_name: str) -> NormalizationResult:  # Builds no-match result.
    return NormalizationResult(  # Returns structured no-match output.
        raw_name=raw_name,  # Stores raw input.
        normalized_name=raw_name,  # Keeps raw name unchanged.
        product_ref=None,  # Stores no product reference.
        confidence=NO_MATCH_CONFIDENCE,  # Stores zero confidence.
        matched_rule_type=NO_MATCH,  # Stores no-match rule type.
    )  # Ends result construction.


def _get_product_ref(product: dict[str, Any]) -> str | None:  # Reads product identifier.
    product_id: Any = product.get("_id", product.get("id"))  # Reads Mongo-style _id first, then id.
    if product_id is None:  # Checks whether no id exists.
        return None  # Returns no product reference.
    return str(product_id)  # Converts product id to string.


def _normalize_text(value: str) -> str:  # Normalizes text for exact comparison.
    lowered: str = value.lower()  # Lowercases text.
    replaced: str = re.sub(r"[^a-z0-9]+", " ", lowered)  # Converts punctuation to spaces.
    collapsed: str = re.sub(r"\s+", " ", replaced).strip()  # Collapses repeated spaces.
    return collapsed  # Returns normalized text.


def _tokenize(value: str) -> set[str]:  # Tokenizes text for partial matching.
    normalized: str = _normalize_text(value)  # Normalizes text first.
    tokens: set[str] = set(normalized.split())  # Splits normalized text into tokens.
    return {token for token in tokens if len(token) > 1}  # Removes one-character tokens.


def _token_overlap_score(raw_tokens: set[str], candidate_tokens: set[str]) -> float:  # Computes token overlap score.
    if not raw_tokens or not candidate_tokens:  # Checks for empty token sets.
        return 0.0  # Returns zero score.
    overlap_count: int = len(raw_tokens.intersection(candidate_tokens))  # Counts shared tokens.
    return overlap_count / len(raw_tokens)  # Returns fraction of raw tokens found.
# Source Note — P1-09 Stage 2B Product Normalization Using Product Aliases

## Change

Added Stage 2B product normalization for H-E-B online receipt parsed item names.

## Reason

Parsed item names from P1-08 must be mapped to canonical product names before correction review, deal matching, and later reporting.

## Real Receipt Format Impact

P1-08 was corrected to parse real H-E-B exported receipt item lines such as:

`Item, Mission 25 Calories Yellow Corn Tortillas, 30 ct. Quantity: 1 each. Price: $3.13.`

Because of that correction, P1-09 seed aliases use real H-E-B online receipt product names instead of artificial parser-only names.

## Implementation Rule

The normalizer:

- Uses `backend/normalizer/rule_normalizer.py`.
- Uses `backend/parsers/heb/abbreviations.py`.
- Seeds at least 30 H-E-B product alias mappings.
- Uses `products.aliases[]` on product documents.
- Looks up products through an injected product access object.
- Returns `normalized_name`, `product_ref`, `confidence`, `matched_rule_type`, and `normalizer_version`.

## Lookup Order

1. Exact `canonical_name` match.
2. Exact alias match inside `products.aliases[]`.
3. Partial token match across `canonical_name` and aliases.
4. No match returns raw name unchanged with confidence `0.0`.

## Not Allowed in Phase 1 Normalization

- Creating a separate `normalization_rules` collection.
- ML normalization.
- Direct MongoDB writes from the normalizer.
- Motor or pymongo imports in the normalizer.
- API route logic.
- Direct service imports.

## SRS Support

- SRS Section 12 / ET-002: Stage 2 runs the store-specific parser and normalization step.
- SRS Section 14 / PN-001 through PN-005: Product normalization requirements.
- SRS Section 18 / MI-001 through MI-004: My Items requirements.
- SRS Section 19: Product collection.
- SRS Section 20 / TS-001 and TS-002: Tests cover valid, malformed, and edge cases.

## SDD Support

- SDD Section 4: ETL Stage 2 Transform.
- SDD Section 5.1: H-E-B abbreviation table.
- SDD Section 7.3: Products canonical product catalog.

## GitHub Issue

P1-09 / #14

## Traceability Impact

Confirms that Phase 1 normalization uses canonical products plus `products.aliases[]` instead of a separate normalization rules collection.

## Testing Impact

Tests verify:

- H-E-B seed has at least 30 mappings.
- Seed is idempotent.
- Exact canonical match works.
- Exact alias match works.
- Partial token match works.
- No match returns raw name and confidence `0.0`.
- Empty input returns safe no-match result.
- No forbidden Motor, pymongo, FastAPI, direct Data Access Layer, old DAL, or `normalization_rules` usage exists in the normalizer.

## Scope

Current Phase 1 scope.
# Sample Data Policy

This project must not commit real personal receipt data, account data, payment data, address data, or store account data.

## Rules

Committed fixtures must be synthetic or anonymized.

Do not commit:

- Real receipt PDFs
- Real copied receipt text
- Real screenshots
- Real delivery addresses
- Real order numbers
- Real payment card details
- Real account identifiers
- Real loyalty identifiers
- Real barcodes
- Real store transaction identifiers

Remove or replace the following before committing any fixture:

- Personal names
- Home addresses
- Delivery addresses
- Billing addresses
- Phone numbers
- Email addresses
- Payment card details
- Account identifiers
- Store account identifiers
- Loyalty account identifiers
- Real order identifiers
- Real barcode values
- Real delivery notes

## Allowed

Synthetic test data is allowed when it is clearly fake and used only for tests.

Examples:

- `HEB-TEST-1001`
- `HEB Curbside Test Store`
- `123 Test Address`
- `Test City, TX 00000`
- `Visa TEST`
- Synthetic item names
- Synthetic prices
- Synthetic dates
- Synthetic totals
- Synthetic substitution examples

## H-E-B Online Receipt Fixture Format

H-E-B online receipt fixtures should preserve the real parser structure without preserving real private values.

Allowed structural examples:

```text
Item, <name>. Quantity: <number> <unit>. Price: $<amount>.
Out of stock
Substituted with
Subtotal $<amount>
Delivery fee $<amount>
Tax $<amount>
Driver tip $<amount>
Total $<amount>
Your savings -$<amount>
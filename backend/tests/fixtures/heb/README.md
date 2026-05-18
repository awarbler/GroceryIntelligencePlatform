# HEB Fixture Privacy README

This folder contains synthetic or anonymized HEB online receipt fixture text for parser tests.

The fixtures must match the real H-E-B online receipt export/copy-paste structure, but they must not contain real personal receipt data.

Do not commit real H-E-B receipt PDFs, real copied receipt text, screenshots, addresses, order numbers, payment details, or account details.

Before committing any fixture, remove or replace:

- Personal names
- Delivery addresses
- Billing addresses
- Phone numbers
- Email addresses
- Payment card details
- Account identifiers
- Loyalty account identifiers
- Real order identifiers
- Real store transaction identifiers
- Real barcode values
- Real delivery notes
- Real account header text

Allowed fixture content:

- Synthetic order numbers, such as `HEB-TEST-1001`
- Synthetic addresses, such as `123 Test Address`
- Synthetic store names, such as `HEB Curbside Test Store`
- Synthetic item names
- Synthetic prices
- Synthetic dates
- Synthetic totals
- Synthetic substitution examples
- Realistic H-E-B parser structure using lines like:
  - `Item, <name>. Quantity: <number> <unit>. Price: $<amount>.`
  - `Out of stock`
  - `Substituted with`
  - `Subtotal $<amount>`
  - `Delivery fee $<amount>`
  - `Tax $<amount>`
  - `Driver tip $<amount>`
  - `Total $<amount>`

Purpose:

These fixtures support P1-08 parser tests without exposing private receipt, payment, account, or address information.
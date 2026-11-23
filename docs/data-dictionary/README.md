# Data Dictionary

## Implemented models

### Bronze (Parquet)
- `hm_sample/articles` — product catalog (5,000 rows).
- `hm_sample/customers` — customer attributes (1,100 rows).
- `hm_sample/transactions` — purchase transactions (15,773 rows).
- `uci/transactions_year_2009-2010`, `transactions_year_2010-2011` — UCI retail lines.

### Silver (Parquet)
- `hm_articles` — normalized articles (article_id zero-padded to 10 digits).
- `hm_customers` — normalized customers (missingness flags).
- `hm_transactions` — validated transactions (price >= 0, exact duplicates collapsed).
- `uci_transactions` — UCI lines with cancellation/return flags.

### Gold (Parquet)
- `hm_daily_product_demand` — daily aggregates per article.
- `hm_product_velocity` — sales velocity per article.
- `uci_daily_product_demand` — daily aggregates per stock code/country.
- `synthetic_warehouses`, `synthetic_suppliers`, `synthetic_inventory_snapshots`,
  `synthetic_purchase_orders`, `synthetic_stock_adjustments`.

### dbt models
- Staging views: `stg_hm_articles`, `stg_hm_transactions`, `stg_uci_transactions`.
- Mart table: `fct_hm_daily_demand`.

## Identifiers
- `article_id` (H&M): 10-digit zero-padded string.
- `customer_id` (H&M): hashed hex string.
- `stock_code`, `invoice_no` (UCI): strings.
- Synthetic IDs: `WHxx`, `SUPxxx`, `POxxxx`.
- Source-specific identifiers are never mixed (ADR-0003).

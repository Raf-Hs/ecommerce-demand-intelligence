# Data Dictionary — initial entity list (Phase 0)

To be expanded per layer as models are implemented.

## Dimensions
- **DimDate** — calendar date, holiday flags, weekend, month, quarter, year.
- **DimProduct** — article attributes (type, group, colour, department, index, section, garment group).
- **DimCustomer** — customer attributes (age band, club status, news frequency, postal code).
- **DimWarehouse** — warehouse (synthetic).
- **DimSupplier** — supplier with lead-time distribution (synthetic).

## Facts
- **FactSalesTransactions** — one row per transaction line (H&M + optional UCI).
- **FactDailyProductDemand** — daily aggregates per article.
- **FactInventorySnapshots** — daily stock per article/warehouse (synthetic).
- **FactPurchaseOrders** — PO lines (synthetic).
- **FactStockAdjustments** — shrinkage/damage (synthetic).

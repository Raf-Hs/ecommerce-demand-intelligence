# Phase 0 — Research and Architecture Report

**Project:** E-commerce Inventory & Demand Intelligence Platform
**Phase:** 0 — Research and Architecture
**Status:** Draft for review (awaiting approval before Phase 1 implementation)

---

## 0. Executive summary

This report documents the Phase 0 investigation: source datasets, verified schemas, data-quality
risks, additional source recommendations, synthetic operational data design, the proposed
architecture, technology decisions, and the initial repository layout.

Key conclusions:

1. The **H&M Personalized Fashion Recommendations** dataset is the primary real source. Its
   official files are `transactions_train.csv`, `customers.csv`, `articles.csv` (plus images).
   Official row counts: ~31.8M transactions, ~1.37M customers, ~105.5k articles. Date range:
   2018-09-20 to 2020-09-22.
2. The dataset is **not present in this repository**. A small public derived sample
   (`jamescalam/hm-sample`, 5,000 articles / 1,100 customers / 15,773 transactions) was
   downloaded and profiled to verify schema and data-quality patterns. All findings from that
   sample are labelled as **sample-verified** and must be re-validated on the full data.
3. The dataset has **real, non-trivial data-quality issues**: NaN-encoded missingness, empty
   strings, integer-encoded article IDs that lose leading zeros, repeated purchase rows that
   are legitimate, and a highly skewed postal-code distribution.
4. **Additional real source (recommended):** Python `holidays` library for a calendar/holiday
   dimension, plus optionally UCI Online Retail II as a second transaction source for
   multi-source ingestion validation.
5. **Synthetic operational data is required** for inventory, purchase orders, suppliers and
   warehouses; it must be clearly labelled as synthetic.
6. Proposed architecture: **Medallion (Bronze/Silver/Gold)** data lake on local filesystem
   (Parquet), Pandas for profiling, PySpark for large-scale processing, Airflow for
   orchestration, PostgreSQL as serving layer.

---

## 1. Source inventory

### 1.1 Primary source — H&M Personalized Fashion Recommendations (real)

| Attribute | Value | Status |
|---|---|---|
| Source | Kaggle competition: `h-and-m-personalized-fashion-recommendations` | Verified (public page) |
| URL | https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data | Verified |
| License / terms | Competition rules; data free for non-commercial use; must accept terms on Kaggle | Verified |
| Files | `transactions_train.csv`, `customers.csv`, `articles.csv`, image archive | Verified |
| transactions_train rows | ~31.8M (documented) | Verified (public) |
| customers rows | ~1.37M (documented) | Verified (public) |
| articles rows | ~105,542 (documented) | Verified (public; microsoft/hnm mirror reports 105,542 rows, 25 cols) |
| Transaction date range | 2018-09-20 to 2020-09-22 | Verified (public) |
| Prediction horizon | 2020-09-23 to 2020-09-29 | Verified (public) |
| Sales channels | 1 = online, 2 = store (inferred from notebooks) | Assumption (to verify) |

### 1.2 transactions_train.csv schema (verified from public notebooks/docs)

| Column | Type (as read) | Notes |
|---|---|---|
| t_dat | string/date | Purchase date. Parse as date. |
| customer_id | string (hex) | Hashed customer identifier. |
| article_id | string (10-digit, zero-padded) | **Must be read as string and zero-padded to 10 digits.** Reading as int loses leading zeros. |
| price | float | Normalised price (0..1 range observed). |
| sales_channel_id | int | 1 or 2. |

### 1.3 customers.csv schema (verified)

| Column | Type | Notes |
|---|---|---|
| customer_id | string (hex) | PK. |
| FN | float (0/1/NaN) | Newsletter flag. Missing encoded as NaN. |
| Active | float (0/1/NaN) | Active flag. Missing encoded as NaN. |
| club_member_status | string | ACTIVE / PRE-CREATE / empty (missing). |
| fashion_news_frequency | string | NONE / Regularly / Monthly / empty (missing). |
| age | float | 17..87 observed; some NaN. |
| postal_code | string (hex) | Hashed. Highly skewed (one code ~120k customers in full data). |

### 1.4 articles.csv schema (verified, 25 columns)

| Column | Type | Notes |
|---|---|---|
| article_id | int/string | 10-digit zero-padded ID. |
| product_code | int | First 6-7 digits of article_id (product family). |
| prod_name | string | Product name. |
| product_type_no | int | |
| product_type_name | string | 131 distinct. |
| product_group_name | string | 19 distinct. |
| graphical_appearance_no | int | |
| graphical_appearance_name | string | 30 distinct. |
| colour_group_code | int | |
| colour_group_name | string | 50 distinct. |
| perceived_colour_value_id | int | |
| perceived_colour_value_name | string | 8 distinct. |
| perceived_colour_master_id | int | |
| perceived_colour_master_name | string | 20 distinct. |
| department_no | int | |
| department_name | string | 299 distinct. |
| index_code | string | 10 distinct. |
| index_name | string | 10 distinct. |
| index_group_no | int | |
| index_group_name | string | 5 distinct. |
| section_no | int | |
| section_name | string | 56 distinct. |
| garment_group_no | int | |
| garment_group_name | string | 21 distinct. |
| detail_desc | string | Free text; ~43k distinct; some empty. |

### 1.5 Additional real source — Calendar / holidays (recommended)

- **Source:** Python `holidays` library (https://github.com/vacanza/python-holidays) plus an optional curated CSV of country holidays.
- **License:** MIT.
- **Schema:** `date`, `is_holiday`, `holiday_name`, `country_code`.
- **Size:** derived; ~730 dates for the H&M range.
- **Reason:** Demand seasonality and holiday effects. Joined to the date dimension on `date`. Defensible and low-cost.
- **Caveat:** H&M transactions carry no country; holiday flags will be based on a chosen primary market (e.g. Sweden) plus generic weekend/payday flags. Document this limitation.

### 1.6 Additional real source — UCI Online Retail II (recommended, optional)

- **Source:** UCI ML Repository — Online Retail II.
- **URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **License:** CC BY 4.0.
- **Schema:** `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country`.
- **Size:** ~1.07M rows, 8 columns, 2009-2011.
- **Reason:** Demonstrates multi-source ingestion and schema standardisation on a second, heterogeneous retail transaction source; useful for validating the Bronze/Silver contracts. Joinability with H&M is **none** (different products/customers); it is treated as a separate `source_system` in the unified fact sales model.
- **Decision:** Optional. Include only if approved; otherwise keep scope to H&M + calendar + synthetic ops.

### 1.7 Additional real source — Favorita (Store Sales, large-scale retail) (recommended)

- **Source:** Kaggle competition "Store Sales — Time Series Forecasting" (Corporación Favorita).
- **URL:** https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data
- **License / terms:** Competition rules; accept terms on Kaggle.
- **Key files:** `train.csv`, `stores.csv`, `items.csv`, `transactions.csv`, `oil.csv`, `holidays_events.csv`.
- **Approx size:** `train.csv` ~3M rows (2013-2017), plus store/item dimensions.
- **Reason:** Large-scale retail demand dataset used as the **benchmark dataset** for the
  DuckDB vs PySpark comparative benchmark, and as a second retail demand source. Provides
  store/item/transactions/oil/holidays — useful for calendar and replenishment modelling.
- **Joinability:** None with H&M (different retailers/products/customers). Treated as a
  separate `source_system = 'favorita'` in the unified fact model. Never fabricate relationships.
- **Decision:** Include as approved (per user). Download required in Phase 1/3.

### 1.8 Rejected / not recommended

- Unrelated datasets added only to increase source count — rejected.
- Weather data — deferred (external dependency, weak join).

---

## 2. Data-quality risk assessment (H&M)

### 2.1 Verified on the full documented dataset (public sources)

- ~31.8M transaction rows, ~1.37M customers, ~105.5k articles.
- Transaction prices are normalised to a 0..1 range (not currency).
- Article IDs are 10-digit zero-padded strings; many notebooks read them as strings to preserve leading zeros.
- Customer `postal_code` is highly skewed (one code holds ~120k customers in full data) — possible encoded missing/DC.
- `detail_desc` has ~43k distinct values and some empties.

### 2.2 Sample-verified (jamescalam/hm-sample, 5k articles / 1.1k customers / 15.8k txns)

| Check | Result | Implication |
|---|---|---|
| Article nulls | 0 in sample | Full data may differ; validate. |
| Customer nulls (JSON null) | 0 | Missingness is encoded as NaN/empty, not null. |
| FN / Active missing | ~57% NaN | Treat NaN as "false/unknown", not drop. |
| club_member_status empty | 4 rows | Convert empty string to NULL/unknown. |
| fashion_news_frequency empty | 4 rows | Same. |
| age NaN | 5 rows | Impute or flag. |
| age range | 17..87 | Validate bounds. |
| article_id leading-zero loss | present (min 9 digits) | **Critical:** read as string + zero-pad to 10. |
| article_id // 10 != product_code | confirmed | article_id = product_code*1000 + variant suffix. |
| Exact full-row duplicate txns | 2,670 extra rows (~17%) | Do not dedup blindly; investigate. |
| Same cust-art-date groups >1 row | 2,224 | Repeated purchases are legitimate. |
| Groups differing in price/channel | 161 | Indicates multiple line items / intraday price change. |
| Cust-art pairs across >1 date | 1,005 | Repeat purchases over time (legitimate). |
| Referential integrity (sample) | 0 violations | Full data must be re-checked. |
| detail_desc empty | 20 | Handle as missing text. |
| Postal code skew | top code 37/1100 (~3.4%) | Skew confirmed at small scale. |

### 2.3 Handling rules (to be implemented in Silver)

1. **Never silently discard.** Rejected rows go to a quarantine table with reason codes.
2. Missing `FN`/`Active` (NaN) → `false` + `is_fn_known` flag (or keep NaN as explicit unknown). Decision to be documented.
3. Empty `club_member_status` / `fashion_news_frequency` → NULL with an `is_unknown` flag.
4. `article_id` → read as string, `zfill(10)`. Reject rows that cannot be normalised to 10 digits.
5. `age` → validate [0, 120]; out-of-range → NULL + flag.
6. Price → validate >= 0; null/invalid → quarantine.
7. Duplicate transaction rows → keep as separate line items unless exact full-row duplicates are confirmed as ingestion duplicates; define rule in Silver (recommend: collapse exact full-row duplicates, keep repeated purchases).
8. Referential integrity violations → quarantine with reason `orphan_customer` / `orphan_article`.

---

## 3. Synthetic operational data design

The H&M dataset contains no inventory, orders, suppliers, or warehouses. These are required for the
demand/integration story and will be **synthetic, clearly labelled**.

| Entity | Type | Grain | Generation rule (high level) |
|---|---|---|---|
| dim_warehouse | dimension | warehouse | 5-20 warehouses with location, capacity. |
| dim_supplier | dimension | supplier | N suppliers with lead-time distribution. |
| fact_inventory_snapshot | fact | article x warehouse x day | Opening stock = recent sales velocity * cover target + noise; decremented by sales; replenished by POs. |
| fact_purchase_order | fact | PO line | Triggered when stock < reorder point; lead time from supplier distribution. |
| fact_stock_adjustment | fact | adjustment | Random shrinkage/damage events at low rate. |

Rules:
- Every synthetic row carries `source_system = 'synthetic_ops'` and `is_synthetic = true`.
- Generation is deterministic given a seed and documented parameters.
- Inject controlled data-quality issues (nulls, duplicates, late arrivals) to test validation.
- Never present as real company data.

---

## 4. Proposed architecture

### 4.1 Logical layers (Medallion)

```
Source Systems
   H&M CSVs | Calendar (holidays) | Synthetic ops
        |
        v
Ingestion (schema validation, metadata capture, raw preservation)
        |
        v
Bronze (raw, append-only, with ingestion metadata, Parquet)
        |
        v
Silver (cleaned, standardised, validated, quarantined rejects, Parquet)
        |
        v
Gold (dimensional model: facts + dims, Parquet + PostgreSQL serving)
        |
        v
Consumption (demand analysis, inventory coverage, replenishment)
```

### 4.2 Storage

- Data lake on local filesystem under `data/{raw,bronze,silver,gold}`.
- Parquet (Snappy) with partitioning by date/source.
- PostgreSQL as serving layer for Gold (optional, Phase 4+).

### 4.3 Processing

- **Primary analytical engine: DuckDB.** Used for Silver/Gold transformations, aggregations,
  and analytics on the local data lake (Parquet). Chosen for simplicity, speed, and SQL ergonomics.
- **PySpark: planned, not mandatory initially.** Included in the stack and introduced via a
  comparative benchmark (DuckDB vs PySpark) on the Favorita dataset before any pipeline depends
  on distributed processing. Adoption requires a measured, documented benefit.
- Pandas + PyArrow for profiling and small transforms.
- Chunked Pandas only where neither DuckDB nor Spark is justified; measure both.

### 4.4 Orchestration

- Apache Airflow (Docker Compose) with DAGs per layer, retries, backfills, incremental runs.

### 4.5 Data quality

- Custom validation module + pandera (Pandas) / Spark-native checks.
- Quarantine tables with reason codes.
- Data-quality report per stage (counts: total/accepted/rejected/corrected).

---

## 5. Technology decisions

| Capability | Choice | Rationale |
|---|---|---|
| Language | Python 3.11 via pyenv (WSL Ubuntu) | Spark/Airflow compatibility; isolated venv. WSL currently has 3.14 (too new). |
| Data processing (primary) | DuckDB | Fast local analytical engine over Parquet; SQL ergonomics. |
| Data processing (distributed, planned) | PySpark 3.5 | Benchmark vs DuckDB on Favorita before mandatory use. |
| Transformations | dbt Core + dbt-duckdb | SQL models, tests, lineage for Silver/Gold. |
| Storage format | Parquet (Snappy) | Columnar, compressed, partition pruning. |
| Orchestration | Apache Airflow 2.9 | DAGs, retries, backfills. |
| Serving DB | PostgreSQL 15 | Gold consumption + Airflow/metadata. |
| Data quality | pandera + dbt tests + custom | Lightweight; escalate if needed. |
| Testing | pytest + pytest-cov | Standard. |
| Infra | Docker Compose (local only) | Reproducible local; no paid cloud. |
| Config | pydantic-settings + .env | Typed config. |
| Logging | structlog | Structured logs. |
| CI | GitHub Actions | Lint + tests. |
| Holidays | python-holidays | Calendar dimension. |

---

## 6. Data dictionary (initial)

See `docs/data-dictionary/`. To be expanded per layer. Initial entity list:
DimDate, DimProduct, DimCustomer, DimWarehouse, DimSupplier, FactSalesTransactions,
FactDailyProductDemand, FactInventorySnapshots, FactPurchaseOrders, FactStockAdjustments.

---

## 7. Initial repository structure

(As created; see tree.)

```
ecommerce-demand-intelligence/
├── data/{raw,bronze,silver,gold,samples}
├── docs/{architecture,data-dictionary,data-quality,decisions}
├── infrastructure/
├── src/{ingestion,validation,transformation,processing,storage,utils}
├── dags/
├── dbt/
├── tests/
├── scripts/
├── docker-compose.yml (to add Phase 1)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 8. Risks and open questions

1. H&M and Favorita datasets not yet downloaded (no Kaggle credentials). Phase 1 ingestion depends on them.
2. Python 3.11 provisioning via pyenv in WSL — to be done in Phase 1.
3. DuckDB vs PySpark benchmark on Favorita — to be designed in Phase 3/6.
4. Holiday market (Sweden vs others) is an assumption to validate/document.
5. Price is normalised (0..1), not currency — affects monetary KPIs; document.
6. Favorita and UCI have no join path to H&M; maintain `source_system` and never fabricate relationships.

---

## 9. Approval gate

Phase 0 updated per user decisions. ADRs recorded in `docs/decisions/`.

Confirmed decisions:
- [x] Medallion architecture (Bronze/Silver/Gold).
- [x] Parquet data lake.
- [x] DuckDB primary analytical engine.
- [x] PostgreSQL for operational/Airflow metadata.
- [x] Airflow orchestration.
- [x] dbt Core transformations.
- [x] PySpark planned + DuckDB vs PySpark benchmark on Favorita.
- [x] Sources: H&M (primary), UCI Online Retail II (secondary), Favorita (benchmark/large-scale).
- [x] Python 3.11 via pyenv in WSL2 with isolated venv.
- [x] Local only, Docker Compose, no paid cloud.
- [ ] H&M + Favorita + UCI data downloaded into `data/raw/`.

Open: provide Kaggle credentials or download data. Then proceed to Phase 1.

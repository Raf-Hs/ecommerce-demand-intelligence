# Decision 0001 — Phase 0 source selection and architecture

- **Date:** Phase 0
- **Status:** Accepted (implemented in Phases 1+)

## Context
Need a primary real dataset, optional secondary real dataset, calendar source, and synthetic
operational data to support demand + inventory analytics.

## Decisions
1. Primary source: H&M Personalized Fashion Recommendations (Kaggle).
2. Calendar source: Python `holidays` library.
3. Optional secondary transaction source: UCI Online Retail II (pending approval).
4. Synthetic operational data: inventory snapshots, POs, suppliers, warehouses, adjustments
   (clearly labelled synthetic).
5. Architecture: Medallion data lake (Parquet) + PySpark + Airflow + PostgreSQL serving.
6. Data quality: quarantine with reason codes; never silently discard.

## Consequences
- UCI Online Retail II ingested and processed (not optional anymore).
- H&M full dataset pending Kaggle credentials; sample used for development.
- Python 3.11 provisioned via pyenv (WSL now 3.14 system, 3.11 project).

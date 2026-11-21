# Technical Interview Guide

Practical study guide based on the real implementation. Each question references
source evidence.

## A. Architecture questions

**Q1. Describe the overall architecture.**
Strong answer: Medallion (Bronze/Silver/Gold) data lake on local filesystem (Parquet),
DuckDB primary analytical engine, PySpark planned, dbt for SQL transforms, Airflow
orchestration, PostgreSQL serving, Docker Compose infra.
Evidence: `docs/phase0-report.md`, `README.md`, `src/transformation/`.

**Q2. Why Medallion architecture?**
Strong answer: separation of concerns — preserve raw, standardize/clean, then model
analytics; enables reprocessing and lineage.
Evidence: `docs/decisions/0001-phase0-sources.md`.

**Q3. How does data flow from source to Gold?**
Strong answer: source → ingestion → Bronze Parquet with metadata → Silver (DuckDB)
→ Gold (DuckDB) → dbt marts.
Evidence: `scripts/run_ingestion.py`, `src/transformation/silver.py`,
`src/transformation/gold.py`, `dbt/models/`.

## B. Data Engineering questions

**Q4. How is ingestion implemented?**
Strong answer: source-specific readers, schema handling, metadata columns, Parquet output.
Evidence: `src/ingestion/base.py`, `src/ingestion/hm_sample.py`, `src/ingestion/uci.py`.

**Q5. How are data quality issues handled?**
Strong answer: NaN/empty normalization, zero-padded IDs, cancellation/return flags,
exact-duplicate collapse, quarantine approach documented.
Evidence: `src/transformation/silver.py`, `docs/phase0-report.md` §2.

**Q6. Why Parquet?**
Strong answer: columnar, compressed, partition pruning, Arrow interoperability.
Evidence: `docs/decisions/`, `requirements.txt`.

**Q7. How is idempotency addressed?**
Strong answer: Bronze writes are deterministic per source; Silver/Gold regenerate from
Bronze. Not fully tested for concurrent runs.
Evidence: `src/transformation/silver.py` (COPY ... TO).

## C. SQL and analytical modeling questions

**Q8. How are identifiers handled across sources?**
Strong answer: source-specific IDs preserved; never mixed across H&M and UCI.
Evidence: `src/transformation/silver.py`, ADR-0003.

**Q9. What Gold models exist?**
Strong answer: daily product demand, product velocity, UCI daily demand, synthetic
inventory snapshots/POs/adjustments.
Evidence: `src/transformation/gold.py`, `src/transformation/synthetic_inventory.py`.

**Q10. How does dbt fit?**
Strong answer: staging views + mart table, tests, lineage, DuckDB adapter.
Evidence: `dbt/models/`, `dbt/models/schema.yml`.

## D. Distributed processing questions

**Q11. DuckDB vs PySpark — what did the benchmark show?**
Strong answer: DuckDB 0.36s vs PySpark 24.17s on ~1.07M rows (ratio 66x) in local mode;
JVM startup dominates. Conclusion: DuckDB primary, Spark for larger/cluster workloads.
Evidence: `docs/benchmarks/duckdb_vs_spark.md`, `scripts/benchmark_duckdb_vs_spark.py`.

**Q12. Is Spark production-ready here?**
Strong answer: No — planned, benchmarked only, not used in pipelines.
Evidence: ADR-0002, `docs/PROJECT_STATUS.md`.

## E. Reliability and orchestration questions

**Q13. How is the pipeline orchestrated?**
Strong answer: Airflow DAG with ingest → silver → gold/synthetic, retries configured.
Evidence: `dags/ecommerce_demand_pipeline.py`.

**Q14. Is the DAG deployed?**
Strong answer: No — defined in code only; not executed in an Airflow runtime.
Evidence: `docs/PROJECT_STATUS.md`.

**Q15. What testing exists?**
Strong answer: pytest smoke tests (2), dbt tests (6), ruff lint. No integration tests
for full pipeline yet.
Evidence: `tests/test_environment.py`, dbt build output.

**Q16. How is configuration managed?**
Strong answer: pydantic-settings + `.env` (never committed).
Evidence: `src/utils/config.py`, `.env.example`.

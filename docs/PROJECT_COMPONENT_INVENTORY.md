# Project Component Inventory

Inventory of actual repository components. Status values: Implemented, Tested, Configured, Planned.

| Component | File path | Responsibility | Status | Validation evidence |
|---|---|---|---|---|
| Project config (Python version) | `.python-version` | Pins Python 3.11.9 via pyenv | Implemented | `python --version` = 3.11.9 |
| Runtime dependencies | `requirements.txt` | Core runtime deps + optional sections | Implemented | pip install success |
| Dev dependencies | `requirements-dev.txt` | pytest, pytest-cov, ruff | Implemented | pip install success |
| Env template | `.env.example` | Configuration template, no secrets | Implemented | Reviewed |
| Git ignore | `.gitignore` | Excludes data, venv, secrets, caches | Implemented | git status clean |
| Ingestion base | `src/ingestion/base.py` | Bronze writer with metadata | Implemented | run_ingestion.py |
| H&M sample ingestion | `src/ingestion/hm_sample.py` | Ingest sample JSONL to Bronze | Implemented | Bronze parquet created |
| UCI ingestion | `src/ingestion/uci.py` | Ingest UCI xlsx to Bronze | Implemented | Bronze parquet created |
| Ingestion runner | `scripts/run_ingestion.py` | Orchestrate all ingestions | Implemented | Executed successfully |
| Silver transforms | `src/transformation/silver.py` | DuckDB Silver standardization | Implemented | Executed successfully |
| Gold transforms | `src/transformation/gold.py` | DuckDB Gold aggregations | Implemented | Executed successfully |
| Synthetic inventory | `src/transformation/synthetic_inventory.py` | Generate synthetic ops data | Implemented | Executed successfully |
| Config | `src/utils/config.py` | pydantic-settings config | Implemented | Imported in tests |
| Logging | `src/utils/logging.py` | structlog configuration | Implemented | Used in pipelines |
| dbt project | `dbt/dbt_project.yml` | dbt project config | Configured | dbt debug OK |
| dbt profiles | `dbt/profiles.yml` | DuckDB connection | Configured | dbt debug OK |
| dbt staging articles | `dbt/models/staging/stg_hm_articles.sql` | Staging view | Implemented | dbt build pass |
| dbt staging transactions | `dbt/models/staging/stg_hm_transactions.sql` | Staging view | Implemented | dbt build pass |
| dbt staging UCI | `dbt/models/staging/stg_uci_transactions.sql` | Staging view | Implemented | dbt build pass |
| dbt mart demand | `dbt/models/marts/fct_hm_daily_demand.sql` | Mart table | Implemented | dbt build pass |
| dbt schema tests | `dbt/models/schema.yml` | 6 data tests | Implemented | dbt build pass (6/6) |
| Airflow DAG | `dags/ecommerce_demand_pipeline.py` | Pipeline orchestration DAG | Implemented (not deployed) | Not executed |
| Docker Compose | `infrastructure/docker-compose.yml` | PostgreSQL 15 service | Configured | Container healthy |
| Infra docs | `infrastructure/README.md` | Startup/shutdown/verification | Implemented | Reviewed |
| CI workflow | `.github/workflows/ci.yml` | Lint + tests on push/PR | Configured | Not executed (no push yet at audit; now pushed) |
| Environment test | `tests/test_environment.py` | Smoke tests (2) | Tested | pytest 2/2 pass |
| Profile H&M sample | `scripts/profile_hm_sample.py` | Schema/data-quality profiling | Implemented | Executed |
| Profile UCI | `scripts/profile_uci.py` | UCI profiling | Implemented | Executed |
| Benchmark | `scripts/benchmark_duckdb_vs_spark.py` | DuckDB vs PySpark benchmark | Implemented | Executed (0.36s vs 24.17s) |
| Benchmark report | `docs/benchmarks/duckdb_vs_spark.md` | Benchmark documentation | Implemented | Reviewed |
| Benchmark raw | `docs/benchmarks/duckdb_vs_spark.txt` | Raw benchmark numbers | Implemented | Reviewed |
| Setup guide | `docs/setup.md` | Environment setup | Implemented | Reviewed |
| Phase 0 report | `docs/phase0-report.md` | Research report | Implemented | Reviewed |
| ADRs | `docs/decisions/0001–0006` | Architecture decisions | Implemented | Reviewed |
| Data dictionary | `docs/data-dictionary/README.md` | Entity list | Implemented | Reviewed |
| README | `README.md` | Portfolio documentation | Implemented | Reviewed |
| GitHub publish helper | `scripts/publish_github.sh` | Publish to GitHub | Implemented | Executed successfully |

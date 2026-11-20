# E-commerce Inventory & Demand Intelligence Platform

Production-oriented data engineering platform integrating large, messy, multi-source retail data
(H&M transactions, calendar/holidays, and synthetic operational systems) into a Medallion
(Bronze/Silver/Gold) data lake supporting demand analysis and inventory planning.

> Status: **Phase 0 — Research and Architecture** (awaiting approval). See `docs/phase0-report.md`.

## Highlights (planned)

- Multi-source ingestion of ~31.8M real H&M transactions, plus UCI Online Retail II and Favorita.
- Medallion architecture on a local data lake (Parquet), DuckDB (primary) with PySpark benchmark.
- dbt Core transformations, Airflow orchestration, PostgreSQL serving layer.
- Data quality framework with quarantine and reason codes.
- pytest, Docker Compose, GitHub Actions.

## Repository layout

See `docs/phase0-report.md` §7.

## Getting started (Phase 0)

1. Read `docs/phase0-report.md`.
2. Review and approve the architecture and open questions.
3. Provide the H&M dataset (see below) or Kaggle credentials.

### Data (not committed)

Raw and generated data are gitignored. Place the H&M files under `data/raw/hm/`:

```
data/raw/hm/
├── transactions_train.csv
├── customers.csv
└── articles.csv
```

A small public derived sample is available at `data/samples/hm_sample/` for schema verification
(not the official dataset).

### Profile the sample

```bash
python scripts/profile_hm_sample.py
```

## License

Code: MIT (to be confirmed). Data: H&M Kaggle competition terms (non-commercial, accept terms on Kaggle).

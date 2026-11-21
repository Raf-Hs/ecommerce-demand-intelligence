# Benchmark: DuckDB vs PySpark (local)

## Methodology

- **Dataset:** `data/silver/uci_transactions.parquet` (UCI Online Retail II, ~1.07M rows).
- **Operation:** group-by `stock_code, country` with `SUM(quantity)` and
  `SUM(quantity * unit_price)`, filtering out cancellations.
- **Hardware:** local WSL2 environment (single node).
- **Spark config:** `local[*]`, Java 17 (Temurin).

## Results

| Engine | Duration (s) |
|---|---|
| DuckDB 2.0.1 | 0.3643 |
| PySpark 3.5.3 | 24.1690 |

Ratio (Spark / DuckDB): **66.34x**.

## Interpretation

For this single-node, sub-GB workload, DuckDB is dramatically faster. Most of the
Spark time is JVM startup and task scheduling overhead rather than computation.
This supports the approved decision (ADR-0002): DuckDB is the primary analytical
engine; PySpark remains planned and is justified only for larger distributed or
cluster workloads. A future benchmark on the full Favorita dataset (when available)
should re-evaluate the crossover point.

## Limitations

- Single run, no warm-up, no repeated trials.
- Dataset is small (~1.07M rows); results may differ at 30M+ rows.
- Spark measured in local mode only.
- No memory profiling performed.

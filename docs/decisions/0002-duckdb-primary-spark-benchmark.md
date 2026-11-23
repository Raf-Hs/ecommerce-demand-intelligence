# ADR 0002 — DuckDB as primary analytical engine; PySpark via benchmark

- **Status:** Accepted
- **Date:** Phase 0 (user decision)

## Context
The platform must process ~31.8M H&M rows and a Favorita benchmark dataset. Two candidate
engines: DuckDB (local, fast, SQL) and PySpark (distributed).

## Decision
- DuckDB is the **primary** analytical engine for Silver/Gold transformations and analytics.
- PySpark is **planned but not mandatory** for initial pipelines.
- Before making Spark mandatory, run a **comparative benchmark (DuckDB vs PySpark)** on an
  available dataset (UCI Online Retail II; Favorita unavailable due to Kaggle credentials)
  and document measurable benefits (duration, memory, scalability).
- Adoption of Spark for a given pipeline requires evidence from that benchmark.

## Consequences
- Simpler initial implementation and lower resource requirements.
- Spark code paths remain optional until justified.
- Benchmark completed on UCI (~1.07M rows): DuckDB 0.36s vs PySpark 24.17s (ratio 66x).
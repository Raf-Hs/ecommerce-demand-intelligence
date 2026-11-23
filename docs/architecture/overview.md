# Architecture Overview

## System architecture

```mermaid
flowchart LR
    Sources[Sources] --> Ingestion[Ingestion]
    Ingestion --> Bronze[Bronze Parquet]
    Bronze --> Silver[Silver DuckDB]
    Silver --> Gold[Gold DuckDB]
    Silver --> dbt[dbt on DuckDB]
    Gold --> Serving[(PostgreSQL)]
    Gold --> Airflow[Airflow DAG]
```

## Medallion layers

- **Bronze**: raw preservation with ingestion metadata (`_source_system`, `_source_file`,
  `_ingestion_timestamp`).
- **Silver**: standardized schemas, normalized identifiers, validation, duplicate handling.
- **Gold**: analytical models (demand, velocity, inventory, replenishment).

## Data lineage

```mermaid
flowchart LR
    HM[H&M sample] --> B1[bronze/hm_sample/*]
    UCI[UCI XLSX] --> B2[bronze/uci/*]
    B1 --> S1[silver/hm_*]
    B2 --> S2[silver/uci_*]
    S1 --> G1[gold/hm_*]
    S2 --> G2[gold/uci_*]
    S1 --> SYN[gold/synthetic_*]
    S1 --> DBT[dbt marts]
```

## Technology responsibilities

- Python: orchestration, ingestion, synthetic generation.
- DuckDB: Silver/Gold transforms and analytics.
- dbt Core: SQL models and tests on DuckDB.
- Airflow: DAG orchestration (defined, not deployed).
- PostgreSQL: serving layer.
- Docker Compose: local infrastructure.
- GitHub Actions: CI (lint + tests).

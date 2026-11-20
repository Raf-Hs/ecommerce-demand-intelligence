# ADR 0006 — dbt Core for SQL transformations

- **Status:** Accepted
- **Date:** Phase 0 (user decision)

## Context
Need maintainable, tested, documented SQL transformations with lineage.

## Decision
- Use dbt Core with dbt-duckdb adapter for Silver/Gold SQL models.
- dbt tests enforce data quality (not null, unique, relationships, accepted values).

## Consequences
- Transformation logic lives in `dbt/` as version-controlled SQL.
- Python handles ingestion and complex parsing; dbt handles dimensional modelling.
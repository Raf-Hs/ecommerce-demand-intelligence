# ADR 0005 — Local-only infrastructure via Docker Compose

- **Status:** Accepted
- **Date:** Phase 0 (user decision)

## Context
Portfolio project must be reproducible locally without paid cloud services.

## Decision
- Keep the entire platform local.
- Use Docker Compose for infrastructure services (PostgreSQL, Airflow, optional Spark).
- No paid cloud dependencies.

## Consequences
- Performance claims are local-machine benchmarks; document hardware.
# ADR 0003 — Data sources and source_system isolation

- **Status:** Accepted
- **Date:** Phase 0 (user decision)

## Context
Need multi-source retail data while avoiding artificial joins between unrelated entities.

## Decision
- Primary: H&M Personalized Fashion Recommendations (Kaggle).
- Secondary: UCI Online Retail II (independent retail source).
- Benchmark/large-scale: Favorita Store Sales (Kaggle).
- Calendar: Python `holidays` library.
- Synthetic operational data: inventory, POs, suppliers, warehouses, adjustments (clearly labelled).
- Every record carries `source_system`. Never fabricate relationships between H&M and Favorita/UCI
  customer or product identifiers.

## Consequences
- Unified fact models use `source_system` discriminator.
- Cross-source analytics are limited to aggregate-level comparisons.
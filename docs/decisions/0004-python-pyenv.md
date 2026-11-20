# ADR 0004 — Python 3.11 via pyenv in WSL2

- **Status:** Accepted
- **Date:** Phase 0 (user decision)

## Context
WSL Ubuntu ships Python 3.14, which is too new for Spark/Airflow/dbt compatibility.

## Decision
- Provision Python 3.11 using pyenv inside Ubuntu WSL2.
- Use an isolated virtual environment for project dependencies.

## Consequences
- Phase 1 begins with environment setup (pyenv + python 3.11 + venv).
# Local Development Setup

## Prerequisites

- Windows 11 with WSL2 and Ubuntu.
- Docker Desktop with WSL2 integration.
- Git and GitHub (SSH) configured.
- pyenv (installed under `~/.pyenv`).

## Python version management

The project pins Python 3.11.9 via `.python-version`. pyenv selects it automatically
inside the project directory.

```bash
python --version   # Python 3.11.9
```

The system Python (`/usr/bin/python3`) is not modified.

## Virtual environment

```bash
cd ~/projects/ecommerce-demand-intelligence
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Verify the environment

```bash
.venv/bin/python -c "import duckdb, pandas, pyarrow; print('ok')"
.venv/bin/pytest --version
.venv/bin/ruff --version
```

## Docker infrastructure

See `infrastructure/README.md`. PostgreSQL runs on host port 5433 by default
(port 5432 is commonly occupied by other local instances).

```bash
cp .env.example .env
docker compose -f infrastructure/docker-compose.yml --env-file .env up -d
docker compose -f infrastructure/docker-compose.yml ps
```

## Troubleshooting

- **`python` not found after pyenv install:** ensure `~/.bashrc` contains the pyenv
  init lines and reload the shell (`source ~/.bashrc`) or use an interactive shell.
- **Port 5432 already allocated:** set `POSTGRES_PORT=5433` (default) in `.env`.
- **Docker daemon not reachable in WSL:** start Docker Desktop on Windows.
- **pip install fails for psycopg2:** use `psycopg2-binary` (already specified).

## Reproducibility

- Python version: `.python-version`.
- Dependencies: `requirements.txt` (runtime) and `requirements-dev.txt` (development).
- Infrastructure: `infrastructure/docker-compose.yml` + `.env.example`.
- No datasets, credentials, or virtual environments are committed.

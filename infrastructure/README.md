# Infrastructure

Local development infrastructure is managed with Docker Compose.

## Prerequisites

- Docker Desktop (or Docker Engine) running and integrated with WSL2.
- Docker Compose v2 (`docker compose`).

Verify:

```bash
docker --version
docker compose version
docker info
```

## Start PostgreSQL

```bash
cp .env.example .env
# edit .env and set a strong POSTGRES_PASSWORD

docker compose -f infrastructure/docker-compose.yml --env-file .env up -d
```

## Verify

```bash
docker compose -f infrastructure/docker-compose.yml ps
docker compose -f infrastructure/docker-compose.yml exec postgres pg_isready
```

## Stop

```bash
docker compose -f infrastructure/docker-compose.yml down
```

To remove the data volume (destructive):

```bash
docker compose -f infrastructure/docker-compose.yml down -v
```

## Port note

The host port defaults to **5433** because port 5432 is commonly occupied by other
local PostgreSQL instances (for example, an existing `olist-postgres` container).
Change `POSTGRES_PORT` in `.env` if needed.

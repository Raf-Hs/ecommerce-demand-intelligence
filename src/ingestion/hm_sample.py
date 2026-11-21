"""Ingest the small public H&M sample into Bronze (development only)."""

import json
from pathlib import Path

import pandas as pd

from src.ingestion.base import write_bronze
from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger("ingestion.hm_sample")

SAMPLE_DIR = Path("data/samples/hm_sample")


def _read_jsonl(name: str) -> pd.DataFrame:
    rows = [json.loads(line) for line in (SAMPLE_DIR / name).read_text().splitlines() if line.strip()]
    return pd.DataFrame(rows)


def ingest_hm_sample() -> list[Path]:
    if not SAMPLE_DIR.exists():
        log.warning("hm_sample_missing", path=str(SAMPLE_DIR))
        return []

    written = []
    articles = _read_jsonl("articles.jsonl")
    customers = _read_jsonl("customers.jsonl")
    transactions = _read_jsonl("transactions.jsonl")

    written.append(write_bronze(articles, "hm_sample", "articles", "data/samples/hm_sample/articles.jsonl"))
    written.append(write_bronze(customers, "hm_sample", "customers", "data/samples/hm_sample/customers.jsonl"))
    written.append(write_bronze(transactions, "hm_sample", "transactions", "data/samples/hm_sample/transactions.jsonl"))
    log.info("hm_sample_ingestion_complete",
             articles=len(articles), customers=len(customers), transactions=len(transactions))
    return written

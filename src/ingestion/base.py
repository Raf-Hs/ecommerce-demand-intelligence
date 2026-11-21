"""Shared Bronze-layer helpers."""

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger("ingestion.base")


def bronze_path(source: str, table: str) -> Path:
    out = settings.bronze_dir / source / f"{table}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def write_bronze(df: pd.DataFrame, source: str, table: str, source_file: str) -> Path:
    """Persist a DataFrame to Bronze as Parquet with ingestion metadata."""
    out = df.copy()
    # Preserve original values; force object columns to string for Arrow compatibility
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].astype("string")
    out["_source_system"] = source
    out["_source_file"] = source_file
    out["_ingestion_timestamp"] = datetime.now(UTC)
    path = bronze_path(source, table)
    out.to_parquet(path, index=False, engine="pyarrow")
    log.info("bronze_written", source=source, table=table, rows=len(out), path=str(path))
    return path

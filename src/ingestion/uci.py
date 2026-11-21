"""Ingest the UCI Online Retail II dataset into Bronze."""

from pathlib import Path

import pandas as pd

from src.ingestion.base import write_bronze
from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger("ingestion.uci")


def ingest_uci() -> list[Path]:
    raw = settings.raw_uci / "online_retail_II.xlsx"
    if not raw.exists():
        log.warning("uci_raw_missing", path=str(raw))
        return []

    written = []
    xl = pd.ExcelFile(raw)
    for sheet in xl.sheet_names:
        df = pd.read_excel(raw, sheet_name=sheet)
        table = "transactions"
        # tag the sheet origin for traceability
        df["_source_sheet"] = sheet
        path = write_bronze(df, "uci", f"transactions_{sheet.replace(' ', '_').lower()}", str(raw))
        written.append(path)
    log.info("uci_ingestion_complete", sheets=xl.sheet_names,
             total_rows=sum(pd.read_excel(raw, sheet_name=s).shape[0] for s in xl.sheet_names))
    return written

"""Silver-layer transformations using DuckDB over Bronze Parquet."""

from pathlib import Path

import duckdb

from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger("transformation.silver")


def _out(name: str) -> Path:
    p = settings.silver_dir / f"{name}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def build_hm_sample_silver() -> None:
    con = duckdb.connect()
    bronze = settings.bronze_dir / "hm_sample"

    # Articles: normalize article_id to 10-digit zero-padded string
    con.execute(f"""
        COPY (
            SELECT
                LPAD(CAST(article_id AS VARCHAR), 10, '0') AS article_id,
                CAST(product_code AS INTEGER) AS product_code,
                prod_name,
                CAST(product_type_no AS INTEGER) AS product_type_no,
                product_type_name,
                product_group_name,
                CAST(graphical_appearance_no AS INTEGER) AS graphical_appearance_no,
                graphical_appearance_name,
                CAST(colour_group_code AS INTEGER) AS colour_group_code,
                colour_group_name,
                CAST(perceived_colour_value_id AS INTEGER) AS perceived_colour_value_id,
                perceived_colour_value_name,
                CAST(perceived_colour_master_id AS INTEGER) AS perceived_colour_master_id,
                perceived_colour_master_name,
                CAST(department_no AS INTEGER) AS department_no,
                department_name,
                index_code,
                index_name,
                CAST(index_group_no AS INTEGER) AS index_group_no,
                index_group_name,
                CAST(section_no AS INTEGER) AS section_no,
                section_name,
                CAST(garment_group_no AS INTEGER) AS garment_group_no,
                garment_group_name,
                NULLIF(TRIM(detail_desc), '') AS detail_desc,
                _source_system,
                _ingestion_timestamp
            FROM read_parquet('{bronze}/articles.parquet')
        ) TO '{_out("hm_articles")}' (FORMAT PARQUET);
    """)

    # Customers: normalize missingness
    con.execute(f"""
        COPY (
            SELECT
                customer_id,
                CASE WHEN FN IS NULL OR isnan(FN) THEN FALSE ELSE (FN = 1) END AS has_fn,
                CASE WHEN Active IS NULL OR isnan(Active) THEN FALSE ELSE (Active = 1) END AS is_active,
                NULLIF(TRIM(club_member_status), '') AS club_member_status,
                NULLIF(TRIM(fashion_news_frequency), '') AS fashion_news_frequency,
                CASE WHEN age IS NULL OR isnan(age) THEN NULL ELSE CAST(age AS INTEGER) END AS age,
                postal_code,
                _source_system,
                _ingestion_timestamp
            FROM read_parquet('{bronze}/customers.parquet')
        ) TO '{_out("hm_customers")}' (FORMAT PARQUET);
    """)

    # Transactions: normalize article_id, validate price, drop exact full-row duplicates
    con.execute(f"""
        COPY (
            SELECT DISTINCT
                t_dat::DATE AS transaction_date,
                customer_id,
                LPAD(CAST(article_id AS VARCHAR), 10, '0') AS article_id,
                CAST(price AS DOUBLE) AS price,
                CAST(sales_channel_id AS INTEGER) AS sales_channel_id,
                _source_system,
                _ingestion_timestamp
            FROM read_parquet('{bronze}/transactions.parquet')
            WHERE price IS NOT NULL AND price >= 0
        ) TO '{_out("hm_transactions")}' (FORMAT PARQUET);
    """)
    log.info("hm_sample_silver_complete")


def build_uci_silver() -> None:
    con = duckdb.connect()
    bronze = settings.bronze_dir / "uci"
    files = [str(p) for p in bronze.glob("transactions_*.parquet")]
    if not files:
        log.warning("uci_bronze_missing")
        return
    file_list = ", ".join(f"'{f}'" for f in files)
    con.execute(f"""
        COPY (
            SELECT
                Invoice AS invoice_no,
                StockCode AS stock_code,
                NULLIF(TRIM(Description), '') AS description,
                CAST(Quantity AS INTEGER) AS quantity,
                InvoiceDate::TIMESTAMP AS invoice_date,
                CAST(Price AS DOUBLE) AS unit_price,
                CAST("Customer ID" AS VARCHAR) AS customer_id,
                Country AS country,
                (Invoice LIKE 'C%') AS is_cancellation,
                (Quantity < 0) AS is_return,
                _source_system,
                _ingestion_timestamp
            FROM read_parquet([{file_list}])
        ) TO '{_out("uci_transactions")}' (FORMAT PARQUET);
    """)
    log.info("uci_silver_complete", files=files)


def build_all() -> None:
    build_hm_sample_silver()
    build_uci_silver()
    log.info("silver_build_complete")


if __name__ == "__main__":
    build_all()

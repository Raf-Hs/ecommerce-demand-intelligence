"""Gold-layer analytical models using DuckDB over Silver Parquet."""

from pathlib import Path

import duckdb

from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger("transformation.gold")


def _out(name: str) -> Path:
    p = settings.gold_dir / f"{name}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def build_hm_gold() -> None:
    con = duckdb.connect()
    s = settings.silver_dir

    # Daily product demand (fact)
    con.execute(f"""
        COPY (
            SELECT
                t.transaction_date,
                t.article_id,
                a.product_type_name,
                a.product_group_name,
                a.department_name,
                a.index_name,
                COUNT(*) AS transaction_lines,
                SUM(t.price) AS revenue_norm,
                COUNT(DISTINCT t.customer_id) AS distinct_customers
            FROM read_parquet('{s}/hm_transactions.parquet') t
            LEFT JOIN read_parquet('{s}/hm_articles.parquet') a USING (article_id)
            GROUP BY 1,2,3,4,5,6
        ) TO '{_out("hm_daily_product_demand")}' (FORMAT PARQUET);
    """)

    # Product sales velocity
    con.execute(f"""
        COPY (
            SELECT
                article_id,
                product_type_name,
                product_group_name,
                COUNT(*) AS total_lines,
                SUM(price) AS total_revenue_norm,
                COUNT(DISTINCT transaction_date) AS active_days,
                COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT transaction_date), 0) AS lines_per_active_day
            FROM read_parquet('{s}/hm_transactions.parquet') t
            LEFT JOIN read_parquet('{s}/hm_articles.parquet') a USING (article_id)
            GROUP BY 1,2,3
        ) TO '{_out("hm_product_velocity")}' (FORMAT PARQUET);
    """)
    log.info("hm_gold_complete")


def build_uci_gold() -> None:
    con = duckdb.connect()
    s = settings.silver_dir
    con.execute(f"""
        COPY (
            SELECT
                invoice_date::DATE AS sale_date,
                stock_code,
                country,
                COUNT(*) AS line_count,
                SUM(quantity) AS total_quantity,
                SUM(quantity * unit_price) AS revenue,
                COUNT(DISTINCT invoice_no) AS distinct_invoices
            FROM read_parquet('{s}/uci_transactions.parquet')
            WHERE NOT is_cancellation
            GROUP BY 1,2,3
        ) TO '{_out("uci_daily_product_demand")}' (FORMAT PARQUET);
    """)
    log.info("uci_gold_complete")


def build_all() -> None:
    build_hm_gold()
    build_uci_gold()
    log.info("gold_build_complete")


if __name__ == "__main__":
    build_all()

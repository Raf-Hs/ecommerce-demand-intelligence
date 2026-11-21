"""Generate clearly-labelled synthetic operational inventory data."""

import random
from datetime import date, timedelta

import duckdb
import pandas as pd

from src.utils.config import settings
from src.utils.logging import get_logger

log = get_logger("synthetic.inventory")
SEED = 42
random.seed(SEED)


def _out(name: str):
    p = settings.gold_dir / f"{name}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def generate() -> None:
    con = duckdb.connect()
    s = settings.silver_dir

    # Distinct articles from H&M sample
    articles = con.execute(
        f"SELECT DISTINCT article_id FROM read_parquet('{s}/hm_articles.parquet')"
    ).fetchdf()["article_id"].tolist()

    warehouses = pd.DataFrame([
        {"warehouse_id": "WH01", "warehouse_name": "Nordic DC", "country": "SE", "capacity_units": 50000},
        {"warehouse_id": "WH02", "warehouse_name": "Central Europe DC", "country": "DE", "capacity_units": 80000},
        {"warehouse_id": "WH03", "warehouse_name": "UK DC", "country": "GB", "capacity_units": 60000},
    ])

    suppliers = pd.DataFrame([
        {"supplier_id": f"SUP{i:03d}", "supplier_name": f"Supplier {i}", "lead_time_days": random.randint(3, 14)}
        for i in range(1, 8)
    ])

    # Inventory snapshots: one row per article x warehouse, with stock levels derived from
    # recent demand velocity + a coverage target + noise.
    snapshot_date = date(2020, 9, 22)
    rows = []
    for a in articles[:200]:  # keep scope small and reproducible
        for w in warehouses["warehouse_id"]:
            velocity = random.uniform(0.5, 5.0)
            cover = random.randint(7, 21)
            stock = int(velocity * cover + random.randint(-5, 5))
            stock = max(stock, 0)
            rows.append({
                "snapshot_date": snapshot_date,
                "article_id": a,
                "warehouse_id": w,
                "on_hand_units": stock,
                "reserved_units": random.randint(0, max(1, stock // 5)),
                "reorder_point": int(velocity * 5),
                "safety_stock": int(velocity * 2),
                "is_synthetic": True,
                "source_system": "synthetic_ops",
            })
    inv = pd.DataFrame(rows)

    # Purchase orders: triggered when on_hand < reorder_point
    po_rows = []
    po_id = 1000
    for r in rows:
        if r["on_hand_units"] < r["reorder_point"]:
            lead = random.choice(suppliers["lead_time_days"].tolist())
            po_rows.append({
                "po_id": f"PO{po_id}",
                "po_date": snapshot_date - timedelta(days=random.randint(1, 5)),
                "article_id": r["article_id"],
                "warehouse_id": r["warehouse_id"],
                "supplier_id": random.choice(suppliers["supplier_id"].tolist()),
                "ordered_units": r["reorder_point"] * 2,
                "lead_time_days": lead,
                "expected_receipt_date": snapshot_date + timedelta(days=lead),
                "status": "open",
                "is_synthetic": True,
                "source_system": "synthetic_ops",
            })
            po_id += 1
    pos = pd.DataFrame(po_rows)

    # Stock adjustments
    adj_rows = []
    for r in rows[:50]:
        adj_rows.append({
            "adjustment_date": snapshot_date,
            "article_id": r["article_id"],
            "warehouse_id": r["warehouse_id"],
            "adjustment_type": random.choice(["shrinkage", "damage", "correction"]),
            "quantity_delta": -random.randint(1, 5),
            "is_synthetic": True,
            "source_system": "synthetic_ops",
        })
    adjs = pd.DataFrame(adj_rows)

    warehouses.to_parquet(_out("synthetic_warehouses"), index=False)
    suppliers.to_parquet(_out("synthetic_suppliers"), index=False)
    inv.to_parquet(_out("synthetic_inventory_snapshots"), index=False)
    pos.to_parquet(_out("synthetic_purchase_orders"), index=False)
    adjs.to_parquet(_out("synthetic_stock_adjustments"), index=False)

    log.info("synthetic_inventory_complete",
             warehouses=len(warehouses), suppliers=len(suppliers),
             snapshots=len(inv), purchase_orders=len(pos), adjustments=len(adjs))


if __name__ == "__main__":
    generate()

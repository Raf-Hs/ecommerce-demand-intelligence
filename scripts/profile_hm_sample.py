"""Profile the small public H&M sample used for schema/data-quality verification.

Source: jamescalam/hm-sample on Hugging Face (derived from the Kaggle H&M competition).
This is a SMALL derived sample (5,000 articles / 1,100 customers / ~15k transactions).
It is NOT the official dataset and is used only to validate assumptions during Phase 0.
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parents[1] / "data" / "samples" / "hm_sample"


def load(name):
    path = SAMPLE_DIR / name
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    articles = load("articles.jsonl")
    customers = load("customers.jsonl")
    transactions = load("transactions.jsonl")

    print("=== VOLUMES (sample) ===")
    print("articles", len(articles), "distinct", len({r["article_id"] for r in articles}))
    print("customers", len(customers), "distinct", len({r["customer_id"] for r in customers}))
    print("transactions", len(transactions))

    print("\n=== KEYS ===")
    print("article:", list(articles[0].keys()))
    print("customer:", list(customers[0].keys()))
    print("transaction:", list(transactions[0].keys()))

    print("\n=== NULL / MISSING (articles) ===")
    for k in articles[0]:
        print(f"  {k}: {sum(1 for r in articles if r.get(k) is None)}")

    print("\n=== NULL / MISSING (customers) ===")
    for k in customers[0]:
        print(f"  {k}: {sum(1 for r in customers if r.get(k) is None)}")
        if k in ("FN", "Active"):
            nan = sum(1 for r in customers if isinstance(r[k], float) and math.isnan(r[k]))
            print(f"     (NaN-encoded missing: {nan})")
        if k in ("club_member_status", "fashion_news_frequency"):
            empty = sum(1 for r in customers if r[k] == "")
            print(f"     (empty-string missing: {empty})")
    print("  age NaN:", sum(1 for r in customers if isinstance(r["age"], float) and math.isnan(r["age"])))

    print("\n=== TRANSACTIONS ===")
    print("nulls:", {k: sum(1 for r in transactions if r.get(k) is None) for k in transactions[0]})
    print("date range:", min(r["t_dat"] for r in transactions), "->", max(r["t_dat"] for r in transactions))
    print("distinct dates:", len({r["t_dat"] for r in transactions}))
    prices = [r["price"] for r in transactions]
    print("price min/max/mean:", min(prices), max(prices), sum(prices) / len(prices))
    print("sales_channel:", dict(Counter(r["sales_channel_id"] for r in transactions)))

    # referential integrity
    aids = {r["article_id"] for r in articles}
    cids = {r["customer_id"] for r in customers}
    print("txn article_id not in articles:", sum(1 for r in transactions if r["article_id"] not in aids))
    print("txn customer_id not in customers:", sum(1 for r in transactions if r["customer_id"] not in cids))

    # duplicates
    full = Counter(tuple(sorted(r.items())) for r in transactions)
    print("exact full-row duplicate extra rows:", sum(v - 1 for v in full.values() if v > 1))
    g = defaultdict(list)
    for r in transactions:
        g[(r["customer_id"], r["article_id"], r["t_dat"])].append(r)
    multi = [v for v in g.values() if len(v) > 1]
    print("cust-art-date groups with >1 row:", len(multi))
    diff = sum(1 for v in multi if len({x["price"] for x in v}) > 1 or len({x["sales_channel_id"] for x in v}) > 1)
    print("  of which differ in price/channel:", diff)
    pairs = defaultdict(set)
    for r in transactions:
        pairs[(r["customer_id"], r["article_id"])].add(r["t_dat"])
    print("cust-art pairs with >1 distinct date:", sum(1 for v in pairs.values() if len(v) > 1))

    # article id / product code relationship
    print("\n=== ARTICLE ID STRUCTURE ===")
    print("article_id min/max:", min(r["article_id"] for r in articles), max(r["article_id"] for r in articles))
    print("article_id < 1e8 (lost leading zero):", sum(1 for r in articles if r["article_id"] < 100_000_000))
    print("product_code // 10? article_id == product_code*1000+suffix:",
          all(r["article_id"] == r["product_code"] * 1000 + (r["article_id"] % 1000) for r in articles))
    print("distinct product_code:", len({r["product_code"] for r in articles}))

    print("\n=== CARDINALITIES (articles) ===")
    for col in ("product_type_name", "product_group_name", "graphical_appearance_name",
                "colour_group_name", "department_name", "index_name", "index_group_name",
                "section_name", "garment_group_name"):
        print(f"  {col}: {len({r[col] for r in articles})}")
    print("empty detail_desc:", sum(1 for r in articles if not r["detail_desc"]))

    print("\n=== CUSTOMERS ===")
    print("FN:", dict(Counter(r["FN"] for r in customers)))
    print("Active:", dict(Counter(r["Active"] for r in customers)))
    print("club_member_status:", dict(Counter(r["club_member_status"] for r in customers)))
    print("fashion_news_frequency:", dict(Counter(r["fashion_news_frequency"] for r in customers)))
    print("age min/max:", min(r["age"] for r in customers), max(r["age"] for r in customers))
    print("distinct postal_code:", len({r["postal_code"] for r in customers}))
    pc = Counter(r["postal_code"] for r in customers)
    print("top5 postal counts:", pc.most_common(5))


if __name__ == "__main__":
    main()

"""Generate data insight charts from the actual ingested datasets."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import duckdb
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
NAVY = "#1e3a5f"
GOLD = "#b45309"
GREEN = "#16a34a"
GREY = "#64748b"

S = ROOT / "data" / "silver"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(ASSETS / name, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# 1. H&M daily transactions
con = duckdb.connect()
df = con.execute(f"""
    SELECT transaction_date, COUNT(*) AS n
    FROM read_parquet('{S}/hm_transactions.parquet')
    GROUP BY transaction_date ORDER BY transaction_date
""").fetchdf()
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(df["transaction_date"], df["n"], color=NAVY, linewidth=1.2)
ax.set_title("H&M sample - daily transaction lines")
ax.set_xlabel("Date")
ax.set_ylabel("Transaction lines")
save(fig, "insight_hm_daily_transactions.png")

# 2. H&M top product groups
df = con.execute(f"""
    SELECT a.product_group_name, COUNT(*) AS n
    FROM read_parquet('{S}/hm_transactions.parquet') t
    JOIN read_parquet('{S}/hm_articles.parquet') a USING (article_id)
    GROUP BY a.product_group_name ORDER BY n DESC LIMIT 10
""").fetchdf()
fig, ax = plt.subplots(figsize=(9, 4))
ax.barh(df["product_group_name"][::-1], df["n"][::-1], color=NAVY)
ax.set_title("H&M sample - top 10 product groups by transaction lines")
ax.set_xlabel("Transaction lines")
save(fig, "insight_hm_top_product_groups.png")

# 3. H&M sales channel
df = con.execute(f"""
    SELECT sales_channel_id, COUNT(*) AS n
    FROM read_parquet('{S}/hm_transactions.parquet')
    GROUP BY sales_channel_id
""").fetchdf()
fig, ax = plt.subplots(figsize=(6, 4))
labels = ["Channel " + str(int(x)) for x in df["sales_channel_id"]]
ax.pie(df["n"], labels=labels, autopct="%1.1f%%", colors=[NAVY, GOLD])
ax.set_title("H&M sample - sales channel share")
save(fig, "insight_hm_sales_channel.png")

# 4. UCI daily revenue
df = con.execute(f"""
    SELECT invoice_date::DATE AS d, SUM(quantity*unit_price) AS rev
    FROM read_parquet('{S}/uci_transactions.parquet')
    WHERE NOT is_cancellation
    GROUP BY d ORDER BY d
""").fetchdf()
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(df["d"], df["rev"], color=GREEN, linewidth=1.0)
ax.set_title("UCI Online Retail II - daily revenue")
ax.set_xlabel("Date")
ax.set_ylabel("Revenue")
save(fig, "insight_uci_daily_revenue.png")

# 5. UCI top countries
df = con.execute(f"""
    SELECT country, SUM(quantity*unit_price) AS rev
    FROM read_parquet('{S}/uci_transactions.parquet')
    WHERE NOT is_cancellation
    GROUP BY country ORDER BY rev DESC LIMIT 10
""").fetchdf()
fig, ax = plt.subplots(figsize=(9, 4))
ax.barh(df["country"][::-1], df["rev"][::-1], color=GREEN)
ax.set_title("UCI - top 10 countries by revenue")
ax.set_xlabel("Revenue")
save(fig, "insight_uci_top_countries.png")

# 6. Data quality: null/missing counts per column (H&M customers)
cust = pd.read_parquet(ROOT / "data" / "bronze" / "hm_sample" / "customers.parquet")
nulls = cust.isna().sum()
# treat NaN-encoded missing for FN/Active already counted; also count empty strings
# treat NaN-encoded missing for FN/Active (already in isna) + empty strings
for c in ["club_member_status", "fashion_news_frequency"]:
    empty = int((cust[c].astype(str).str.strip() == "").sum())
    nulls[c] = int(nulls[c]) + empty
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(nulls.index, nulls.values, color=GREY)
ax.set_title("H&M sample - missing values per customer column")
ax.set_ylabel("Missing count")
ax.tick_params(axis="x", rotation=30)
save(fig, "insight_hm_customer_missingness.png")

# 7. UCI returns/cancellations share
df = con.execute(f"""
    SELECT
      SUM(CASE WHEN is_cancellation THEN 1 ELSE 0 END) AS canc,
      SUM(CASE WHEN is_return THEN 1 ELSE 0 END) AS ret,
      COUNT(*) AS total
    FROM read_parquet('{S}/uci_transactions.parquet')
""").fetchdf()
fig, ax = plt.subplots(figsize=(6, 4))
vals = [int(df["canc"][0]), int(df["ret"][0]), int(df["total"][0]) - int(df["canc"][0]) - int(df["ret"][0])]
ax.bar(["Cancellation", "Return", "Normal"], vals, color=[GOLD, GREY, GREEN])
ax.set_title("UCI - transaction type distribution")
ax.set_ylabel("Rows")
save(fig, "insight_uci_transaction_types.png")

print("all charts generated")

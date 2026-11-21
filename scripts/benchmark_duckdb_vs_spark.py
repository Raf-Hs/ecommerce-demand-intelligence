"""Benchmark DuckDB vs PySpark on the UCI silver dataset."""

import os
os.environ.setdefault("JAVA_HOME", "/home/rafa/.local/jdk/jdk-17.0.13+11")
os.environ.setdefault("PATH", os.environ["JAVA_HOME"] + "/bin:" + os.environ.get("PATH", ""))
os.environ.setdefault("TMPDIR", "/home/rafa/.spark-tmp")

import time

import duckdb
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

PARQUET = "data/silver/uci_transactions.parquet"


def bench_duckdb() -> float:
    con = duckdb.connect()
    t0 = time.perf_counter()
    con.execute(f"""
        SELECT stock_code, country, SUM(quantity) AS q, SUM(quantity*unit_price) AS rev
        FROM read_parquet('{PARQUET}')
        WHERE NOT is_cancellation
        GROUP BY stock_code, country
    """).fetchall()
    return time.perf_counter() - t0


def bench_spark() -> float:
    spark = (SparkSession.builder
             .appName("benchmark")
             .master("local[*]")
             .config("spark.local.dir", "/home/rafa/.spark-tmp")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    df = spark.read.parquet(PARQUET)
    t0 = time.perf_counter()
    (df.filter(~F.col("is_cancellation"))
       .groupBy("stock_code", "country")
       .agg(F.sum("quantity").alias("q"), F.sum(F.col("quantity") * F.col("unit_price")).alias("rev"))
       .count())
    return time.perf_counter() - t0


if __name__ == "__main__":
    d = bench_duckdb()
    s = bench_spark()
    print(f"duckdb_seconds={d:.4f}")
    print(f"spark_seconds={s:.4f}")
    print(f"ratio_spark_over_duckdb={s/d:.2f}")
    with open("docs/benchmarks_duckdb_vs_spark.txt", "w") as f:
        f.write(f"dataset: {PARQUET}\n")
        f.write(f"duckdb_seconds: {d:.4f}\n")
        f.write(f"spark_seconds: {s:.4f}\n")
        f.write(f"ratio_spark_over_duckdb: {s/d:.2f}\n")

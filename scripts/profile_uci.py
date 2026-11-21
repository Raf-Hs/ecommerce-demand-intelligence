#!/usr/bin/env python3
"""Profile the UCI Online Retail II dataset."""
import pandas as pd

path = "data/raw/uci/online_retail_II.xlsx"
xl = pd.ExcelFile(path)
print("sheets:", xl.sheet_names)
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    print("\n===", sheet, "===")
    print("shape:", df.shape)
    print("columns:", list(df.columns))
    print("dtypes:", df.dtypes.astype(str).to_dict())
    print("nulls:", df.isna().sum().to_dict())
    print("head:")
    print(df.head(3).to_string())
    if "Invoice" in df.columns:
        print("distinct invoices:", df["Invoice"].nunique())
    if "StockCode" in df.columns:
        print("distinct stock codes:", df["StockCode"].nunique())
    if "Country" in df.columns:
        print("countries:", df["Country"].nunique())
    if "Quantity" in df.columns:
        print("quantity min/max:", df["Quantity"].min(), df["Quantity"].max())
    if "Price" in df.columns:
        print("price min/max:", df["Price"].min(), df["Price"].max())


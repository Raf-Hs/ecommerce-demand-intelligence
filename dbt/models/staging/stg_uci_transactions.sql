{{ config(materialized='view') }}

select
    invoice_date,
    stock_code,
    country,
    quantity,
    unit_price,
    customer_id,
    is_cancellation,
    is_return
from read_parquet('../data/silver/uci_transactions.parquet')

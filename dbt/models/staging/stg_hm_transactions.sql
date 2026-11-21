{{ config(materialized='view') }}

select
    transaction_date,
    customer_id,
    article_id,
    price,
    sales_channel_id
from read_parquet('../data/silver/hm_transactions.parquet')

{{ config(materialized='table') }}

select
    t.transaction_date as sale_date,
    t.article_id,
    a.product_type_name,
    a.product_group_name,
    count(*) as transaction_lines,
    sum(t.price) as revenue_norm,
    count(distinct t.customer_id) as distinct_customers
from {{ ref('stg_hm_transactions') }} t
left join {{ ref('stg_hm_articles') }} a using (article_id)
group by 1, 2, 3, 4

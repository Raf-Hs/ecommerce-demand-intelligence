{{ config(materialized='view') }}

select
    article_id,
    product_code,
    prod_name,
    product_type_name,
    product_group_name,
    colour_group_name,
    department_name,
    index_name,
    section_name,
    garment_group_name,
    detail_desc
from read_parquet('../data/silver/hm_articles.parquet')

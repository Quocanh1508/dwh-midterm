SELECT
  product_id                                    AS product_key,
  product_name,
  brand,
  category,
  department,
  cost,
  retail_price,
  gross_margin,
  sku
FROM {{ ref('stg_products') }}

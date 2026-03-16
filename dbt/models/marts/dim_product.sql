SELECT
  product_id                                    AS product_key,
  product_name,
  brand,
  category,
  department,
  cost,
  retail_price,
  gross_margin,
  sku,
  distribution_center_id
FROM {{ ref('stg_products') }}

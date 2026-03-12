WITH raw_products AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _loaded_at DESC) AS rn
  FROM {{ source('retail_raw', 'products') }}
)

SELECT
  id                                            AS product_id,
  TRIM(name)                                    AS product_name,
  TRIM(brand)                                   AS brand,
  TRIM(category)                                AS category,
  TRIM(department)                              AS department,
  ROUND(cost, 2)                                AS cost,
  ROUND(retail_price, 2)                        AS retail_price,
  ROUND(retail_price - cost, 2)                 AS gross_margin,
  sku,
  distribution_center_id,
  _loaded_at
FROM raw_products
WHERE rn = 1

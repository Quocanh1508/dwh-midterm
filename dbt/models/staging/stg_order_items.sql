WITH raw_order_items AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _loaded_at DESC) AS rn
  FROM {{ source('retail_raw', 'order_items') }}
)

SELECT
  id                                            AS order_item_id,
  order_id,
  user_id,
  product_id,
  inventory_item_id,
  UPPER(TRIM(status))                           AS item_status,
  created_at,
  shipped_at,
  delivered_at,
  returned_at,
  ROUND(sale_price, 2)                          AS sale_price,
  _loaded_at
FROM raw_order_items
WHERE rn = 1

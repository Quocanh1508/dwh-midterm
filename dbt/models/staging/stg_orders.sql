WITH raw_orders AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY _loaded_at DESC) AS rn
  FROM {{ source('retail_raw', 'orders') }}
)

SELECT
  order_id,
  user_id,
  UPPER(TRIM(status))                           AS order_status,
  gender,
  created_at,
  returned_at,
  shipped_at,
  delivered_at,
  COALESCE(num_of_item, 0)                      AS num_of_item,
  DATE_DIFF(
    COALESCE(delivered_at, CURRENT_TIMESTAMP()),
    created_at,
    DAY
  )                                             AS fulfillment_days,
  _loaded_at
FROM raw_orders
WHERE rn = 1

SELECT
  oi.order_item_id,
  oi.order_id,
  oi.user_id                                    AS customer_key,
  oi.product_id                                 AS product_key,
  CAST(FORMAT_DATE('%Y%m%d', DATE(oi.created_at)) AS INT64)
                                                AS date_key,
  oi.item_status,
  oi.sale_price,
  p.cost,
  ROUND(oi.sale_price - p.cost, 2)              AS profit,
  ROUND(
    SAFE_DIVIDE(oi.sale_price - p.cost, oi.sale_price) * 100, 2
  )                                             AS profit_margin_pct,
  o.order_status,
  o.num_of_item,
  o.fulfillment_days,
  oi.created_at                                 AS sale_timestamp,
  DATE(oi.created_at)                           AS sale_date
FROM {{ ref('stg_order_items') }} oi
LEFT JOIN {{ ref('stg_orders') }} o
       ON oi.order_id = o.order_id
LEFT JOIN {{ ref('stg_products') }} p
       ON oi.product_id = p.product_id

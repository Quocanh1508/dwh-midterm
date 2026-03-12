-- =============================================================================
-- DDL: Staging Layer
-- Project : dwh-midterm-123456
-- Dataset : retail_staging
-- Purpose : Cleaned, typed, deduplicated views on top of raw tables.
-- =============================================================================

-- 1. STG_ORDERS --------------------------------------------------------------
CREATE OR REPLACE VIEW `dwh-midterm-123456.retail_staging.stg_orders` AS
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
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY _loaded_at DESC) AS rn
  FROM `dwh-midterm-123456.retail_raw.orders`
)
WHERE rn = 1;

-- 2. STG_ORDER_ITEMS ---------------------------------------------------------
CREATE OR REPLACE VIEW `dwh-midterm-123456.retail_staging.stg_order_items` AS
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
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _loaded_at DESC) AS rn
  FROM `dwh-midterm-123456.retail_raw.order_items`
)
WHERE rn = 1;

-- 3. STG_PRODUCTS ------------------------------------------------------------
CREATE OR REPLACE VIEW `dwh-midterm-123456.retail_staging.stg_products` AS
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
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _loaded_at DESC) AS rn
  FROM `dwh-midterm-123456.retail_raw.products`
)
WHERE rn = 1;

-- 4. STG_USERS / CUSTOMERS ---------------------------------------------------
CREATE OR REPLACE VIEW `dwh-midterm-123456.retail_staging.stg_users` AS
SELECT
  id                                            AS user_id,
  INITCAP(first_name)                           AS first_name,
  INITCAP(last_name)                            AS last_name,
  LOWER(email)                                  AS email,
  age,
  gender,
  city,
  state,
  country,
  postal_code,
  traffic_source,
  created_at                                    AS customer_since,
  _loaded_at
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _loaded_at DESC) AS rn
  FROM `dwh-midterm-123456.retail_raw.users`
)
WHERE rn = 1;

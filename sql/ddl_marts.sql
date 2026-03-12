-- =============================================================================
-- DDL: Marts Layer  (Kimball Star Schema)
-- Project : dwh-midterm-123456
-- Dataset : retail_marts
-- Purpose : Business-ready fact and dimension tables.
-- =============================================================================

-- ── DIMENSION: dim_date ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `dwh-midterm-123456.retail_marts.dim_date` (
  date_key        INT64     NOT NULL,   -- YYYYMMDD
  full_date       DATE      NOT NULL,
  year            INT64,
  quarter         INT64,
  month           INT64,
  month_name      STRING,
  week_of_year    INT64,
  day_of_week     INT64,
  day_name        STRING,
  is_weekend      BOOL
)
OPTIONS (description = "Date dimension – pre-populated via seed script");

-- ── DIMENSION: dim_customer ─────────────────────────────────────────────────
CREATE OR REPLACE VIEW `dwh-midterm-123456.retail_marts.dim_customer` AS
SELECT
  user_id                                       AS customer_key,
  first_name,
  last_name,
  CONCAT(first_name, ' ', last_name)            AS full_name,
  email,
  age,
  gender,
  city,
  state,
  country,
  traffic_source,
  customer_since
FROM `dwh-midterm-123456.retail_staging.stg_users`;

-- ── DIMENSION: dim_product ──────────────────────────────────────────────────
CREATE OR REPLACE VIEW `dwh-midterm-123456.retail_marts.dim_product` AS
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
FROM `dwh-midterm-123456.retail_staging.stg_products`;

-- ── FACT: fact_sales ────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW `dwh-midterm-123456.retail_marts.fact_sales` AS
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
FROM `dwh-midterm-123456.retail_staging.stg_order_items`  oi
LEFT JOIN `dwh-midterm-123456.retail_staging.stg_orders`  o
       ON oi.order_id  = o.order_id
LEFT JOIN `dwh-midterm-123456.retail_staging.stg_products` p
       ON oi.product_id = p.product_id;

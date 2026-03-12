-- =============================================================================
-- DDL: Raw Layer
-- Project : dwh-midterm-123456
-- Dataset : retail_raw
-- Purpose : Exact-copy landing zone for source data.
--           All columns kept as STRING to preserve source fidelity.
-- =============================================================================

-- 1. ORDERS ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `dwh-midterm-123456.retail_raw.orders` (
  order_id          STRING    NOT NULL,
  user_id           STRING,
  status            STRING,
  gender            STRING,
  created_at        TIMESTAMP,
  returned_at       TIMESTAMP,
  shipped_at        TIMESTAMP,
  delivered_at      TIMESTAMP,
  num_of_item       INT64,
  _loaded_at        TIMESTAMP  DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
OPTIONS (
  description = "Raw orders from thelook_ecommerce public dataset"
);

-- 2. ORDER ITEMS -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `dwh-midterm-123456.retail_raw.order_items` (
  id                STRING    NOT NULL,
  order_id          STRING,
  user_id           STRING,
  product_id        STRING,
  inventory_item_id STRING,
  status            STRING,
  created_at        TIMESTAMP,
  shipped_at        TIMESTAMP,
  delivered_at      TIMESTAMP,
  returned_at       TIMESTAMP,
  sale_price        FLOAT64,
  _loaded_at        TIMESTAMP  DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
OPTIONS (
  description = "Raw order items from thelook_ecommerce public dataset"
);

-- 3. PRODUCTS ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `dwh-midterm-123456.retail_raw.products` (
  id                STRING    NOT NULL,
  cost              FLOAT64,
  category          STRING,
  name              STRING,
  brand             STRING,
  retail_price      FLOAT64,
  department        STRING,
  sku               STRING,
  distribution_center_id STRING,
  _loaded_at        TIMESTAMP  DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = "Raw products from thelook_ecommerce public dataset"
);

-- 4. USERS / CUSTOMERS -------------------------------------------------------
CREATE TABLE IF NOT EXISTS `dwh-midterm-123456.retail_raw.users` (
  id                STRING    NOT NULL,
  first_name        STRING,
  last_name         STRING,
  email             STRING,
  age               INT64,
  gender            STRING,
  state             STRING,
  street_address    STRING,
  postal_code       STRING,
  city              STRING,
  country           STRING,
  latitude          FLOAT64,
  longitude         FLOAT64,
  traffic_source    STRING,
  created_at        TIMESTAMP,
  _loaded_at        TIMESTAMP  DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = "Raw users/customers from thelook_ecommerce public dataset"
);

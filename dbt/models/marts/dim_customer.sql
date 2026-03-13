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
  cuWITH stg_users AS (
    SELECT * FROM {{ ref('stg_users') }}
    WHERE non_existent_column_to_break_pipeline = 1 -- INTENTIONAL ERROR FOR DEMO
)

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
FROM {{ ref('stg_users') }}

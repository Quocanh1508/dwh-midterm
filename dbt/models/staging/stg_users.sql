WITH raw_users AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _loaded_at DESC) AS rn
  FROM {{ source('retail_raw', 'users') }}
)

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
FROM raw_users
WHERE rn = 1

WITH raw_dc AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _loaded_at DESC) AS rn
  FROM {{ source('retail_raw', 'distribution_centers') }}
)

SELECT
  id                                            AS distribution_center_id,
  name                                          AS dc_name,
  latitude,
  longitude,
  _loaded_at
FROM raw_dc
WHERE rn = 1

SELECT
  distribution_center_id                        AS dc_key,
  dc_name,
  latitude,
  longitude
FROM {{ ref('stg_distribution_centers') }}

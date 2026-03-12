WITH date_spine AS (
  SELECT date_day
  FROM UNNEST(GENERATE_DATE_ARRAY('2018-01-01', '2030-12-31')) AS date_day
)

SELECT
  CAST(FORMAT_DATE('%Y%m%d', date_day) AS INT64) AS date_key,
  date_day                                       AS full_date,
  EXTRACT(YEAR FROM date_day)                    AS year,
  EXTRACT(QUARTER FROM date_day)                 AS quarter,
  EXTRACT(MONTH FROM date_day)                   AS month,
  FORMAT_DATE('%B', date_day)                    AS month_name,
  EXTRACT(WEEK FROM date_day)                    AS week_of_year,
  EXTRACT(DAYOFWEEK FROM date_day)               AS day_of_week,
  FORMAT_DATE('%A', date_day)                    AS day_name,
  EXTRACT(DAYOFWEEK FROM date_day) IN (1, 7)     AS is_weekend
FROM date_spine

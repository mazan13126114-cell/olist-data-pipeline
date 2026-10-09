-- Calendar table covering every purchase date, for time-intelligence in BI tools.
CREATE OR REPLACE TABLE marts.dim_date AS
WITH bounds AS (
    SELECT
        min(purchased_at)::DATE AS start_date,
        max(purchased_at)::DATE AS end_date
    FROM staging.orders
)
SELECT
    d::DATE                      AS date,
    year(d)                      AS year,
    quarter(d)                   AS quarter,
    month(d)                     AS month,
    strftime(d, '%Y-%m')         AS year_month,
    strftime(d, '%B')            AS month_name,
    dayname(d)                   AS weekday,
    isodow(d) IN (6, 7)          AS is_weekend
FROM bounds,
     generate_series(start_date, end_date, INTERVAL 1 DAY) AS t(d);

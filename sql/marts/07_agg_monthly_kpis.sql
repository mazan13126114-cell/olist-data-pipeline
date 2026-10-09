-- Pre-aggregated monthly KPIs for a dashboard's headline cards and trend line.
CREATE OR REPLACE TABLE marts.agg_monthly_kpis AS
SELECT
    strftime(order_date, '%Y-%m')                              AS year_month,
    count(*)                                                   AS orders,
    count(DISTINCT customer_key)                               AS customers,
    round(sum(items_value), 2)                                 AS revenue,
    round(sum(items_value) / count(*), 2)                      AS avg_order_value,
    round(avg(review_score), 2)                                AS avg_review_score,
    round(avg(delivery_days), 1)                               AS avg_delivery_days,
    round(100.0 * avg(CASE WHEN is_late THEN 1 ELSE 0 END)
          FILTER (WHERE is_late IS NOT NULL), 1)               AS late_delivery_pct
FROM marts.fct_orders
WHERE order_status NOT IN ('canceled', 'unavailable')
GROUP BY 1
ORDER BY 1;

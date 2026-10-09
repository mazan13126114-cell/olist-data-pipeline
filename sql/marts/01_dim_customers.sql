-- One row per real customer (customer_unique_id), using the location from
-- their most recent order.
CREATE OR REPLACE TABLE marts.dim_customers AS
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        c.city,
        c.state,
        c.zip_code_prefix,
        o.purchased_at
    FROM staging.customers c
    LEFT JOIN staging.orders o USING (customer_id)
)
SELECT
    customer_unique_id                                   AS customer_key,
    arg_max(city,            purchased_at)               AS city,
    arg_max(state,           purchased_at)               AS state,
    arg_max(zip_code_prefix, purchased_at)               AS zip_code_prefix,
    min(purchased_at)                                    AS first_order_at,
    max(purchased_at)                                    AS last_order_at,
    count(purchased_at)                                  AS lifetime_orders
FROM customer_orders
GROUP BY customer_unique_id;

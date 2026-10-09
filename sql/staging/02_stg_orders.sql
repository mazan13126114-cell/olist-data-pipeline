CREATE OR REPLACE TABLE staging.orders AS
SELECT DISTINCT
    trim(order_id)                                          AS order_id,
    trim(customer_id)                                       AS customer_id,
    lower(trim(order_status))                               AS order_status,
    try_cast(order_purchase_timestamp      AS TIMESTAMP)    AS purchased_at,
    try_cast(order_approved_at             AS TIMESTAMP)    AS approved_at,
    try_cast(order_delivered_carrier_date  AS TIMESTAMP)    AS shipped_at,
    try_cast(order_delivered_customer_date AS TIMESTAMP)    AS delivered_at,
    try_cast(order_estimated_delivery_date AS TIMESTAMP)    AS estimated_delivery_at
FROM raw.orders
WHERE order_id IS NOT NULL;

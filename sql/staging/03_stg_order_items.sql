CREATE OR REPLACE TABLE staging.order_items AS
SELECT DISTINCT
    trim(order_id)                                 AS order_id,
    try_cast(order_item_id AS INTEGER)             AS order_item_id,
    trim(product_id)                               AS product_id,
    trim(seller_id)                                AS seller_id,
    try_cast(shipping_limit_date AS TIMESTAMP)     AS shipping_limit_at,
    try_cast(price         AS DECIMAL(10, 2))      AS price,
    try_cast(freight_value AS DECIMAL(10, 2))      AS freight_value
FROM raw.order_items
WHERE order_id IS NOT NULL;

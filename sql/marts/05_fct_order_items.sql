-- Grain: one row per item in an order.
CREATE OR REPLACE TABLE marts.fct_order_items AS
SELECT
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    c.customer_unique_id         AS customer_key,
    o.purchased_at::DATE         AS order_date,
    o.order_status,
    i.price,
    i.freight_value,
    i.price + i.freight_value    AS total_value
FROM staging.order_items i
JOIN staging.orders     o USING (order_id)
JOIN staging.customers  c USING (customer_id);

-- Grain: one row per order, with payments, review and delivery performance.
CREATE OR REPLACE TABLE marts.fct_orders AS
WITH items AS (
    SELECT
        order_id,
        count(*)            AS item_count,
        sum(price)          AS items_value,
        sum(freight_value)  AS freight_value
    FROM staging.order_items
    GROUP BY order_id
),
payments AS (
    SELECT
        order_id,
        sum(payment_value)                       AS payment_value,
        arg_max(payment_type, payment_value)     AS main_payment_type,
        max(installments)                        AS installments
    FROM staging.order_payments
    GROUP BY order_id
)
SELECT
    o.order_id,
    c.customer_unique_id                                   AS customer_key,
    o.order_status,
    o.purchased_at,
    o.purchased_at::DATE                                   AS order_date,
    o.delivered_at,
    o.estimated_delivery_at,
    coalesce(i.item_count, 0)                              AS item_count,
    coalesce(i.items_value, 0)                             AS items_value,
    coalesce(i.freight_value, 0)                           AS freight_value,
    p.payment_value,
    p.main_payment_type,
    p.installments,
    r.review_score,
    date_diff('day', o.purchased_at, o.delivered_at)       AS delivery_days,
    CASE
        WHEN o.delivered_at IS NULL THEN NULL
        ELSE o.delivered_at::DATE > o.estimated_delivery_at::DATE
    END                                                    AS is_late
FROM staging.orders o
JOIN staging.customers           c USING (customer_id)
LEFT JOIN items                  i USING (order_id)
LEFT JOIN payments               p USING (order_id)
LEFT JOIN staging.order_reviews  r USING (order_id);

-- An order can be paid in several parts (e.g. voucher + credit card).
CREATE OR REPLACE TABLE staging.order_payments AS
SELECT DISTINCT
    trim(order_id)                                  AS order_id,
    try_cast(payment_sequential   AS INTEGER)       AS payment_sequential,
    lower(trim(payment_type))                       AS payment_type,
    try_cast(payment_installments AS INTEGER)       AS installments,
    try_cast(payment_value        AS DECIMAL(10, 2)) AS payment_value
FROM raw.order_payments
WHERE order_id IS NOT NULL;

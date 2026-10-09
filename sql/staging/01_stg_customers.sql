-- One row per customer_id (Olist creates a new customer_id for every order;
-- customer_unique_id is the real person).
CREATE OR REPLACE TABLE staging.customers AS
SELECT DISTINCT
    trim(customer_id)                          AS customer_id,
    trim(customer_unique_id)                   AS customer_unique_id,
    lpad(trim(customer_zip_code_prefix), 5, '0') AS zip_code_prefix,
    lower(trim(customer_city))                 AS city,
    upper(trim(customer_state))                AS state
FROM raw.customers
WHERE customer_id IS NOT NULL;

CREATE OR REPLACE TABLE staging.sellers AS
SELECT DISTINCT
    trim(seller_id)                              AS seller_id,
    lpad(trim(seller_zip_code_prefix), 5, '0')   AS zip_code_prefix,
    lower(trim(seller_city))                     AS city,
    upper(trim(seller_state))                    AS state
FROM raw.sellers
WHERE seller_id IS NOT NULL;

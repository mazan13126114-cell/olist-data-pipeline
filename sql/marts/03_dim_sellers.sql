CREATE OR REPLACE TABLE marts.dim_sellers AS
SELECT
    seller_id,
    city,
    state,
    zip_code_prefix
FROM staging.sellers;

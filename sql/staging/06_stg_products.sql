-- Category names are Portuguese in the raw data; translate them to English.
-- (Note: "lenght" is a typo in the original Kaggle column names.)
CREATE OR REPLACE TABLE staging.products AS
SELECT DISTINCT
    trim(p.product_id)                                         AS product_id,
    coalesce(t.product_category_name_english,
             p.product_category_name, 'unknown')               AS category,
    try_cast(p.product_photos_qty AS INTEGER)                  AS photos_qty,
    try_cast(p.product_weight_g   AS INTEGER)                  AS weight_g,
    try_cast(p.product_length_cm  AS INTEGER)                  AS length_cm,
    try_cast(p.product_height_cm  AS INTEGER)                  AS height_cm,
    try_cast(p.product_width_cm   AS INTEGER)                  AS width_cm
FROM raw.products p
LEFT JOIN raw.category_translation t
       ON trim(p.product_category_name) = trim(t.product_category_name)
WHERE p.product_id IS NOT NULL;

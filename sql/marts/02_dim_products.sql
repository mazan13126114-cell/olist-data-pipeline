CREATE OR REPLACE TABLE marts.dim_products AS
SELECT
    product_id,
    category,
    photos_qty,
    weight_g,
    length_cm * height_cm * width_cm AS volume_cm3
FROM staging.products;

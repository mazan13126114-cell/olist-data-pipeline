-- The raw reviews file contains duplicate review_ids and some orders with
-- more than one review. Keep only the most recent review per order.
CREATE OR REPLACE TABLE staging.order_reviews AS
WITH typed AS (
    SELECT
        trim(review_id)                               AS review_id,
        trim(order_id)                                AS order_id,
        try_cast(review_score AS INTEGER)             AS review_score,
        nullif(trim(review_comment_message), '')      AS review_comment,
        try_cast(review_creation_date    AS TIMESTAMP) AS review_created_at,
        try_cast(review_answer_timestamp AS TIMESTAMP) AS review_answered_at
    FROM raw.order_reviews
    WHERE order_id IS NOT NULL
)
SELECT *
FROM typed
QUALIFY row_number() OVER (
    PARTITION BY order_id
    ORDER BY review_answered_at DESC NULLS LAST, review_id
) = 1;

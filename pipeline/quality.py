"""
Data-quality step - automated checks on the modelled tables.

Each check is a SQL query that returns the number of BAD rows (0 = pass).
  error -> a failure stops the pipeline before export, so broken data
           never reaches the dashboard (keys, joins, row reconciliation)
  warn  -> logged but not blocking (business-rule anomalies that exist
           in the real source data and should be investigated)
"""

import logging

import duckdb

log = logging.getLogger(__name__)

# (severity, check name, SQL returning count of violating rows)
CHECKS = [
    # Primary keys are unique and not null
    ("error", "dim_customers.customer_key unique",
     "SELECT count(*) - count(DISTINCT customer_key) FROM marts.dim_customers"),
    ("error", "dim_products.product_id unique",
     "SELECT count(*) - count(DISTINCT product_id) FROM marts.dim_products"),
    ("error", "dim_sellers.seller_id unique",
     "SELECT count(*) - count(DISTINCT seller_id) FROM marts.dim_sellers"),
    ("error", "fct_orders.order_id unique",
     "SELECT count(*) - count(DISTINCT order_id) FROM marts.fct_orders"),
    ("error", "fct_order_items PK unique",
     "SELECT count(*) - count(DISTINCT (order_id, order_item_id)) FROM marts.fct_order_items"),
    ("error", "fct_orders.order_id not null",
     "SELECT count(*) FROM marts.fct_orders WHERE order_id IS NULL"),

    # Referential integrity (every fact row points at an existing dimension row)
    ("error", "fct_orders -> dim_customers",
     """SELECT count(*) FROM marts.fct_orders f
        LEFT JOIN marts.dim_customers d USING (customer_key)
        WHERE d.customer_key IS NULL"""),
    ("error", "fct_order_items -> dim_products",
     """SELECT count(*) FROM marts.fct_order_items f
        LEFT JOIN marts.dim_products d USING (product_id)
        WHERE d.product_id IS NULL"""),
    ("error", "fct_order_items -> dim_sellers",
     """SELECT count(*) FROM marts.fct_order_items f
        LEFT JOIN marts.dim_sellers d USING (seller_id)
        WHERE d.seller_id IS NULL"""),
    ("error", "fct_order_items -> fct_orders",
     """SELECT count(*) FROM marts.fct_order_items i
        LEFT JOIN marts.fct_orders o USING (order_id)
        WHERE o.order_id IS NULL"""),

    # Business rules
    ("warn", "item price > 0",
     "SELECT count(*) FROM marts.fct_order_items WHERE price <= 0"),
    ("warn", "freight >= 0",
     "SELECT count(*) FROM marts.fct_order_items WHERE freight_value < 0"),
    ("warn", "review score between 1 and 5",
     "SELECT count(*) FROM marts.fct_orders WHERE review_score NOT BETWEEN 1 AND 5"),
    ("warn", "delivered date not before purchase",
     "SELECT count(*) FROM marts.fct_orders WHERE delivered_at < purchased_at"),
    ("warn", "valid order_status",
     """SELECT count(*) FROM marts.fct_orders WHERE order_status NOT IN
        ('delivered','shipped','canceled','unavailable','invoiced',
         'processing','created','approved')"""),

    # Reconciliation: nothing lost between raw and staging
    ("error", "all raw orders reach the mart",
     """SELECT (SELECT count(DISTINCT order_id) FROM raw.orders)
             - (SELECT count(*) FROM marts.fct_orders)"""),
]


class DataQualityError(Exception):
    pass


def run_checks(con: duckdb.DuckDBPyConnection) -> list[tuple[str, str, int]]:
    results = []
    for severity, name, sql in CHECKS:
        bad_rows = con.execute(sql).fetchone()[0]
        status = "PASS" if bad_rows == 0 else severity.upper()
        log.info("[%-5s] %-40s bad rows: %s", status, name, bad_rows)
        results.append((severity, name, bad_rows))

    errors = [name for severity, name, bad in results if bad and severity == "error"]
    warnings = [name for severity, name, bad in results if bad and severity == "warn"]
    if errors:
        raise DataQualityError(f"{len(errors)} blocking check(s) failed: {errors}")
    log.info("Data-quality: %d checks, %d warning(s), 0 errors",
             len(results), len(warnings))
    return results

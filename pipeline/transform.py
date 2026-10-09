"""
Transform step - run the SQL models in ./sql/ in layer order.

    raw  ->  staging (typed, cleaned, deduplicated)  ->  marts (star schema)

Files inside each layer run in alphabetical order, so prefix them with
numbers when one model depends on another.
"""

import logging
from pathlib import Path

import duckdb

log = logging.getLogger(__name__)

LAYERS = ["staging", "marts"]


def transform(con: duckdb.DuckDBPyConnection, sql_dir: Path) -> None:
    for layer in LAYERS:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {layer}")
        for sql_file in sorted((sql_dir / layer).glob("*.sql")):
            log.info("Running %s/%s", layer, sql_file.name)
            con.execute(sql_file.read_text(encoding="utf-8"))
    log.info("Transform complete")

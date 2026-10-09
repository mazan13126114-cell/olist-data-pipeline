"""
Load step - copy the raw CSVs into the `raw` schema of a DuckDB warehouse.

Every table is fully reloaded on each run (idempotent), and two audit
columns are added so you can see where and when each row came from.
"""

import logging
from pathlib import Path

import duckdb

from pipeline.extract import RAW_FILES

log = logging.getLogger(__name__)


def load(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> dict[str, int]:
    """Load every raw CSV into raw.<table>. Returns row counts per table."""
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    counts = {}

    for file_name, table in RAW_FILES.items():
        path = (raw_dir / file_name).as_posix()
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.{table} AS
            SELECT
                *,
                '{file_name}'      AS _source_file,
                current_timestamp  AS _loaded_at
            FROM read_csv_auto('{path}', header = true, all_varchar = true)
        """)
        counts[table] = con.execute(f"SELECT count(*) FROM raw.{table}").fetchone()[0]
        log.info("Loaded raw.%-22s %10s rows", table, f"{counts[table]:,}")

    return counts

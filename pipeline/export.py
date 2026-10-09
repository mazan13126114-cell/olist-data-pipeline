"""
Export step - write the mart tables to Parquet + CSV so Power BI / Tableau /
Excel can connect to them without needing DuckDB.
"""

import logging
from pathlib import Path

import duckdb

log = logging.getLogger(__name__)


def export(con: duckdb.DuckDBPyConnection, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = [row[0] for row in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'marts' ORDER BY table_name"
    ).fetchall()]

    for table in tables:
        for fmt in ("parquet", "csv"):
            path = (out_dir / f"{table}.{fmt}").as_posix()
            options = "FORMAT parquet" if fmt == "parquet" else "FORMAT csv, HEADER"
            con.execute(f"COPY marts.{table} TO '{path}' ({options})")
        log.info("Exported marts.%s", table)

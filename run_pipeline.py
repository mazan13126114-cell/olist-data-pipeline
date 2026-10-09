"""
Olist E-Commerce ELT pipeline - orchestrator
--------------------------------------------
Runs every step in order and logs to the console and to logs/pipeline.log:

    extract (Kaggle API) -> load (DuckDB raw) -> transform (SQL staging + marts)
    -> data-quality checks -> export (Parquet / CSV for BI)

Usage:
    python run_pipeline.py                 # full run
    python run_pipeline.py --skip-extract  # CSVs already in data/raw/
    python run_pipeline.py --force-download
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import duckdb

from pipeline.export import export
from pipeline.extract import extract
from pipeline.load import load
from pipeline.quality import DataQualityError, run_checks
from pipeline.transform import transform

# --- Config ----------------------------------------------------------------
ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "data" / "warehouse.duckdb"
SQL_DIR = ROOT / "sql"
OUTPUT_DIR = ROOT / "output"
LOG_FILE = ROOT / "logs" / "pipeline.log"


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)-18s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout),
                  logging.FileHandler(LOG_FILE, encoding="utf-8")],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Olist ELT pipeline")
    parser.add_argument("--skip-extract", action="store_true",
                        help="don't call the Kaggle API; use files in data/raw/")
    parser.add_argument("--force-download", action="store_true",
                        help="re-download from Kaggle even if files exist")
    args = parser.parse_args()

    setup_logging()
    log = logging.getLogger("pipeline")
    started = time.perf_counter()
    log.info("=== Pipeline started ===")

    try:
        if not args.skip_extract:
            extract(RAW_DIR, force=args.force_download)

        with duckdb.connect(str(WAREHOUSE)) as con:
            load(con, RAW_DIR)
            transform(con, SQL_DIR)
            run_checks(con)
            export(con, OUTPUT_DIR)
    except DataQualityError as e:
        log.error("Pipeline stopped by data-quality gate: %s", e)
        return 1
    except Exception:
        log.exception("Pipeline failed")
        return 1

    log.info("=== Pipeline finished in %.1fs ===", time.perf_counter() - started)
    return 0


if __name__ == "__main__":
    sys.exit(main())

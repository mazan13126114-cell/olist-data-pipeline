# Olist E-Commerce Data Pipeline

An automated ELT pipeline that turns the raw **Brazilian E-Commerce (Olist)**
Kaggle dataset into a clean, query-ready star schema, with data-quality
gates and BI-ready exports.

## Problem

A multi-seller marketplace (Olist) has ~100k orders spread across nine raw
CSVs (customers, orders, items, payments, reviews, products, sellers,
geolocation). Before anyone can build a dashboard or answer a business
question reliably, the data needs to be extracted, loaded, cleaned,
modelled into a sensible schema, and **checked for integrity** — every run,
automatically, not by eyeballing a spreadsheet.

## Data

**Brazilian E-Commerce Public Dataset by Olist** - Kaggle
(`olistbr/brazilian-ecommerce`). ~100k orders, Oct 2016 - Oct 2018, with
customer location, order items, payments, reviews and products.

> Raw data is **not** committed (see `.gitignore`). The pipeline downloads
> it itself via the Kaggle API (see **How to run**).

## Architecture

```
Kaggle API                 DuckDB                SQL models            Quality gate         BI tools
┌──────────┐  extract   ┌──────────┐  transform ┌───────────┐  checks ┌──────────┐ export ┌─────────────┐
│ 9 raw    │ ─────────► │ raw.*    │ ─────────► │ staging.* │ ──────► │ marts.*  │ ─────► │ Parquet/CSV │
│ CSVs     │   load     │ (typed)  │            │ (cleaned) │  gate   │ (star    │        │ Power BI /  │
└──────────┘            └──────────┘            └───────────┘         │ schema)  │        │ Tableau     │
                                                                        └──────────┘        └─────────────┘
```

Everything runs locally against an embedded **DuckDB** warehouse file — no
server to install, no cloud account needed, and it's fast enough to
re-run the full ~100k-order pipeline in seconds.

## Pipeline stages (`run_pipeline.py`)

1. **Extract** (`pipeline/extract.py`) - downloads the dataset via the
   Kaggle API into `data/raw/` (skipped automatically if the files are
   already there).
2. **Load** (`pipeline/load.py`) - loads every raw CSV as-is into a `raw`
   schema in DuckDB, tagging each row with its source file and load time.
3. **Transform** (`pipeline/transform.py`) - runs the SQL models in
   `sql/staging/` (typing, trimming, deduplication, Portuguese -> English
   category translation) then `sql/marts/` (star schema: `dim_customers`,
   `dim_products`, `dim_sellers`, `dim_date`, `fct_orders`,
   `fct_order_items`, plus a pre-aggregated `agg_monthly_kpis` table).
4. **Data quality** (`pipeline/quality.py`) - 16 automated checks: primary
   key uniqueness, referential integrity between facts and dimensions, row
   reconciliation against the raw data, and business rules (positive
   prices, valid review scores, valid order statuses, delivery dates that
   make sense). Key/integrity checks are **blocking** - the pipeline stops
   before export if any fail; business-rule anomalies are logged as
   warnings so known quirks in the real data don't halt the run.
5. **Export** (`pipeline/export.py`) - writes every mart table to
   `output/` as both Parquet (fast, typed) and CSV (universal), ready to
   plug into Power BI, Tableau, or pandas.

## How to run

```bash
pip install -r requirements.txt

# One-time Kaggle setup: Kaggle account -> Settings -> API -> Create New Token,
# save the downloaded kaggle.json to ~/.kaggle/kaggle.json

python run_pipeline.py
# or, if you already downloaded the CSVs into data/raw/ yourself:
python run_pipeline.py --skip-extract
```

Logs are written to the console and to `logs/pipeline.log`. Results land in
`data/warehouse.duckdb` (queryable directly) and `output/*.parquet` / `*.csv`.

## What's in here

| Path | Purpose |
|------|---------|
| `run_pipeline.py` | Orchestrator - runs every stage in order, handles logging and exit codes |
| `pipeline/extract.py` | Kaggle API download |
| `pipeline/load.py` | Raw CSV -> DuckDB `raw` schema |
| `pipeline/transform.py` | Runs the SQL models in `sql/` |
| `pipeline/quality.py` | Automated data-quality checks |
| `pipeline/export.py` | Mart tables -> Parquet / CSV |
| `sql/staging/` | Cleaning & typing models, one file per raw table |
| `sql/marts/` | Star-schema dimension, fact and aggregate models |

## Design decisions

- **DuckDB** instead of a hosted warehouse: zero setup, runs anywhere,
  still real SQL (window functions, `QUALIFY`, etc.) - the same modelling
  patterns transfer directly to Snowflake/BigQuery/Postgres.
- **SQL-first transforms** (not pandas) so the transformation logic is
  transparent, versionable, and reads like what a dbt project would
  produce, without needing dbt itself for a solo project this size.
- **Idempotent, full-refresh loads**: every run rebuilds every table from
  the raw CSVs (`CREATE OR REPLACE TABLE`), so there's no partial-state
  risk and reruns are always safe.
- **Blocking vs. warning checks**: structural problems (duplicate keys,
  orphaned foreign keys) should never silently reach a dashboard; messy
  but harmless real-world rows (a handful of invalid review scores) are
  surfaced, not hidden, without stopping a working pipeline.

## Tech

Python · DuckDB · SQL · pandas · Kaggle API · Parquet

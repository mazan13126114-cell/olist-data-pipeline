"""
Extract step - download the Olist dataset from Kaggle.

Uses the official Kaggle API. Needs a Kaggle API token at
~/.kaggle/kaggle.json (Kaggle > Settings > API > Create New Token).
If the CSVs are already in ./data/raw/, the download is skipped.
"""

import logging
from pathlib import Path

log = logging.getLogger(__name__)

KAGGLE_DATASET = "olistbr/brazilian-ecommerce"

# File name in the Kaggle download -> table name in the warehouse
RAW_FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}


def missing_files(raw_dir: Path) -> list[str]:
    return [f for f in RAW_FILES if not (raw_dir / f).exists()]


def extract(raw_dir: Path, force: bool = False) -> None:
    """Download and unzip the dataset into raw_dir (skipped if already present)."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    if not force and not missing_files(raw_dir):
        log.info("All %d raw files already present - skipping download", len(RAW_FILES))
        return

    # Imported here so the rest of the pipeline works without Kaggle credentials
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    log.info("Downloading %s from Kaggle ...", KAGGLE_DATASET)
    api.dataset_download_files(KAGGLE_DATASET, path=str(raw_dir), unzip=True, quiet=False)

    still_missing = missing_files(raw_dir)
    if still_missing:
        raise FileNotFoundError(f"Download finished but files are missing: {still_missing}")
    log.info("Extract complete")

"""
setup_bq.py
===========
Idempotently creates the three BigQuery datasets and all raw-layer tables
defined in sql/ddl_raw.sql.

Usage:
    python scripts/setup_bq.py

Requires:
    GOOGLE_APPLICATION_CREDENTIALS and GCP_PROJECT_ID in .env
"""

import os
import pathlib
from dotenv import load_dotenv
from google.cloud import bigquery

# ── Load env ────────────────────────────────────────────────────────────────
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
LOCATION   = os.environ.get("BQ_LOCATION", "US")
DATASETS   = [
    os.environ.get("BQ_DATASET_RAW",     "retail_raw"),
    os.environ.get("BQ_DATASET_STAGING", "retail_staging"),
    os.environ.get("BQ_DATASET_MARTS",   "retail_marts"),
]

# ── Client ───────────────────────────────────────────────────────────────────
client = bigquery.Client(project=PROJECT_ID)


def create_dataset(dataset_id: str) -> None:
    """Create a BQ dataset if it does not already exist."""
    full_id = f"{PROJECT_ID}.{dataset_id}"
    dataset  = bigquery.Dataset(full_id)
    dataset.location = LOCATION
    dataset.description = f"DWH Midterm – {dataset_id} layer"
    client.create_dataset(dataset, exists_ok=True)
    print(f"  ✅ Dataset ready: {full_id}")


def run_ddl_file(sql_path: pathlib.Path) -> None:
    """Execute a DDL SQL file statement-by-statement."""
    sql = sql_path.read_text(encoding="utf-8")
    # Split on semicolons; keep only non-empty statements
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        # Strip leading comment lines to check if real SQL remains
        code_lines = [ln for ln in stmt.splitlines() if not ln.strip().startswith("--")]
        code_body  = "\n".join(code_lines).strip()
        if not code_body:
            continue
        job = client.query(stmt)
        job.result()  # wait
        # Find first non-comment, non-blank line for the log label
        label = next((ln.strip() for ln in stmt.splitlines()
                      if ln.strip() and not ln.strip().startswith("--")), stmt)[:80]
        print(f"  ✅ Executed: {label}...")


def main() -> None:
    print("\n🔧 Step 1 – Creating BigQuery datasets")
    for ds in DATASETS:
        create_dataset(ds)

    sql_dir = pathlib.Path(__file__).parent.parent / "sql"

    print("\n🔧 Step 2 – Creating raw-layer tables")
    run_ddl_file(sql_dir / "ddl_raw.sql")

    print("\n🎉 BigQuery setup complete! (Staging and Marts will be built by dbt)\n")


if __name__ == "__main__":
    main()

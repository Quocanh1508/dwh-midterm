"""
seed_data.py
============
Seeds the retail_raw BigQuery dataset by copying rows from the public
BigQuery dataset `bigquery-public-data.thelook_ecommerce` (free to query).

Usage:
    python scripts/seed_data.py [--limit N]

    --limit N   max rows per table (default: 50000)

The script uses INSERT ... SELECT so no local files or GCS needed.
All data stays within BigQuery — 0 egress charges.
"""

import argparse
import os
import pathlib
from dotenv import load_dotenv
from google.cloud import bigquery

# ── Load env ────────────────────────────────────────────────────────────────
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

PROJECT_ID   = os.environ["GCP_PROJECT_ID"]
DATASET_RAW  = os.environ.get("BQ_DATASET_RAW", "retail_raw")
SOURCE_DS    = "bigquery-public-data.thelook_ecommerce"

client = bigquery.Client(project=PROJECT_ID)


# Each entry: (target_table, source_table, select_columns)
SEED_PLAN = [
    (
        "orders",
        f"`{SOURCE_DS}.orders`",
        """
            CAST(order_id      AS STRING),
            CAST(user_id       AS STRING),
            status,
            gender,
            created_at,
            returned_at,
            shipped_at,
            delivered_at,
            num_of_item,
            CURRENT_TIMESTAMP()   AS _loaded_at
        """,
    ),
    (
        "order_items",
        f"`{SOURCE_DS}.order_items`",
        """
            CAST(id                AS STRING),
            CAST(order_id          AS STRING),
            CAST(user_id           AS STRING),
            CAST(product_id        AS STRING),
            CAST(inventory_item_id AS STRING),
            status,
            created_at,
            shipped_at,
            delivered_at,
            returned_at,
            sale_price,
            CURRENT_TIMESTAMP()   AS _loaded_at
        """,
    ),
    (
        "products",
        f"`{SOURCE_DS}.products`",
        """
            CAST(id AS STRING),
            cost,
            category,
            name,
            brand,
            retail_price,
            department,
            sku,
            CAST(distribution_center_id AS STRING),
            CURRENT_TIMESTAMP()   AS _loaded_at
        """,
    ),
    (
        "users",
        f"`{SOURCE_DS}.users`",
        """
            CAST(id AS STRING),
            first_name,
            last_name,
            email,
            age,
            gender,
            state,
            street_address,
            postal_code,
            city,
            country,
            latitude,
            longitude,
            traffic_source,
            created_at,
            CURRENT_TIMESTAMP()   AS _loaded_at
        """,
    ),
]


def truncate_table(table_id: str) -> None:
    sql = f"TRUNCATE TABLE `{PROJECT_ID}.{DATASET_RAW}.{table_id}`"
    client.query(sql).result()
    print(f"  🗑️  Truncated {DATASET_RAW}.{table_id}")


def seed_table(table_id: str, source: str, cols: str, limit: int) -> None:
    target = f"`{PROJECT_ID}.{DATASET_RAW}.{table_id}`"
    sql = f"""
        INSERT INTO {target}
        SELECT
            {cols}
        FROM {source}
        LIMIT {limit}
    """
    job = client.query(sql)
    job.result()
    print(f"  ✅ Seeded {DATASET_RAW}.{table_id}  ({limit:,} rows max)")


def main(limit: int) -> None:
    print(f"\n🌱 Seeding retail_raw from {SOURCE_DS}  (limit={limit:,}/table)\n")
    for table_id, source, cols in SEED_PLAN:
        truncate_table(table_id)
        seed_table(table_id, source, cols, limit)

    print("\n📊 Row counts after seeding:")
    for table_id, _, _ in SEED_PLAN:
        row = next(
            client.query(
                f"SELECT COUNT(*) AS n FROM `{PROJECT_ID}.{DATASET_RAW}.{table_id}`"
            ).result()
        )
        print(f"   {DATASET_RAW}.{table_id}: {row.n:,} rows")

    print("\n🎉 Seed complete!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed retail_raw from public BQ dataset")
    parser.add_argument("--limit", type=int, default=50_000, help="Max rows per table")
    args = parser.parse_args()
    main(args.limit)

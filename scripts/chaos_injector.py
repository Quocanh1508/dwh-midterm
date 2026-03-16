import os
import sys
import pathlib
import argparse
from dotenv import load_dotenv
from google.cloud import bigquery

# Load environment
root_dir = pathlib.Path(__file__).parent.parent
load_dotenv(root_dir / ".env")

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
DATASET_RAW = os.environ.get("BQ_DATASET_RAW", "retail_raw")

client = bigquery.Client(project=PROJECT_ID)

def inject_invalid_status():
    print("😈 Injecting Invalid Order Status...")
    sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_RAW}.orders` 
        (order_id, user_id, status, gender, created_at, num_of_item, _loaded_at)
        VALUES 
        ('CHAOS_STATUS_666', '12345', 'HACKED_BY_PROFESSOR', 'M', CURRENT_TIMESTAMP(), 1, CURRENT_TIMESTAMP())
    """
    client.query(sql).result()
    print("✅ Success: This will trigger the dbt 'accepted_values' test failure on stg_orders.")

def inject_negative_quantity():
    print("😈 Injecting Negative Quantity...")
    sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_RAW}.orders` 
        (order_id, user_id, status, gender, created_at, num_of_item, _loaded_at)
        VALUES 
        ('CHAOS_QTY_777', '12345', 'Processing', 'M', CURRENT_TIMESTAMP(), -999, CURRENT_TIMESTAMP())
    """
    client.query(sql).result()
    print("✅ Success: This will trigger a failure in Great Expectations (Raw Checkpoint).")

def inject_orphan_product():
    print("😈 Injecting Orphaned Product (Missing Warehouse)...")
    sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_RAW}.products` 
        (id, name, distribution_center_id, _loaded_at)
        VALUES 
        ('CHAOS_PROD_888', 'Ghost Product', 'WA_99999', CURRENT_TIMESTAMP())
    """
    client.query(sql).result()
    print("✅ Success: This will trigger the dbt 'relationships' test failure in the Marts layer.")

def inject_impossible_location():
    print("😈 Injecting Impossible Warehouse Location...")
    sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_RAW}.distribution_centers` 
        (id, name, latitude, longitude, _loaded_at)
        VALUES 
        ('CHAOS_DC_999', 'Mars Station', 500.0, 999.0, CURRENT_TIMESTAMP())
    """
    client.query(sql).result()
    print("✅ Success: This would normally be caught by Great Expectations statistical range tests.")

def main():
    parser = argparse.ArgumentParser(description="Chaos Injector for Data Warehouse Testing")
    parser.add_argument("--mode", choices=["status", "quantity", "orphan", "location"], required=True, help="Type of failure to simulate")
    
    args = parser.parse_args()
    
    if args.mode == "status":
        inject_invalid_status()
    elif args.mode == "quantity":
        inject_negative_quantity()
    elif args.mode == "orphan":
        inject_orphan_product()
    elif args.mode == "location":
        inject_impossible_location()

if __name__ == "__main__":
    main()

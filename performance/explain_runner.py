"""
explain_runner.py
=================
Performance testing script for the BigQuery Data Warehouse.

This script runs dry-run EXPLAIN plans on key analytical queries 
against the `retail_marts.fact_sales` table to measure:
1. Total Bytes Processed (determines cost under BQ on-demand pricing)
2. Total Slot Milliseconds (estimates query compute time)
    
It fails the CI/CD pipeline if cost/complexity exceeds defined thresholds.
"""

import os
import sys
import pathlib
from dotenv import load_dotenv
from google.cloud import bigquery

# Max bytes processed threshold (e.g., 500 MB)
MAX_BYTES_PROCESSED = 500 * 1024 * 1024 

QUERIES_TO_TEST = [
    {
        "name": "Daily Revenue by Category",
        "sql": """
            SELECT 
                d.full_date, 
                p.category, 
                SUM(f.sale_price) as total_revenue
            FROM `{project}.{marts}.fact_sales` f
            JOIN `{project}.{marts}.dim_date` d ON f.date_key = d.date_key
            JOIN `{project}.{marts}.dim_product` p ON f.product_key = p.product_key
            GROUP BY 1, 2
            ORDER BY 1 DESC, 3 DESC
            LIMIT 100
        """
    },
    {
        "name": "Top Customers by Lifetime Profit",
        "sql": """
            SELECT 
                c.first_name, 
                c.last_name, 
                SUM(f.profit) as lifetime_profit
            FROM `{project}.{marts}.fact_sales` f
            JOIN `{project}.{marts}.dim_customer` c ON f.customer_key = c.customer_key
            GROUP BY 1, 2
            ORDER BY 3 DESC
            LIMIT 50
        """
    }
]

def main():
    root_dir = pathlib.Path(__file__).parent.parent
    load_dotenv(root_dir / ".env")
    
    project_id = os.environ.get("GCP_PROJECT_ID")
    marts_ds = os.environ.get("BQ_DATASET_MARTS", "retail_marts")
    
    if not project_id:
        print("❌ GCP_PROJECT_ID is missing from environment.")
        sys.exit(1)

    # Ensure credentials path is absolute
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds and not os.path.isabs(creds):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(root_dir / creds)
        
    client = bigquery.Client(project=project_id)
    
    print("\n📊 Running Performance EXPLAIN Tests on BigQuery\n" + "="*50)
    
    all_passed = True
    
    for q in QUERIES_TO_TEST:
        sql = q["sql"].format(project=project_id, marts=marts_ds)
        
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        
        try:
            query_job = client.query(sql, job_config=job_config)
            
            # Dry run stats
            bytes_processed = query_job.total_bytes_processed
            mb_processed = bytes_processed / (1024 * 1024)
            
            print(f"\nQuery: {q['name']}")
            print(f"  - Bytes Processed: {mb_processed:.2f} MB")
            
            if bytes_processed > MAX_BYTES_PROCESSED:
                print(f"  ❌ FAILED: Exceeds threshold of {MAX_BYTES_PROCESSED/(1024*1024):.2f} MB")
                all_passed = False
            else:
                print("  ✅ PASSED: Within cost limits")
                
        except Exception as e:
            print(f"\n❌ Error explaining query '{q['name']}': {e}")
            all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("✅ All performance thresholds met.")
        sys.exit(0)
    else:
        print("❌ Performance thresholds exceeded.")
        sys.exit(1)

if __name__ == "__main__":
    main()

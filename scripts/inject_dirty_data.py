import os
import pathlib
from dotenv import load_dotenv
from google.cloud import bigquery

# Load environment variables
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
DATASET_RAW = os.environ.get("BQ_DATASET_RAW", "retail_raw")

client = bigquery.Client(project=PROJECT_ID)

def inject_dirty_data():
    print("😈 Starting Dirty Data Injection...")
    
    # Insert an order with an invalid status that will break dbt's accepted_values test
    # and a negative num_of_items that might break other logic
    sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_RAW}.orders` 
        (order_id, user_id, status, gender, created_at, num_of_item, _loaded_at)
        VALUES 
        ('DIRTY_ORDER_99999', '12345', 'HACKED_BY_PROFESSOR', 'M', CURRENT_TIMESTAMP(), -500, CURRENT_TIMESTAMP())
    """
    
    job = client.query(sql)
    job.result()
    
    print(f"✅ Successfully injected 1 row into {DATASET_RAW}.orders with status='HACKED_BY_PROFESSOR'")
    print("This will cause the dbt test 'accepted_values' on stg_orders to fail in the CI/CD pipeline!")

if __name__ == "__main__":
    inject_dirty_data()

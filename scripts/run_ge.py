"""
run_ge.py
=========
Helper script to run Great Expectations checkpoints programmatically.
"""
import sys
import pathlib
import os
from dotenv import load_dotenv

import great_expectations as gx
from great_expectations.checkpoint import SimpleCheckpoint

def run_checkpoint(name: str):
    root_dir = pathlib.Path(__file__).parent.parent
    load_dotenv(root_dir / ".env")

    context = gx.get_context(context_root_dir=str(root_dir / "great_expectations"))
    
    # Configure the checkpoint programmatically based on name
    if name == "raw_checkpoint":
        asset_name = "retail_raw.orders"
        suite_name = "raw_orders_suite"
    elif name == "mart_checkpoint":
        asset_name = "retail_marts.fact_sales"
        suite_name = "mart_fact_sales_suite"
    else:
        print(f"Unknown checkpoint: {name}")
        sys.exit(1)

    checkpoint_config = {
        "name": name,
        "config_version": 1.0,
        "class_name": "SimpleCheckpoint",
        "run_name_template": f"%Y%m%d-%H%M%S-{name}",
        "validations": [
            {
                "batch_request": {
                    "datasource_name": "retail_dwh",
                    "data_connector_name": "default_configured_data_connector_name",
                    "data_asset_name": asset_name,
                    "data_connector_query": {"index": -1}
                },
                "expectation_suite_name": suite_name
            }
        ]
    }

    checkpoint = SimpleCheckpoint(
        data_context=context,
        **checkpoint_config
    )

    print(f"🚀 Running checkpoint: {name}")
    results = checkpoint.run()
    if not results["success"]:
        print(f"❌ Checkpoint {name} failed!")
        sys.exit(1)
    
    print(f"✅ Checkpoint {name} passed!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_ge.py <checkpoint_name>")
        sys.exit(1)
    run_checkpoint(sys.argv[1])

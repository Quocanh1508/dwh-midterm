"""
generate_expectations.py
========================
Generates Great Expectations suite definitions programmatically and saves
them to the `great_expectations/expectations/` folder.

This replaces the need to run the interactive GE Jupyter Notebooks.

Expectation Suites:
  1. raw_orders_suite
     - expect_table_row_count_to_be_between
     - expect_column_values_to_not_be_null (order_id)
     - expect_column_values_to_be_unique (order_id)

  2. mart_fact_sales_suite
     - expect_table_row_count_to_be_between
     - expect_column_values_to_not_be_null (order_item_id)
     - expect_column_values_to_be_in_set (order_status)
     - expect_column_values_to_be_between (profit_margin_pct)
"""

import json
import os
import pathlib

suites = {
    "raw_orders_suite": {
        "data_asset_type": None,
        "expectation_suite_name": "raw_orders_suite",
        "expectations": [
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {
                    "min_value": 0,
                    "max_value": 5000000
                },
                "meta": {}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {
                    "column": "order_id"
                },
                "meta": {}
            },
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {
                    "column": "order_id"
                },
                "meta": {}
            }
        ],
        "ge_cloud_id": None,
        "meta": {
            "great_expectations_version": "0.18.19"
        }
    },
    "mart_fact_sales_suite": {
        "data_asset_type": None,
        "expectation_suite_name": "mart_fact_sales_suite",
        "expectations": [
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {
                    "min_value": 0,
                    "max_value": 5000000
                },
                "meta": {}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {
                    "column": "order_item_id"
                },
                "meta": {}
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "order_status",
                    "value_set": [
                        "CANCELLED",
                        "COMPLETE",
                        "PROCESSING",
                        "RETURNED",
                        "SHIPPED"
                    ]
                },
                "meta": {}
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "profit_margin_pct",
                    "min_value": -100,
                    "max_value": 100
                },
                "meta": {}
            }
        ],
        "ge_cloud_id": None,
        "meta": {
            "great_expectations_version": "0.18.19"
        }
    }
}

def main():
    base_dir = pathlib.Path(__file__).parent.parent / "great_expectations" / "expectations"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    for suite_name, suite_data in suites.items():
        file_path = base_dir / f"{suite_name}.json"
        with open(file_path, "w") as f:
            json.dump(suite_data, f, indent=2)
        print(f"✅ Generated {suite_name}.json at {file_path}")

if __name__ == "__main__":
    main()

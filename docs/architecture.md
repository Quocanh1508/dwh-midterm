# Data Warehouse Testing – Architecture

## Overview

Three-layer BigQuery schema implementing the Kimball dimensional model:

```
Public BQ Dataset (source)
        │
        ▼
┌─────────────────────┐
│   retail_raw        │  Raw ingestion (exact copy of source)
│   orders, products, │
│   customers         │
└─────────┬───────────┘
          │  dbt staging models
          ▼
┌─────────────────────┐
│  retail_staging     │  Cleaned, typed, deduplicated views
│  stg_orders         │
│  stg_products       │
│  stg_customers      │
└─────────┬───────────┘
          │  dbt mart models
          ▼
┌─────────────────────────────────────┐
│  retail_marts                       │  Star schema
│  fact_sales                         │
│  dim_customer, dim_product,         │
│  dim_date                           │
└─────────────────────────────────────┘
```

## Tools & Rationale

| Layer          | Tool                            | Why Free                                 |
|----------------|---------------------------------|------------------------------------------|
| Cloud DW       | Google BigQuery (free tier)     | 1 TB queries/mo, 10 GB storage           |
| Transformations| dbt-core + dbt-bigquery         | 100 % open-source                        |
| Quality Tests  | Great Expectations 0.18         | Open-source; YAML/JSON expectation suites|
| CI/CD          | GitHub Actions                  | Free for public repos                    |
| Performance    | BQ EXPLAIN + JMeter             | Both free/open-source                    |
| Alerting       | Discord webhook                 | Free tier, no bot required               |

## Testing Strategy (per doc)

1. **Accuracy** – GE suite compares raw vs mart aggregated totals  
2. **Completeness** – not_null + GE completeness checks on all key columns  
3. **Uniqueness** – dbt `unique` tests + GE `expect_column_values_to_be_unique`  
4. **Referential Integrity** – dbt `relationships` test (orders → customers)  
5. **Performance** – BQ EXPLAIN bytes/slot usage; JMeter JDBC load test  
6. **Regression** – full dbt + GE pipeline runs on every PR via GitHub Actions  

# 🏪 DWH Midterm – Cloud Data Warehouse Testing Framework

> Automated, CI/CD-driven data warehouse testing on **Google BigQuery (free tier)**  
> using **dbt-core**, **Great Expectations**, and **GitHub Actions** — $0 cost.

---

## 📐 Architecture

```
Public BigQuery Dataset (thelook_ecommerce)
          │
          ▼  seed_data.py
   retail_raw  (BigQuery dataset)
          │
          ▼  dbt staging models
   retail_staging  (views)
          │
          ▼  dbt mart models
   retail_marts  (fact_sales, dim_customer, dim_product, dim_date)
```

See [`docs/architecture.md`](docs/architecture.md) for full detail.

---

## 🧰 Tech Stack

| Component       | Tool                              | Cost  |
|-----------------|-----------------------------------|-------|
| Cloud DW        | Google BigQuery                   | Free  |
| Transformations | dbt-core + dbt-bigquery           | Free  |
| Quality Tests   | Great Expectations 0.18           | Free  |
| CI/CD           | GitHub Actions                    | Free  |
| Performance     | BQ EXPLAIN + Apache JMeter        | Free  |
| Alerting        | Discord/Slack webhooks            | Free  |

---

## 📁 Project Structure

```
├── .github/workflows/      # CI (PR) and CD (main branch) pipelines
├── dbt/                    # dbt project – transformations & tests
│   ├── models/staging/     # stg_orders, stg_products, stg_customers
│   └── models/marts/       # fact_sales, dim_*, dim_date
├── great_expectations/     # GE expectations + checkpoints
├── performance/            # BQ EXPLAIN runner + JMeter plan
├── scripts/                # setup_bq.py, seed_data.py, alert_webhook.py
├── sql/                    # Raw DDL scripts (can run manually)
└── docs/                   # Architecture & setup docs
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- A [Google Cloud project](https://console.cloud.google.com/) with BigQuery API enabled
- A service-account JSON key with **BigQuery Data Editor + Job User** roles
- Git + GitHub account

### 2. Clone & Install

```bash
git clone https://github.com/<YOUR_USERNAME>/dwh-midterm.git
cd dwh-midterm

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env – fill in GCP_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS, DISCORD_WEBHOOK_URL
```

### 4. Bootstrap BigQuery

```bash
python scripts/setup_bq.py      # creates datasets
python scripts/seed_data.py     # loads sample retail data from public BQ dataset
```

### 5. Run dbt

```bash
cd dbt
dbt deps                        # install packages
dbt run   --profiles-dir .      # build staging + mart models
dbt test  --profiles-dir .      # run all quality tests
```

### 6. Run Great Expectations

```bash
cd ..
great_expectations checkpoint run raw_checkpoint
great_expectations checkpoint run mart_checkpoint
```

### 7. Performance Check

```bash
python performance/explain_runner.py
```

---

## 🔄 CI/CD

| Trigger         | Pipeline          | Steps                                      |
|-----------------|-------------------|--------------------------------------------|
| Pull Request    | `.github/workflows/ci.yml`  | dbt compile → dbt test → GE validate → alert |
| Push to `main`  | `.github/workflows/cd.yml`  | seed → dbt run → dbt test → GE → explain → alert |

### GitHub Secrets Required

| Secret                      | Value                                    |
|-----------------------------|------------------------------------------|
| `GCP_SA_KEY`                | Full contents of your service-account JSON |
| `GCP_PROJECT_ID`            | Your GCP project ID                       |
| `DISCORD_WEBHOOK_URL`       | Discord webhook URL                       |

---

## 📊 Testing Strategy

| Strategy             | Implementation                                          |
|----------------------|---------------------------------------------------------|
| Accuracy             | GE suite: raw vs mart aggregate comparison              |
| Completeness         | dbt `not_null` + GE completeness on key columns         |
| Uniqueness           | dbt `unique` + GE `expect_column_values_to_be_unique`   |
| Referential Integrity| dbt `relationships` test (orders → customers)           |
| Performance          | BQ EXPLAIN bytes/slot stats; JMeter JDBC load test      |
| Regression           | Full pipeline runs on every PR via GitHub Actions        |

---

## 📜 License

MIT – free for educational and commercial use.

import os
import pathlib
from dotenv import load_dotenv
import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.express as px

# ── Setup ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="DWH Midterm Dashboard", page_icon="🛒", layout="wide")

# Load environment using same .env as the pipeline
load_dotenv(pathlib.Path(__file__).parent / ".env")

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "YOUR_PROJECT_ID")
st.title(f"🛒 Retail Data Warehouse Dashboard")
st.markdown(f"**Project:** `{PROJECT_ID}` | **Marts Layer:** `{PROJECT_ID}.retail_marts`")
st.divider()

from google.oauth2 import service_account

# Initialize BigQuery Client
@st.cache_resource
def get_bq_client():
    try:
        # 1. Try Streamlit Cloud Secrets first
        if "gcp_service_account" in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"])
            )
            return bigquery.Client(credentials=credentials, project=PROJECT_ID)
        # 2. Fallback to Local Environment variables
        else:
            return bigquery.Client(project=PROJECT_ID)
    except Exception as e:
        st.error(f"Failed to initialize BigQuery client: {e}")
        st.info("Make sure .env is configured or Streamlit Secrets are set.")
        st.stop()

client = get_bq_client()

# ── Data Fetching ───────────────────────────────────────────────────────────
@st.cache_data(ttl=600)  # Cache queries for 10 minutes to save BQ costs
def load_kpis():
    query = f"""
        SELECT 
            COUNT(DISTINCT order_id) as total_orders,
            COUNT(DISTINCT customer_key) as total_customers,
            SUM(sale_price) as total_revenue,
            SUM(profit) as total_profit
        FROM `{PROJECT_ID}.retail_marts.fact_sales`
        WHERE item_status != 'Cancelled' AND item_status != 'Returned'
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=600)
def load_sales_over_time():
    query = f"""
        SELECT 
            sale_date,
            SUM(sale_price) as daily_revenue,
            SUM(profit) as daily_profit
        FROM `{PROJECT_ID}.retail_marts.fact_sales`
        WHERE sale_date >= '2023-01-01' 
          AND item_status != 'Cancelled' AND item_status != 'Returned'
        GROUP BY sale_date
        ORDER BY sale_date
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=600)
def load_top_categories():
    query = f"""
        SELECT 
            p.category,
            SUM(f.sale_price) as revenue
        FROM `{PROJECT_ID}.retail_marts.fact_sales` f
        JOIN `{PROJECT_ID}.retail_marts.dim_product` p ON f.product_key = p.product_key
        WHERE f.item_status != 'Cancelled' AND f.item_status != 'Returned'
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 10
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=600)
def load_customer_demographics():
    query = f"""
        SELECT 
            gender,
            traffic_source,
            COUNT(customer_key) as customer_count
        FROM `{PROJECT_ID}.retail_marts.dim_customer`
        GROUP BY 1, 2
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=600)
def load_order_status():
    query = f"""
        SELECT 
            order_status,
            COUNT(DISTINCT order_id) as order_count
        FROM `{PROJECT_ID}.retail_marts.fact_sales`
        GROUP BY 1
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=3600)
def load_schema():
    query = f"""
        SELECT 
            table_name, 
            column_name, 
            data_type 
        FROM `{PROJECT_ID}.retail_marts.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name IN ('dim_customer', 'dim_product', 'fact_sales')
        ORDER BY table_name, ordinal_position
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)

# ── Render Dashboard ────────────────────────────────────────────────────────
with st.spinner("Loading Data Warehouse Metrics form BigQuery..."):
    try:
        df_kpis = load_kpis()
        df_time = load_sales_over_time()
        df_cat  = load_top_categories()
        df_demo = load_customer_demographics()
        df_status = load_order_status()
        df_schema = load_schema()
    except Exception as e:
        st.error(f"Error querying BigQuery: {e}")
        st.stop()

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"${df_kpis['total_revenue'].iloc[0]:,.0f}")
with col2:
    st.metric("Total Profit", f"${df_kpis['total_profit'].iloc[0]:,.0f}")
with col3:
    st.metric("Total Orders", f"{df_kpis['total_orders'].iloc[0]:,}")
with col4:
    st.metric("Active Customers", f"{df_kpis['total_customers'].iloc[0]:,}")

st.divider()

# Charts
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Revenue Over Time (2023+)")
    fig_time = px.line(
        df_time, 
        x='sale_date', y=['daily_revenue', 'daily_profit'],
        labels={'value': 'USD', 'sale_date': 'Date', 'variable': 'Metric'},
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    st.plotly_chart(fig_time, use_container_width=True)

with col_right:
    st.subheader("🛍️ Top 10 Categories")
    fig_cat = px.bar(
        df_cat, 
        x='revenue', y='category', 
        orientation='h',
        labels={'revenue': 'Revenue ($)', 'category': 'Category'},
        color='revenue', color_continuous_scale='Blues'
    )
    fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_cat, use_container_width=True)

st.divider()

# Secondary Charts Layer
col_lower1, col_lower2 = st.columns(2)

with col_lower1:
    st.subheader("👥 Customer Traffic Sources")
    fig_demo = px.sunburst(
        df_demo, 
        path=['gender', 'traffic_source'], 
        values='customer_count',
        color='gender',
        color_discrete_map={'M': '#1f77b4', 'F': '#e377c2'}
    )
    st.plotly_chart(fig_demo, use_container_width=True)

with col_lower2:
    st.subheader("📦 Overall Order Status")
    fig_status = px.pie(
        df_status, 
        names='order_status', 
        values='order_count',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_status.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_status, use_container_width=True)

st.divider()

# Schema Documentation Section
with st.expander("🔍 View Data Warehouse Schema (Marts Layer)"):
    st.markdown("Auto-generated documentation from BigQuery `INFORMATION_SCHEMA`")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown("**`fact_sales`**")
        st.dataframe(df_schema[df_schema['table_name'] == 'fact_sales'][['column_name', 'data_type']], hide_index=True)
    with col_s2:
        st.markdown("**`dim_customer`**")
        st.dataframe(df_schema[df_schema['table_name'] == 'dim_customer'][['column_name', 'data_type']], hide_index=True)
    with col_s3:
        st.markdown("**`dim_product`**")
        st.dataframe(df_schema[df_schema['table_name'] == 'dim_product'][['column_name', 'data_type']], hide_index=True)

st.divider()
st.caption("Data is pulled live from the Google BigQuery Data Warehouse `retail_marts` layer.")

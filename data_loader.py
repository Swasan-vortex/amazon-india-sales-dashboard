"""
data_loader.py - Data loading and preprocessing module for Amazon India Sales Analysis.
Academic Project: 4th-Year B.Tech Data Analytics Dashboard

Deployment-Ready Configuration:
- Supports local development (defaulting to local Excel file).
- Supports remote hosting via environment variables or Streamlit secrets (DATASET_URL / DATASET_PATH).
- Supports interactive file upload fallback when deployed without bundled dataset.
- Protects confidential company data (no dummy data, no hardcoded local paths).
"""

import os
import io
from typing import Optional, Tuple, Union, Any
import pandas as pd
import numpy as np
import streamlit as st

DEFAULT_FILE_NAME = "Amazon Sales Data India.xlsx"
EXPECTED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Category",
    "Product",
    "Quantity",
    "Unit_Price_INR",
    "Discount_Pct",
    "Total_Sales_INR",
    "Profit_INR",
    "Payment_Method",
    "Fulfillment",
    "Order_Status",
    "Ship_State",
]


def resolve_dataset_source() -> Tuple[Optional[str], Optional[str]]:
    """
    Identify and resolve the dataset source based on environment priority:
    1. Streamlit Secrets ('DATASET_URL' or 'DATASET_PATH')
    2. Environment Variables ('DATASET_URL' or 'DATASET_PATH')
    3. Local File in workspace ('Amazon Sales Data India.xlsx')

    Returns:
        (source_type, source_reference) e.g. ("local", "path/to/file.xlsx") or ("url", "https://...")
        or (None, None) if no dataset is configured or found on disk.
    """
    # 1. Check Streamlit Secrets (for Streamlit Community Cloud deployments)
    try:
        if hasattr(st, "secrets"):
            if "DATASET_URL" in st.secrets and str(st.secrets["DATASET_URL"]).strip():
                return "url", str(st.secrets["DATASET_URL"]).strip()
            if "DATASET_PATH" in st.secrets and str(st.secrets["DATASET_PATH"]).strip():
                path = str(st.secrets["DATASET_PATH"]).strip()
                if os.path.exists(path):
                    return "local", path
    except Exception:
        pass

    # 2. Check Environment Variables
    env_url = os.environ.get("DATASET_URL")
    if env_url and env_url.strip():
        return "url", env_url.strip()

    env_path = os.environ.get("DATASET_PATH")
    if env_path and env_path.strip() and os.path.exists(env_path.strip()):
        return "local", env_path.strip()

    # 3. Check Local File in Project Root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_relative = os.path.join(script_dir, DEFAULT_FILE_NAME)
    if os.path.exists(local_relative):
        return "local", local_relative

    if os.path.exists(DEFAULT_FILE_NAME):
        return "local", DEFAULT_FILE_NAME

    return None, None


@st.cache_data(show_spinner=False)
def load_and_preprocess_data(source: Any) -> pd.DataFrame:
    """
    Load Amazon India sales dataset from Excel and apply data cleaning and feature engineering.
    Accepts:
        - file path string
        - URL string
        - BytesIO buffer / bytes (from file_uploader)

    Cached with st.cache_data to ensure high dashboard performance.
    """
    if source is None:
        raise ValueError("No dataset source was provided to load_and_preprocess_data.")

    # Handle Bytes / BytesIO / UploadedFile
    if hasattr(source, "getvalue"):
        # Streamlit UploadedFile or BytesIO
        excel_buffer = io.BytesIO(source.getvalue())
        df = pd.read_excel(excel_buffer)
    elif isinstance(source, bytes):
        excel_buffer = io.BytesIO(source)
        df = pd.read_excel(excel_buffer)
    elif isinstance(source, str):
        if source.startswith(("http://", "https://")):
            # Remote URL (e.g. S3 presigned URL or Cloudflare R2 / Google Cloud Storage)
            df = pd.read_excel(source)
        else:
            if not os.path.exists(source):
                raise FileNotFoundError(
                    f"Dataset file not found at '{source}'. "
                    f"Please verify file location or configure DATASET_URL in Streamlit secrets."
                )
            df = pd.read_excel(source)
    else:
        # Fallback to direct read
        df = pd.read_excel(source)

    # Clean column names (strip whitespace)
    df.columns = df.columns.astype(str).str.strip()

    # Validate required schema
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(missing_cols)}. "
            f"Expected schema: {', '.join(EXPECTED_COLUMNS)}"
        )

    # Ensure Order_Date is datetime
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df = df.dropna(subset=["Order_Date"])

    # Feature Engineering for time-based analysis
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month
    df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
    df["Year_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str) + " " + df["Year"].astype(str)
    df["Day_Name"] = df["Order_Date"].dt.day_name()
    df["Day_Of_Week"] = df["Order_Date"].dt.dayofweek  # 0=Monday, 6=Sunday

    # Ensure numeric columns have correct data types
    numeric_cols = ["Quantity", "Unit_Price_INR", "Discount_Pct", "Total_Sales_INR", "Profit_INR"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Derived business metrics
    # Profit Margin % (handled safely against 0 sales)
    df["Profit_Margin_Pct"] = np.where(
        df["Total_Sales_INR"] > 0,
        (df["Profit_INR"] / df["Total_Sales_INR"]) * 100,
        0.0
    )

    # Gross Sales before discount
    df["Gross_Sales_INR"] = df["Quantity"] * df["Unit_Price_INR"]
    df["Discount_Amount_INR"] = df["Gross_Sales_INR"] - df["Total_Sales_INR"]

    # String column formatting
    categorical_cols = ["Category", "Product", "Payment_Method", "Fulfillment", "Order_Status", "Ship_State"]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Sort chronologically by Order_Date
    df = df.sort_values(by="Order_Date").reset_index(drop=True)

    return df


def get_filter_options(df: pd.DataFrame) -> dict:
    """
    Extract unique values for dropdown and multiselect filters.
    """
    return {
        "categories": sorted(df["Category"].dropna().unique().tolist()),
        "products": sorted(df["Product"].dropna().unique().tolist()),
        "fulfillments": sorted(df["Fulfillment"].dropna().unique().tolist()),
        "statuses": sorted(df["Order_Status"].dropna().unique().tolist()),
        "states": sorted(df["Ship_State"].dropna().unique().tolist()),
        "payments": sorted(df["Payment_Method"].dropna().unique().tolist()),
        "min_date": df["Order_Date"].min().date() if len(df) > 0 else None,
        "max_date": df["Order_Date"].max().date() if len(df) > 0 else None,
    }

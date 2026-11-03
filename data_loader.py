"""
data_loader.py - Data loading and preprocessing module for Amazon India Sales Analysis.
Academic Project: 4th-Year B.Tech Data Analytics Dashboard
"""

import os
import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data(show_spinner=False)
def load_and_preprocess_data(file_path: str = "Amazon Sales Data India.xlsx") -> pd.DataFrame:
    """
    Load Amazon India sales dataset from Excel and apply data cleaning and feature engineering.
    Cached with st.cache_data to ensure high dashboard performance.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}. Please check the file path.")

    # Load dataset
    df = pd.read_excel(file_path)

    # Clean column names (strip whitespace)
    df.columns = df.columns.str.strip()

    # Ensure Order_Date is datetime
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])

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
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Derived business metrics
    # Profit Margin % (handled safely against 0 sales)
    df["Profit_Margin_Pct"] = np.where(
        df["Total_Sales_INR"] > 0,
        (df["Profit_INR"] / df["Total_Sales_INR"]) * 100,
        0.0
    )

    # Gross Sales before discount
    # Total_Sales_INR = Quantity * Unit_Price_INR * (1 - Discount_Pct)
    # Gross_Amount = Quantity * Unit_Price_INR
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
        "min_date": df["Order_Date"].min().date(),
        "max_date": df["Order_Date"].max().date(),
    }

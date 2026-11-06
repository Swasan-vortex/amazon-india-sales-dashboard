"""
test_suite.py - All-in-One Automated Test Suite for Amazon India Sales Analysis Dashboard.
Tests:
1. Dataset loading (local resolution, BytesIO/uploader fallback, missing file error handling)
2. Filter-related crosstab reindex robustness (Fulfillment & Payment status charts)
3. Product search plain-text safety (regex metacharacters, case insensitivity, empty/null)
4. Time series Day-of-Week reindexing & fillna safety
5. Comprehensive Filter Permutations & Edge-Case Scenarios
"""

import os
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from data_loader import (
    load_and_preprocess_data,
    resolve_dataset_source,
    get_filter_options,
    DEFAULT_FILE_NAME,
    EXPECTED_COLUMNS
)
from utils import (
    calculate_kpis,
    apply_chart_theme,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    STATUS_COLORS
)

ALL_STATUSES = ["Delivered", "Shipped", "Returned", "Cancelled"]


def test_1_dataset_loading_modes():
    print("\n--- TEST 1: Dataset Loading & Missing Dataset Handling ---")
    
    # 1. Local resolution
    source_type, source_val = resolve_dataset_source()
    assert source_type == "local", f"Expected 'local', got {source_type}"
    assert source_val is not None, "Expected valid source path"
    print("[PASS] Local dataset source successfully resolved.")

    # 2. Local file loading
    df = load_and_preprocess_data(source_val)
    assert len(df) == 10000, f"Expected 10000 rows, got {len(df)}"
    for col in EXPECTED_COLUMNS:
        assert col in df.columns, f"Missing expected column: {col}"
    print("[PASS] Local dataset loaded and preprocessed (10,000 rows, all 13 core columns validated).")

    # 3. In-memory BytesIO loading (simulates Streamlit file uploader)
    with open(source_val, "rb") as f:
        bytes_data = f.read()
    df_from_bytes = load_and_preprocess_data(bytes_data)
    assert len(df_from_bytes) == 10000
    print("[PASS] Upload fallback simulation (BytesIO / file_uploader) succeeded.")

    # 4. Missing dataset error handling
    try:
        load_and_preprocess_data("non_existent_file_12345.xlsx")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("[PASS] Missing dataset gracefully caught: FileNotFoundError")

    try:
        load_and_preprocess_data(None)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("[PASS] None source gracefully caught: ValueError")


def test_2_crosstab_reindex_filter_robustness():
    print("\n--- TEST 2: Crosstab Reindex Robustness (Fulfillment & Payment Charts) ---")
    df = load_and_preprocess_data(DEFAULT_FILE_NAME)
    
    # Test with only 1 status
    single_status_df = df[df["Order_Status"] == "Delivered"]
    ful_ct1 = pd.crosstab(single_status_df["Fulfillment"], single_status_df["Order_Status"], normalize="index") * 100
    ful_status1 = ful_ct1.reindex(columns=ALL_STATUSES, fill_value=0.0).fillna(0.0).reset_index()
    ful_status1.columns.name = None
    
    for status in ALL_STATUSES:
        assert status in ful_status1.columns, f"Status column {status} missing in ful_status1"
    
    fig1 = px.bar(ful_status1, x="Fulfillment", y=ALL_STATUSES, barmode="stack")
    print("[PASS] Single status filter ('Delivered' only) - Chart rendered with all 4 columns intact.")

    # Test with 2 statuses
    two_status_df = df[df["Order_Status"].isin(["Cancelled", "Returned"])]
    pay_ct2 = pd.crosstab(two_status_df["Payment_Method"], two_status_df["Order_Status"], normalize="index") * 100
    pay_status2 = pay_ct2.reindex(columns=ALL_STATUSES, fill_value=0.0).fillna(0.0).reset_index()
    pay_status2.columns.name = None
    
    for status in ALL_STATUSES:
        assert status in pay_status2.columns, f"Status column {status} missing in pay_status2"
    
    fig2 = px.bar(pay_status2, x="Payment_Method", y=ALL_STATUSES, barmode="group")
    print("[PASS] Multiple status filter ('Cancelled' & 'Returned') - Chart rendered with all 4 columns intact.")

    # Test with empty dataframe
    empty_df = df[df["Order_Status"] == "GhostStatus"]
    empty_ct = pd.crosstab(empty_df["Fulfillment"], empty_df["Order_Status"], normalize="index") * 100
    empty_status = empty_ct.reindex(columns=ALL_STATUSES, fill_value=0.0).fillna(0.0).reset_index()
    empty_status.columns.name = None
    fig3 = px.bar(empty_status, x="Fulfillment", y=ALL_STATUSES)
    print("[PASS] Empty dataframe filter - Handled safely without crash.")


def test_3_search_plain_text_regex_safety():
    print("\n--- TEST 3: Search Plain-Text & Regex Safety ---")
    df = load_and_preprocess_data(DEFAULT_FILE_NAME)
    
    metacharacters = ["[", "]", "(", ")", "*", "+", "?", ".", "^", "$", "\\", ".*", "[a-z]"]
    
    for char in metacharacters:
        try:
            matches = df[
                df["Order_ID"].astype(str).str.contains(char, case=False, regex=False, na=False) |
                df["Product"].astype(str).str.contains(char, case=False, regex=False, na=False) |
                df["Category"].astype(str).str.contains(char, case=False, regex=False, na=False) |
                df["Ship_State"].astype(str).str.contains(char, case=False, regex=False, na=False)
            ]
            print(f"  [PASS] Character {char!r:6} -> {len(matches)} safe matches (no regex crash).")
        except Exception as e:
            assert False, f"Failed on metacharacter {char}: {e}"

    # Test case insensitivity
    upper_matches = df[df["Product"].astype(str).str.contains("SMARTPHONE", case=False, regex=False, na=False)]
    lower_matches = df[df["Product"].astype(str).str.contains("smartphone", case=False, regex=False, na=False)]
    assert len(upper_matches) == len(lower_matches) and len(upper_matches) > 0
    print(f"[PASS] Case insensitivity verified: 'SMARTPHONE' ({len(upper_matches)}) == 'smartphone' ({len(lower_matches)})")


def test_4_day_of_week_reindex():
    print("\n--- TEST 4: Day of Week Reindex & FillNA ---")
    df = load_and_preprocess_data(DEFAULT_FILE_NAME)
    
    single_date_df = df[df["Order_Date"].dt.date == df["Order_Date"].min().date()]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_df = single_date_df.groupby("Day_Name").agg(
        Orders=("Order_ID", "count"),
        Sales=("Total_Sales_INR", "sum")
    ).reindex(day_order, fill_value=0).fillna(0).reset_index()
    
    assert len(dow_df) == 7, f"Expected 7 days of week, got {len(dow_df)}"
    assert not dow_df["Orders"].isnull().any(), "Orders should have no NaN"
    assert not dow_df["Sales"].isnull().any(), "Sales should have no NaN"
    print("[PASS] Day of week reindexing verified: all 7 days populated without NaN.")


def test_5_full_filter_permutations():
    print("\n--- TEST 5: Full Filter Permutations Simulation ---")
    df = load_and_preprocess_data(DEFAULT_FILE_NAME)
    
    scenarios = [
        ("Full Unfiltered Dataset", df),
        ("Status = Delivered ONLY", df[df["Order_Status"] == "Delivered"]),
        ("Status = Cancelled ONLY", df[df["Order_Status"] == "Cancelled"]),
        ("Status = Returned ONLY", df[df["Order_Status"] == "Returned"]),
        ("Status = Shipped ONLY", df[df["Order_Status"] == "Shipped"]),
        ("Category = Pantry & Groceries ONLY", df[df["Category"] == "Pantry & Groceries"]),
        ("State = Kerala & Status = Delivered", df[(df["Ship_State"] == "Kerala") & (df["Order_Status"] == "Delivered")]),
        ("Payment = Cash on Delivery (COD) ONLY", df[df["Payment_Method"] == "Cash on Delivery (COD)"]),
        ("Single Row Dataset", df.head(1))
    ]
    
    for name, subset in scenarios:
        kpis = calculate_kpis(subset)
        assert kpis is not None
        
        # Test Fulfillment Chart
        ful_ct = pd.crosstab(subset["Fulfillment"], subset["Order_Status"], normalize="index") * 100
        ful_status = ful_ct.reindex(columns=ALL_STATUSES, fill_value=0.0).fillna(0.0).reset_index()
        ful_status.columns.name = None
        fig_ful = px.bar(ful_status, x="Fulfillment", y=ALL_STATUSES, barmode="stack")
        
        # Test Payment Chart
        pay_ct = pd.crosstab(subset["Payment_Method"], subset["Order_Status"], normalize="index") * 100
        pay_status = pay_ct.reindex(columns=ALL_STATUSES, fill_value=0.0).fillna(0.0).reset_index()
        pay_status.columns.name = None
        fig_pay = px.bar(pay_status, x="Payment_Method", y=ALL_STATUSES, barmode="group")
        
        print(f"  [PASS] Scenario '{name}' (Rows: {len(subset)}) -> Rendered cleanly.")


if __name__ == "__main__":
    test_1_dataset_loading_modes()
    test_2_crosstab_reindex_filter_robustness()
    test_3_search_plain_text_regex_safety()
    test_4_day_of_week_reindex()
    test_5_full_filter_permutations()
    print("\n==========================================")
    print("ALL TEST SUITES PASSED SUCCESSFULLY!")
    print("==========================================")

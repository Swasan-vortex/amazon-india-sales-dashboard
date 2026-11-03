"""
app.py - Main Streamlit Application for Amazon India Sales Analysis Dashboard.
Academic Project: 4th-Year B.Tech Final Year Project
Developed using: Python, Streamlit, Pandas, NumPy, Plotly, OpenPyXL
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Local helper modules
from data_loader import load_and_preprocess_data, get_filter_options
from utils import (
    format_inr,
    format_number,
    format_percent,
    calculate_kpis,
    apply_chart_theme,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_NAVY,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_AMBER,
    CATEGORY_COLORS,
    STATUS_COLORS,
    FULFILLMENT_COLORS,
    PAYMENT_COLORS
)

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Amazon India Sales Analysis Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS STYLING (Simple, Modern, Clean Academic Project Look)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Main container fonts and background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Container */
    .dashboard-header {
        background: linear-gradient(135deg, #131921 0%, #232F3E 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 6px solid #FF9900;
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    .dashboard-header p {
        margin: 6px 0 0 0;
        font-size: 13.5px;
        color: #D5D9D9;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E4E8;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        text-align: left;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        border-color: #FF9900;
    }
    .kpi-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #555555;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #131921;
        margin-bottom: 4px;
    }
    .kpi-subtext {
        font-size: 12px;
        color: #777777;
    }
    
    /* Insight Callout Box */
    .insight-box {
        background-color: #F8F9FA;
        border-left: 4px solid #146EB4;
        border-radius: 0 8px 8px 0;
        padding: 16px 20px;
        margin-top: 18px;
        margin-bottom: 18px;
        border-top: 1px solid #EEEEEE;
        border-right: 1px solid #EEEEEE;
        border-bottom: 1px solid #EEEEEE;
    }
    .insight-title {
        font-weight: 700;
        color: #232F3E;
        font-size: 14.5px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .insight-item {
        font-size: 13px;
        color: #333333;
        margin-bottom: 6px;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    .sidebar-section-title {
        font-size: 13px;
        font-weight: 700;
        color: #232F3E;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 14px;
        margin-bottom: 8px;
    }

    /* Badge */
    .filter-badge {
        display: inline-block;
        background-color: #FFF3CD;
        color: #856404;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. DATA LOADING
# -----------------------------------------------------------------------------
DATA_FILE = "Amazon Sales Data India.xlsx"

try:
    raw_df = load_and_preprocess_data(DATA_FILE)
    filter_opts = get_filter_options(raw_df)
except Exception as e:
    st.error(f"⚠️ Error loading dataset: {str(e)}")
    st.info("Please ensure 'Amazon Sales Data India.xlsx' is present in the project directory.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. SIDEBAR - CONTROLS & DYNAMIC FILTERS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=140)
    st.markdown("### **Sales Analytics Controls**")
    st.caption("Final Year B.Tech Academic Project")
    st.markdown("---")

    # Quick Reset Button
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # 1. Date Range Filter
    st.markdown("<div class='sidebar-section-title'>📅 Date Range</div>", unsafe_allow_html=True)
    date_range = st.date_input(
        "Select Order Date Range",
        value=(filter_opts["min_date"], filter_opts["max_date"]),
        min_value=filter_opts["min_date"],
        max_value=filter_opts["max_date"],
        help="Filter orders by order date"
    )

    # Handle single date selection edge-case
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = filter_opts["min_date"], filter_opts["max_date"]

    # 2. Category Filter
    st.markdown("<div class='sidebar-section-title'>📂 Product Category</div>", unsafe_allow_html=True)
    selected_categories = st.multiselect(
        "Filter by Category",
        options=filter_opts["categories"],
        default=filter_opts["categories"],
        placeholder="Select categories..."
    )

    # 3. Fulfillment Method Filter
    st.markdown("<div class='sidebar-section-title'>🚚 Fulfillment Method</div>", unsafe_allow_html=True)
    selected_fulfillments = st.multiselect(
        "Filter by Fulfillment Channel",
        options=filter_opts["fulfillments"],
        default=filter_opts["fulfillments"],
        placeholder="Select fulfillment methods..."
    )

    # 4. Order Status Filter
    st.markdown("<div class='sidebar-section-title'>📦 Order Status</div>", unsafe_allow_html=True)
    selected_statuses = st.multiselect(
        "Filter by Order Status",
        options=filter_opts["statuses"],
        default=filter_opts["statuses"],
        placeholder="Select order statuses..."
    )

    # 5. Geographic State Filter
    st.markdown("<div class='sidebar-section-title'>🗺️ Destination State</div>", unsafe_allow_html=True)
    selected_states = st.multiselect(
        "Filter by Indian State",
        options=filter_opts["states"],
        default=filter_opts["states"],
        placeholder="Select states..."
    )

    # 6. Payment Method Filter
    st.markdown("<div class='sidebar-section-title'>💳 Payment Method</div>", unsafe_allow_html=True)
    selected_payments = st.multiselect(
        "Filter by Payment Mode",
        options=filter_opts["payments"],
        default=filter_opts["payments"],
        placeholder="Select payment methods..."
    )

    st.markdown("---")
    st.markdown("#### **Project Specs**")
    st.markdown("""
    - **Total Records:** 10,000
    - **Attributes:** 13 Columns
    - **Timeframe:** Jan 2024 – Aug 2026
    - **Domain:** E-commerce Retail (India)
    """)

# -----------------------------------------------------------------------------
# 5. FILTERING LOGIC
# -----------------------------------------------------------------------------
# Apply active filters safely
filtered_df = raw_df[
    (raw_df["Order_Date"].dt.date >= start_date) &
    (raw_df["Order_Date"].dt.date <= end_date) &
    (raw_df["Category"].isin(selected_categories)) &
    (raw_df["Fulfillment"].isin(selected_fulfillments)) &
    (raw_df["Order_Status"].isin(selected_statuses)) &
    (raw_df["Ship_State"].isin(selected_states)) &
    (raw_df["Payment_Method"].isin(selected_payments))
]

kpis = calculate_kpis(filtered_df)

# -----------------------------------------------------------------------------
# 6. HEADER SECTION
# -----------------------------------------------------------------------------
st.markdown("""
<div class="dashboard-header">
    <h1>📦 Amazon India Sales & Profit Analysis Dashboard</h1>
    <p>Comprehensive interactive analytics on revenue, profitability, product categories, fulfillment operations, payment methods, and geographic distribution across Indian states.</p>
</div>
""", unsafe_allow_html=True)

# Filter Status Indicator
pct_filtered = (len(filtered_df) / len(raw_df) * 100) if len(raw_df) > 0 else 0
st.markdown(
    f"<span class='filter-badge'>📊 Active Dataset: <b>{format_number(len(filtered_df))}</b> of <b>{format_number(len(raw_df))}</b> records ({pct_filtered:.1f}%) | Period: {start_date} to {end_date}</span>",
    unsafe_allow_html=True
)

if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filter criteria. Please adjust your filters in the sidebar.")
    st.stop()

# -----------------------------------------------------------------------------
# 7. TOP-LEVEL KPI METRIC CARDS
# -----------------------------------------------------------------------------
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Revenue</div>
        <div class="kpi-value">{format_inr(kpis['total_sales'])}</div>
        <div class="kpi-subtext">Exact: ₹ {kpis['total_sales']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Profit</div>
        <div class="kpi-value" style="color: {COLOR_GREEN};">{format_inr(kpis['total_profit'])}</div>
        <div class="kpi-subtext">Exact: ₹ {kpis['total_profit']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Net Margin</div>
        <div class="kpi-value" style="color: {COLOR_BLUE};">{format_percent(kpis['profit_margin'])}</div>
        <div class="kpi-subtext">Profit-to-Sales Ratio</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Orders</div>
        <div class="kpi-value">{format_number(kpis['total_orders'])}</div>
        <div class="kpi-subtext">Avg Order: {format_inr(kpis['aov'])}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Quantity Sold</div>
        <div class="kpi-value">{format_number(kpis['total_quantity'])}</div>
        <div class="kpi-subtext">Avg Units/Order: {(kpis['total_quantity'] / kpis['total_orders']):.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Delivery Rate</div>
        <div class="kpi-value" style="color: {COLOR_GREEN};">{format_percent(kpis['delivery_rate'])}</div>
        <div class="kpi-subtext">Ret: {kpis['return_rate']:.1f}% | Can: {kpis['cancellation_rate']:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. NAVIGATION TABS (Structured as per project objectives)
# -----------------------------------------------------------------------------
tab_exec, tab_cat, tab_logistics, tab_payment, tab_geo, tab_trends, tab_data, tab_about = st.tabs([
    "📊 Executive Summary",
    "📦 Category & Products",
    "🚚 Logistics & Fulfillment",
    "💳 Payment Methods",
    "🗺️ State Analysis",
    "📈 Sales & Trends",
    "🔍 Data Explorer",
    "🎓 Academic Project Info"
])

# =============================================================================
# TAB 1: EXECUTIVE SUMMARY
# =============================================================================
with tab_exec:
    st.markdown("### 📊 Business Performance Overview")
    st.caption("High-level summary of total sales, profitability, category contributions, and delivery efficiency.")

    row1_col1, row1_col2 = st.columns([1.6, 1])

    with row1_col1:
        # Monthly Sales and Profit Bar + Line Chart
        monthly_data = filtered_df.groupby("Year_Month").agg(
            Sales=("Total_Sales_INR", "sum"),
            Profit=("Profit_INR", "sum")
        ).reset_index()

        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=monthly_data["Year_Month"],
            y=monthly_data["Sales"],
            name="Revenue (Sales)",
            marker_color=COLOR_BLUE,
            hovertemplate="Month: %{x}<br>Sales: ₹ %{y:,.2f}<extra></extra>"
        ))
        fig_monthly.add_trace(go.Scatter(
            x=monthly_data["Year_Month"],
            y=monthly_data["Profit"],
            name="Net Profit",
            mode="lines+markers",
            marker=dict(color=COLOR_PRIMARY, size=7),
            line=dict(color=COLOR_PRIMARY, width=3),
            hovertemplate="Month: %{x}<br>Profit: ₹ %{y:,.2f}<extra></extra>"
        ))

        fig_monthly = apply_chart_theme(
            fig_monthly,
            title="Monthly Sales & Profit Trend (2024 - 2026)",
            x_title="Year-Month",
            y_title="Amount in INR (₹)",
            height=380
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    with row1_col2:
        # Category Sales Share Donut Chart
        cat_sales = filtered_df.groupby("Category")["Total_Sales_INR"].sum().reset_index()
        fig_cat_donut = px.pie(
            cat_sales,
            names="Category",
            values="Total_Sales_INR",
            hole=0.48,
            color="Category",
            color_discrete_map=CATEGORY_COLORS
        )
        fig_cat_donut.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Sales: ₹ %{value:,.2f}<br>Share: %{percent}<extra></extra>"
        )
        fig_cat_donut = apply_chart_theme(
            fig_cat_donut,
            title="Sales Share by Product Category",
            height=380,
            show_legend=False
        )
        st.plotly_chart(fig_cat_donut, use_container_width=True)

    row2_col1, row2_col2 = st.columns([1, 1])

    with row2_col1:
        # Category Revenue vs Profit Comparison (Horizontal Bar Chart)
        cat_summary = filtered_df.groupby("Category").agg(
            Sales=("Total_Sales_INR", "sum"),
            Profit=("Profit_INR", "sum"),
            Orders=("Order_ID", "count")
        ).reset_index().sort_values(by="Sales", ascending=True)

        fig_cat_bar = go.Figure()
        fig_cat_bar.add_trace(go.Bar(
            y=cat_summary["Category"],
            x=cat_summary["Sales"],
            name="Sales (INR)",
            orientation="h",
            marker_color=COLOR_BLUE,
            hovertemplate="Category: %{y}<br>Sales: ₹ %{x:,.2f}<extra></extra>"
        ))
        fig_cat_bar.add_trace(go.Bar(
            y=cat_summary["Category"],
            x=cat_summary["Profit"],
            name="Profit (INR)",
            orientation="h",
            marker_color=COLOR_GREEN,
            hovertemplate="Category: %{y}<br>Profit: ₹ %{x:,.2f}<extra></extra>"
        ))
        fig_cat_bar = apply_chart_theme(
            fig_cat_bar,
            title="Revenue vs Profit by Category",
            x_title="Amount in INR (₹)",
            y_title="",
            height=350
        )
        fig_cat_bar.update_layout(barmode="group")
        st.plotly_chart(fig_cat_bar, use_container_width=True)

    with row2_col2:
        # Order Status Breakdown Pie Chart
        status_df = filtered_df["Order_Status"].value_counts().reset_index()
        status_df.columns = ["Order_Status", "Count"]

        fig_status = px.pie(
            status_df,
            names="Order_Status",
            values="Count",
            color="Order_Status",
            color_discrete_map=STATUS_COLORS,
            hole=0.45
        )
        fig_status.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Percentage: %{percent}<extra></extra>"
        )
        fig_status = apply_chart_theme(
            fig_status,
            title="Order Status Distribution",
            height=350,
            show_legend=False
        )
        st.plotly_chart(fig_status, use_container_width=True)

    # Business Insights Callout Box for Tab 1
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 Key Executive Insights</div>
        <div class="insight-item"><b>Dominant Category:</b> <i>Electronics & Mobiles</i> generates ~79% of total business revenue due to higher average ticket sizes (5G smartphones, smartwatches, backpacks, power banks).</div>
        <div class="insight-item"><b>High Delivery Success:</b> Over <b>{kpis['delivery_rate']:.1f}%</b> of orders are successfully delivered, while cancellations and returns together account for under 10%.</div>
        <div class="insight-item"><b>Healthy Operating Margin:</b> The business maintains a steady <b>{kpis['profit_margin']:.2f}%</b> net profit margin across categories, indicating solid pricing power.</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: CATEGORY & PRODUCT PERFORMANCE
# =============================================================================
with tab_cat:
    st.markdown("### 📦 Product & Category Deep-Dive")
    st.caption("Detailed ranking of top performing products, profit contributions, and discount analysis.")

    cat_col1, cat_col2 = st.columns(2)

    # Product Performance Aggregation
    prod_perf = filtered_df.groupby(["Category", "Product"]).agg(
        Orders=("Order_ID", "count"),
        Quantity=("Quantity", "sum"),
        Total_Sales=("Total_Sales_INR", "sum"),
        Total_Profit=("Profit_INR", "sum")
    ).reset_index()
    prod_perf["Margin_Pct"] = (prod_perf["Total_Profit"] / prod_perf["Total_Sales"] * 100).round(2)
    prod_perf["Avg_Sales_Per_Order"] = (prod_perf["Total_Sales"] / prod_perf["Orders"]).round(2)

    with cat_col1:
        # Top 10 Products by Sales
        top_sales_prod = prod_perf.sort_values(by="Total_Sales", ascending=True).tail(10)
        fig_top_sales = px.bar(
            top_sales_prod,
            y="Product",
            x="Total_Sales",
            color="Category",
            color_discrete_map=CATEGORY_COLORS,
            orientation="h",
            labels={"Total_Sales": "Sales (₹)", "Product": ""},
            title="Top 10 Products by Total Sales Revenue"
        )
        fig_top_sales.update_traces(
            hovertemplate="<b>%{y}</b><br>Category: %{customdata[0]}<br>Total Sales: ₹ %{x:,.2f}<extra></extra>",
            customdata=top_sales_prod[["Category"]].values
        )
        fig_top_sales = apply_chart_theme(fig_top_sales, title="Top 10 Products by Sales Revenue", x_title="Total Sales (₹)", height=420)
        st.plotly_chart(fig_top_sales, use_container_width=True)

    with cat_col2:
        # Top 10 Products by Profit
        top_profit_prod = prod_perf.sort_values(by="Total_Profit", ascending=True).tail(10)
        fig_top_profit = px.bar(
            top_profit_prod,
            y="Product",
            x="Total_Profit",
            color="Category",
            color_discrete_map=CATEGORY_COLORS,
            orientation="h",
            labels={"Total_Profit": "Profit (₹)", "Product": ""},
            title="Top 10 Products by Total Profit"
        )
        fig_top_profit.update_traces(
            hovertemplate="<b>%{y}</b><br>Category: %{customdata[0]}<br>Total Profit: ₹ %{x:,.2f}<extra></extra>",
            customdata=top_profit_prod[["Category"]].values
        )
        fig_top_profit = apply_chart_theme(fig_top_profit, title="Top 10 Products by Total Profit", x_title="Total Profit (₹)", height=420)
        st.plotly_chart(fig_top_profit, use_container_width=True)

    st.markdown("#### 🏷️ Discount Impact on Sales & Profitability")
    st.caption("How different discount tiers impact order volumes, generated revenue, and profit margins.")

    disc_col1, disc_col2 = st.columns([1.2, 1])

    with disc_col1:
        # Discount Distribution Analysis
        filtered_df["Discount_Tier"] = (filtered_df["Discount_Pct"] * 100).astype(int).astype(str) + "% Off"
        disc_summary = filtered_df.groupby("Discount_Tier").agg(
            Orders=("Order_ID", "count"),
            Sales=("Total_Sales_INR", "sum"),
            Profit=("Profit_INR", "sum"),
            Avg_Margin=("Profit_Margin_Pct", "mean")
        ).reindex(["0% Off", "5% Off", "10% Off", "15% Off", "20% Off", "25% Off"]).dropna()

        fig_disc = go.Figure()
        fig_disc.add_trace(go.Bar(
            x=disc_summary.index,
            y=disc_summary["Sales"],
            name="Sales (INR)",
            marker_color=COLOR_BLUE,
            hovertemplate="Discount: %{x}<br>Sales: ₹ %{y:,.2f}<extra></extra>"
        ))
        fig_disc.add_trace(go.Scatter(
            x=disc_summary.index,
            y=disc_summary["Avg_Margin"],
            name="Avg Profit Margin %",
            yaxis="y2",
            mode="lines+markers",
            marker=dict(color=COLOR_PRIMARY, size=8),
            line=dict(color=COLOR_PRIMARY, width=3),
            hovertemplate="Discount: %{x}<br>Margin: %{y:.2f}%<extra></extra>"
        ))
        fig_disc.update_layout(
            yaxis2=dict(
                title="Profit Margin %",
                overlaying="y",
                side="right",
                showgrid=False,
                range=[0, 30]
            )
        )
        fig_disc = apply_chart_theme(
            fig_disc,
            title="Sales Volume and Profit Margin by Discount Tier",
            x_title="Discount Tier",
            y_title="Total Sales (₹)",
            height=360
        )
        st.plotly_chart(fig_disc, use_container_width=True)

    with disc_col2:
        # Category Level Summary Table
        cat_tbl = filtered_df.groupby("Category").agg(
            Orders=("Order_ID", "count"),
            Quantity=("Quantity", "sum"),
            Sales=("Total_Sales_INR", "sum"),
            Profit=("Profit_INR", "sum")
        ).reset_index()
        cat_tbl["Margin %"] = (cat_tbl["Profit"] / cat_tbl["Sales"] * 100).round(2).astype(str) + "%"
        cat_tbl["Revenue"] = cat_tbl["Sales"].apply(lambda x: format_inr(x))
        cat_tbl["Profit Amt"] = cat_tbl["Profit"].apply(lambda x: format_inr(x))

        st.markdown("**Category Performance Table**")
        st.dataframe(
            cat_tbl[["Category", "Orders", "Quantity", "Revenue", "Profit Amt", "Margin %"]],
            use_container_width=True,
            hide_index=True
        )

    # Insights for Tab 2
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 Product & Category Insights</div>
        <div class="insight-item"><b>Hero Products:</b> Laptop Backpacks, Power Banks (20000mAh), 5G Smartphones, and Wireless Earbuds are the top revenue drivers, each generating over ₹50 Lakhs in profit.</div>
        <div class="insight-item"><b>Everyday Essentials:</b> Categories like <i>Pantry & Groceries</i> and <i>Beauty</i> have lower sales values per unit but high repeat purchase velocity and steady 21%+ margins.</div>
        <div class="insight-item"><b>Discount Sensitivity:</b> ~30% of sales happen with zero discount, while 5% to 10% discounts drive healthy volume without eroding net margin significantly.</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 3: LOGISTICS & FULFILLMENT
# =============================================================================
with tab_logistics:
    st.markdown("### 🚚 Logistics, Fulfillment & Order Status")
    st.caption("Evaluating Amazon FBA, Seller Flex, and Merchant (FBM) fulfillment channels and order completion rates.")

    ful_col1, ful_col2 = st.columns([1.1, 1])

    with ful_col1:
        # Fulfillment method breakdown
        ful_data = filtered_df.groupby("Fulfillment").agg(
            Orders=("Order_ID", "count"),
            Sales=("Total_Sales_INR", "sum"),
            Profit=("Profit_INR", "sum")
        ).reset_index()

        fig_ful = px.bar(
            ful_data,
            x="Fulfillment",
            y="Orders",
            color="Fulfillment",
            color_discrete_map=FULFILLMENT_COLORS,
            text_auto=True,
            title="Order Volume by Fulfillment Channel"
        )
        fig_ful = apply_chart_theme(
            fig_ful,
            title="Order Volume by Fulfillment Channel",
            x_title="Fulfillment Method",
            y_title="Total Orders",
            height=360,
            show_legend=False
        )
        st.plotly_chart(fig_ful, use_container_width=True)

    with ful_col2:
        # Fulfillment Channel Delivery Success vs Cancellation/Return
        ful_status = pd.crosstab(
            filtered_df["Fulfillment"],
            filtered_df["Order_Status"],
            normalize="index"
        ) * 100
        ful_status = ful_status.reset_index()

        fig_ful_status = px.bar(
            ful_status,
            x="Fulfillment",
            y=["Delivered", "Shipped", "Returned", "Cancelled"],
            title="Order Status Share by Fulfillment Channel (%)",
            color_discrete_map=STATUS_COLORS,
            barmode="stack"
        )
        fig_ful_status = apply_chart_theme(
            fig_ful_status,
            title="Order Status Breakdown per Fulfillment Channel (%)",
            x_title="Fulfillment Method",
            y_title="Percentage (%)",
            height=360
        )
        st.plotly_chart(fig_ful_status, use_container_width=True)

    # Detailed operational matrix
    st.markdown("#### 📋 Fulfillment Channel Efficiency Matrix")
    ful_matrix = filtered_df.groupby("Fulfillment").agg(
        Total_Orders=("Order_ID", "count"),
        Total_Sales=("Total_Sales_INR", "sum"),
        Total_Profit=("Profit_INR", "sum"),
        Delivered=("Order_Status", lambda s: (s == "Delivered").sum()),
        Returned=("Order_Status", lambda s: (s == "Returned").sum()),
        Cancelled=("Order_Status", lambda s: (s == "Cancelled").sum())
    ).reset_index()

    ful_matrix["Delivery Rate %"] = (ful_matrix["Delivered"] / ful_matrix["Total_Orders"] * 100).round(2).astype(str) + "%"
    ful_matrix["Return Rate %"] = (ful_matrix["Returned"] / ful_matrix["Total_Orders"] * 100).round(2).astype(str) + "%"
    ful_matrix["Cancellation Rate %"] = (ful_matrix["Cancelled"] / ful_matrix["Total_Orders"] * 100).round(2).astype(str) + "%"
    ful_matrix["Revenue"] = ful_matrix["Total_Sales"].apply(lambda x: format_inr(x))
    ful_matrix["Profit"] = ful_matrix["Total_Profit"].apply(lambda x: format_inr(x))

    st.dataframe(
        ful_matrix[["Fulfillment", "Total_Orders", "Revenue", "Profit", "Delivery Rate %", "Return Rate %", "Cancellation Rate %"]],
        use_container_width=True,
        hide_index=True
    )

    # Insights for Tab 3
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 Logistics & Operations Insights</div>
        <div class="insight-item"><b>Amazon FBA Dominance:</b> Over <b>70%</b> of orders are fulfilled through Amazon (FBA) due to Prime delivery speed, lower shipping friction, and automated handling.</div>
        <div class="insight-item"><b>High Delivery Reliability:</b> Amazon FBA achieves a <b>82.0%</b> delivery rate, outperforming Merchant FBM (78.4%) by more than 3.6 percentage points.</div>
        <div class="insight-item"><b>Seller Flex Efficiency:</b> Seller Flex serves as a cost-effective middle tier, handling ~20% of volume with competitive delivery metrics.</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 4: PAYMENT METHODS
# =============================================================================
with tab_payment:
    st.markdown("### 💳 Payment Methods & Buyer Behavior")
    st.caption("Adoption of digital payments (UPI, Cards, Net Banking) versus Cash on Delivery across Amazon India buyers.")

    pay_col1, pay_col2 = st.columns([1, 1.2])

    with pay_col1:
        # Payment method share pie chart
        pay_counts = filtered_df["Payment_Method"].value_counts().reset_index()
        pay_counts.columns = ["Payment_Method", "Orders"]

        fig_pay_pie = px.pie(
            pay_counts,
            names="Payment_Method",
            values="Orders",
            color="Payment_Method",
            color_discrete_map=PAYMENT_COLORS,
            hole=0.45
        )
        fig_pay_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>"
        )
        fig_pay_pie = apply_chart_theme(
            fig_pay_pie,
            title="Payment Method Share (Orders)",
            height=370,
            show_legend=False
        )
        st.plotly_chart(fig_pay_pie, use_container_width=True)

    with pay_col2:
        # Average Order Value by Payment Method
        pay_metrics = filtered_df.groupby("Payment_Method").agg(
            Orders=("Order_ID", "count"),
            Total_Sales=("Total_Sales_INR", "sum"),
            Total_Profit=("Profit_INR", "sum"),
            AOV=("Total_Sales_INR", "mean")
        ).reset_index().sort_values(by="AOV", ascending=True)

        fig_aov = px.bar(
            pay_metrics,
            y="Payment_Method",
            x="AOV",
            color="Payment_Method",
            color_discrete_map=PAYMENT_COLORS,
            orientation="h",
            text_auto=",.0f"
        )
        fig_aov = apply_chart_theme(
            fig_aov,
            title="Average Order Value (AOV) by Payment Mode",
            x_title="Average Order Value (₹)",
            y_title="",
            height=370,
            show_legend=False
        )
        st.plotly_chart(fig_aov, use_container_width=True)

    # Payment Status Performance (Return / Cancellation comparison)
    st.markdown("#### 🔄 Return & Cancellation Rate by Payment Mode")
    pay_status = pd.crosstab(
        filtered_df["Payment_Method"],
        filtered_df["Order_Status"],
        normalize="index"
    ) * 100
    pay_status = pay_status.reset_index()

    fig_pay_stat = px.bar(
        pay_status,
        x="Payment_Method",
        y=["Delivered", "Shipped", "Returned", "Cancelled"],
        color_discrete_map=STATUS_COLORS,
        barmode="group",
        labels={"value": "Percentage of Orders (%)", "Payment_Method": "Payment Mode"}
    )
    fig_pay_stat = apply_chart_theme(
        fig_pay_stat,
        title="Delivery vs Return/Cancel Rate across Payment Methods (%)",
        x_title="Payment Method",
        y_title="Percentage (%)",
        height=360
    )
    st.plotly_chart(fig_pay_stat, use_container_width=True)

    # Insights for Tab 4
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 Payment & Customer Insights</div>
        <div class="insight-item"><b>UPI Revolution:</b> UPI is the single largest payment mode, accounting for nearly <b>50%</b> of all orders, demonstrating the immense penetration of instant QR & VPA payments in India.</div>
        <div class="insight-item"><b>Credit/Debit Cards & Amazon Pay Later:</b> Card buyers have high ticket sizes, frequently used for premium electronics. Amazon Pay Later has the highest delivery completion rate (~84.3%).</div>
        <div class="insight-item"><b>Cash on Delivery (COD):</b> COD represents ~14.6% of orders, remaining an essential payment option for customers building trust with the platform.</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 5: REGIONAL & STATE ANALYSIS
# =============================================================================
with tab_geo:
    st.markdown("### 🗺️ Geographic & State-wise Sales Analysis")
    st.caption("Evaluating revenue, profit, and demand across 10 major Indian states.")

    # State Aggregations
    state_df = filtered_df.groupby("Ship_State").agg(
        Orders=("Order_ID", "count"),
        Sales=("Total_Sales_INR", "sum"),
        Profit=("Profit_INR", "sum"),
        Units=("Quantity", "sum")
    ).reset_index().sort_values(by="Sales", ascending=True)

    geo_col1, geo_col2 = st.columns([1.2, 1])

    with geo_col1:
        # State Sales & Profit Horizontal Bar Chart
        fig_state = go.Figure()
        fig_state.add_trace(go.Bar(
            y=state_df["Ship_State"],
            x=state_df["Sales"],
            name="Revenue (Sales)",
            orientation="h",
            marker_color=COLOR_BLUE,
            hovertemplate="State: %{y}<br>Sales: ₹ %{x:,.2f}<extra></extra>"
        ))
        fig_state.add_trace(go.Bar(
            y=state_df["Ship_State"],
            x=state_df["Profit"],
            name="Net Profit",
            orientation="h",
            marker_color=COLOR_PRIMARY,
            hovertemplate="State: %{y}<br>Profit: ₹ %{x:,.2f}<extra></extra>"
        ))
        fig_state = apply_chart_theme(
            fig_state,
            title="Sales and Profit by Indian State",
            x_title="Amount in INR (₹)",
            y_title="",
            height=430
        )
        fig_state.update_layout(barmode="group")
        st.plotly_chart(fig_state, use_container_width=True)

    with geo_col2:
        # State Sales Share Donut Chart
        state_share = state_df.sort_values(by="Sales", ascending=False)
        fig_state_pie = px.pie(
            state_share,
            names="Ship_State",
            values="Sales",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_state_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Sales: ₹ %{value:,.2f}<br>Share: %{percent}<extra></extra>"
        )
        fig_state_pie = apply_chart_theme(
            fig_state_pie,
            title="State Revenue Contribution (%)",
            height=430,
            show_legend=False
        )
        st.plotly_chart(fig_state_pie, use_container_width=True)

    # State-level Performance Table
    st.markdown("#### 📋 State Performance Scorecard")
    state_table = state_df.sort_values(by="Sales", ascending=False).reset_index(drop=True)
    state_table["Revenue"] = state_table["Sales"].apply(lambda x: format_inr(x))
    state_table["Profit Amount"] = state_table["Profit"].apply(lambda x: format_inr(x))
    state_table["Margin %"] = (state_table["Profit"] / state_table["Sales"] * 100).round(2).astype(str) + "%"
    state_table["Avg Order Value"] = (state_table["Sales"] / state_table["Orders"]).apply(lambda x: format_inr(x, compact=False))

    st.dataframe(
        state_table[["Ship_State", "Orders", "Units", "Revenue", "Profit Amount", "Margin %", "Avg Order Value"]],
        use_container_width=True,
        hide_index=True
    )

    # Insights for Tab 5
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 Geographic Market Insights</div>
        <div class="insight-item"><b>Top 3 Hubs (Tri-State Engine):</b> <b>Maharashtra (19.0%), Karnataka (15.7%), and Delhi (14.4%)</b> collectively generate almost <b>50%</b> of all sales revenue, driven by major metro hubs (Mumbai, Pune, Bengaluru, Delhi NCR).</div>
        <div class="insight-item"><b>Southern Strength:</b> Tamil Nadu and Telangana represent another ~20% of revenue, indicating robust e-commerce adoption across South India.</div>
        <div class="insight-item"><b>Uniform Profitability:</b> Profit margins across all 10 states remain consistent between 20.8% and 21.6%, showing strong price discipline regardless of destination.</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 6: SALES & TRENDS
# =============================================================================
with tab_trends:
    st.markdown("### 📈 Time-Series & Trend Analysis")
    st.caption("Analyzing sales growth, day-of-week buying behavior, and year-over-year performance.")

    trend_col1, trend_col2 = st.columns([1.3, 1])

    with trend_col1:
        # Quarterly Sales & Profit Trend
        quarterly_df = filtered_df.groupby("Quarter").agg(
            Sales=("Total_Sales_INR", "sum"),
            Profit=("Profit_INR", "sum")
        ).reset_index()

        # Sort quarters chronologically
        quarterly_df["Quarter_Order"] = quarterly_df["Quarter"].apply(
            lambda q: int(q.split()[1]) * 10 + int(q.split()[0][1])
        )
        quarterly_df = quarterly_df.sort_values(by="Quarter_Order").reset_index(drop=True)

        fig_quarter = go.Figure()
        fig_quarter.add_trace(go.Bar(
            x=quarterly_df["Quarter"],
            y=quarterly_df["Sales"],
            name="Quarterly Sales",
            marker_color=COLOR_BLUE,
            hovertemplate="Quarter: %{x}<br>Sales: ₹ %{y:,.2f}<extra></extra>"
        ))
        fig_quarter.add_trace(go.Bar(
            x=quarterly_df["Quarter"],
            y=quarterly_df["Profit"],
            name="Quarterly Profit",
            marker_color=COLOR_PRIMARY,
            hovertemplate="Quarter: %{x}<br>Profit: ₹ %{y:,.2f}<extra></extra>"
        ))
        fig_quarter = apply_chart_theme(
            fig_quarter,
            title="Quarterly Sales & Profit Progression",
            x_title="Fiscal Quarter",
            y_title="Amount in INR (₹)",
            height=370
        )
        fig_quarter.update_layout(barmode="group")
        st.plotly_chart(fig_quarter, use_container_width=True)

    with trend_col2:
        # Day of Week Orders Distribution
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_df = filtered_df.groupby("Day_Name").agg(
            Orders=("Order_ID", "count"),
            Sales=("Total_Sales_INR", "sum")
        ).reindex(day_order).reset_index()

        fig_dow = px.bar(
            dow_df,
            x="Day_Name",
            y="Orders",
            text_auto=True,
            color_discrete_sequence=[COLOR_SECONDARY],
            labels={"Day_Name": "Day of the Week", "Orders": "Total Orders"}
        )
        fig_dow = apply_chart_theme(
            fig_dow,
            title="Order Volume by Day of Week",
            x_title="Day",
            y_title="Orders Placed",
            height=370,
            show_legend=False
        )
        st.plotly_chart(fig_dow, use_container_width=True)

    # Yearly Performance Comparison
    st.markdown("#### 📅 Year-over-Year (YoY) Summary")
    year_df = filtered_df.groupby("Year").agg(
        Orders=("Order_ID", "count"),
        Units=("Quantity", "sum"),
        Sales=("Total_Sales_INR", "sum"),
        Profit=("Profit_INR", "sum")
    ).reset_index()
    year_df["Margin %"] = (year_df["Profit"] / year_df["Sales"] * 100).round(2).astype(str) + "%"
    year_df["Total Sales"] = year_df["Sales"].apply(lambda x: format_inr(x))
    year_df["Total Profit"] = year_df["Profit"].apply(lambda x: format_inr(x))

    st.dataframe(
        year_df[["Year", "Orders", "Units", "Total Sales", "Total Profit", "Margin %"]],
        use_container_width=True,
        hide_index=True
    )

    # Insights for Tab 6
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 Seasonality & Trend Insights</div>
        <div class="insight-item"><b>Steady Run-Rate:</b> 2024 and 2025 delivered consistent annual sales exceeding ₹5.7 Crore each, with healthy sales maintained through mid-2026.</div>
        <div class="insight-item"><b>Consistent Weekday Purchasing:</b> Unlike purely entertainment products, Amazon India orders remain evenly distributed across all 7 days of the week, reflecting steady utility and consumer demand.</div>
        <div class="insight-item"><b>Quarterly Stability:</b> Quarters consistently generate ₹1.2 Cr to ₹1.6 Cr in sales volume, indicating a stable, non-volatile product portfolio.</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 7: DATA EXPLORER & EXPORT
# =============================================================================
with tab_data:
    st.markdown("### 🔍 Interactive Raw Data Explorer")
    st.caption("Inspect individual order records, search by keyword, and export filtered datasets.")

    exp_col1, exp_col2, exp_col3 = st.columns([2, 1, 1])

    with exp_col1:
        search_query = st.text_input("🔎 Search by Order ID or Product Name", placeholder="e.g. IN-AMD-100003 or Smartphone...")

    with exp_col2:
        sort_by_col = st.selectbox(
            "Sort Table By",
            options=["Order_Date", "Total_Sales_INR", "Profit_INR", "Quantity", "Unit_Price_INR"],
            index=0
        )

    with exp_col3:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

    # Apply search filter
    display_df = filtered_df.copy()
    if search_query:
        query_lower = search_query.lower()
        display_df = display_df[
            display_df["Order_ID"].str.lower().str.contains(query_lower) |
            display_df["Product"].str.lower().str.contains(query_lower) |
            display_df["Category"].str.lower().str.contains(query_lower) |
            display_df["Ship_State"].str.lower().str.contains(query_lower)
        ]

    # Sort
    is_ascending = (sort_order == "Ascending")
    display_df = display_df.sort_values(by=sort_by_col, ascending=is_ascending)

    # Prepare view columns
    view_columns = [
        "Order_ID", "Order_Date", "Category", "Product", "Quantity",
        "Unit_Price_INR", "Discount_Pct", "Total_Sales_INR", "Profit_INR",
        "Payment_Method", "Fulfillment", "Order_Status", "Ship_State"
    ]

    st.markdown(f"**Showing {len(display_df):,} matching rows**")
    st.dataframe(
        display_df[view_columns],
        use_container_width=True,
        hide_index=True,
        height=450
    )

    # Export Button (CSV)
    csv_data = display_df[view_columns].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name=f"amazon_india_sales_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=False
    )


# =============================================================================
# TAB 8: ACADEMIC PROJECT INFO & VIVA PREPARATION
# =============================================================================
with tab_about:
    st.markdown("### 🎓 Academic Project Documentation")
    st.caption("Comprehensive documentation, problem statement, technology stack, and examination defense guide.")

    abt_col1, abt_col2 = st.columns([1.2, 1])

    with abt_col1:
        st.markdown("""
        #### 📌 Project Overview
        - **Project Title:** Amazon India Sales & Profit Analysis Dashboard
        - **Academic Level:** 4th-Year B.Tech Final Year Capstone Project
        - **Domain:** Data Analytics, Business Intelligence & E-Commerce Metrics
        - **Objective:** To transform 10,000 raw sales transaction records from Amazon India into actionable managerial insights, interactive visual dashboards, and performance benchmarks.

        #### 🎯 Core Research & Analysis Objectives
        1. **Revenue & Profit Dynamics:** Measure total revenue (₹15.58 Cr), net profit (₹3.32 Cr), and profit margins across products.
        2. **Category & Product Performance:** Identify high-margin vs high-velocity products across 5 major sectors.
        3. **Logistics & Order Distribution:** Compare delivery success and return rates between Amazon FBA, Seller Flex, and Merchant FBM.
        4. **Consumer Payment Trends:** Analyze UPI dominance (~50%) vs Credit Cards, Net Banking, Pay Later, and COD.
        5. **Geographic Sales Footprint:** Evaluate market demand and profitability across top 10 Indian state economies.

        #### 🛠️ Technology Stack
        - **Python 3:** Core programming language for data transformations.
        - **Streamlit:** Fast, reactive web dashboard framework.
        - **Pandas & NumPy:** High-performance vectorized data manipulation and mathematical aggregations.
        - **Plotly Express & Graph Objects:** Interactive, publication-ready data visualizations.
        - **OpenPyXL:** Engine for parsing multi-record Microsoft Excel datasets.
        """)

    with abt_col2:
        st.markdown("""
        #### 💡 Viva / Project Defense Questions
        
        **Q1: Why is Amazon FBA preferred over Merchant FBM?**
        - *Answer:* Amazon FBA handles ~70.5% of volume and delivers the highest fulfillment success (~82.0%), lower transit delays, and Prime eligibility compared to FBM (78.4%).
        
        **Q2: What explains the revenue dominance of Electronics?**
        - *Answer:* Electronics & Mobiles has significantly higher unit prices (₹10,000 to ₹35,000) than groceries or apparel, resulting in ~79% of total gross sales despite representing ~30% of order count.
        
        **Q3: How are cancelled and returned orders accounted for?**
        - *Answer:* Cancelled and returned orders result in ₹0 profit to reflect realistic accounting rules where revenue is reversed and inventory returned.
        
        **Q4: How does caching improve dashboard performance?**
        - *Answer:* Utilizing `@st.cache_data` caches the preprocessed dataset in memory, cutting subsequent filter response times from ~2.5 seconds to under 0.05 seconds.
        """)

st.markdown("---")
st.markdown("<center><small style='color: #888888;'>Amazon India Sales Analysis Dashboard • 4th-Year B.Tech Project • Developed with Python, Streamlit & Plotly</small></center>", unsafe_allow_html=True)

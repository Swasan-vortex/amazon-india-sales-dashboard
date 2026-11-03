"""
utils.py - Helper functions, formatting utilities, KPI calculations, and chart theming.
Academic Project: 4th-Year B.Tech Data Analytics Dashboard
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Amazon Brand & Visualization Color Palette
COLOR_PRIMARY = "#FF9900"       # Amazon Orange
COLOR_SECONDARY = "#232F3E"     # Amazon Dark Slate Blue
COLOR_NAVY = "#131921"          # Amazon Deep Navy
COLOR_BLUE = "#146EB4"          # Amazon Link Blue
COLOR_GREEN = "#2E7D32"         # Success / Delivered / Profit
COLOR_RED = "#D32F2F"           # Cancelled / Loss
COLOR_AMBER = "#F57C00"         # Returned / Pending
COLOR_PURPLE = "#7B1FA2"        # Secondary Accent
COLOR_CYAN = "#0097A7"          # Analytical Accent

# Category-specific consistent color map
CATEGORY_COLORS = {
    "Electronics & Mobiles": "#146EB4",
    "Home & Kitchen": "#FF9900",
    "Apparel & Fashion": "#7B1FA2",
    "Beauty & Personal Care": "#E91E63",
    "Pantry & Groceries": "#2E7D32",
}

# Order Status color map
STATUS_COLORS = {
    "Delivered": "#2E7D32",
    "Shipped": "#0288D1",
    "Cancelled": "#E53935",
    "Returned": "#FB8C00",
}

# Fulfillment channel color map
FULFILLMENT_COLORS = {
    "Amazon (FBA)": "#FF9900",
    "Seller Flex": "#146EB4",
    "Merchant (FBM)": "#546E7A",
}

# Payment method color map
PAYMENT_COLORS = {
    "UPI": "#673AB7",
    "Credit/Debit Card": "#1E88E5",
    "Cash on Delivery (COD)": "#FB8C00",
    "Net Banking": "#00897B",
    "Amazon Pay Later": "#FFB300",
}


def format_inr(val: float, compact: bool = True) -> str:
    """
    Format numeric values into Indian Rupee (INR) representation.
    Supports Crore (Cr) and Lakh (L) compact notations.
    """
    if val is None or np.isnan(val):
        return "₹ 0"

    sign = "-" if val < 0 else ""
    abs_val = abs(val)

    if compact:
        if abs_val >= 10_000_000:
            return f"{sign}₹ {abs_val / 10_000_000:.2f} Cr"
        elif abs_val >= 100_000:
            return f"{sign}₹ {abs_val / 100_000:.2f} L"
        elif abs_val >= 1_000:
            return f"{sign}₹ {abs_val / 1_000:.1f} K"
        else:
            return f"{sign}₹ {abs_val:,.2f}"
    else:
        return f"{sign}₹ {abs_val:,.2f}"


def format_number(val: int or float) -> str:
    """
    Format integer count with comma separators.
    """
    if val is None or np.isnan(val):
        return "0"
    return f"{int(val):,}"


def format_percent(val: float, decimals: int = 2) -> str:
    """
    Format decimal float to percentage string.
    """
    if val is None or np.isnan(val):
        return "0.0%"
    return f"{val:.{decimals}f}%"


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Compute essential e-commerce business KPIs from the filtered dataframe.
    """
    total_orders = len(df)
    if total_orders == 0:
        return {
            "total_sales": 0.0,
            "total_profit": 0.0,
            "profit_margin": 0.0,
            "total_orders": 0,
            "total_quantity": 0,
            "aov": 0.0,
            "delivered_orders": 0,
            "delivery_rate": 0.0,
            "cancelled_orders": 0,
            "cancellation_rate": 0.0,
            "returned_orders": 0,
            "return_rate": 0.0,
            "avg_discount": 0.0,
        }

    total_sales = float(df["Total_Sales_INR"].sum())
    total_profit = float(df["Profit_INR"].sum())
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0.0
    total_quantity = int(df["Quantity"].sum())
    aov = (total_sales / total_orders) if total_orders > 0 else 0.0

    # Status counts and percentages
    status_counts = df["Order_Status"].value_counts().to_dict()
    delivered_orders = status_counts.get("Delivered", 0)
    cancelled_orders = status_counts.get("Cancelled", 0)
    returned_orders = status_counts.get("Returned", 0)
    shipped_orders = status_counts.get("Shipped", 0)

    delivery_rate = (delivered_orders / total_orders * 100)
    cancellation_rate = (cancelled_orders / total_orders * 100)
    return_rate = (returned_orders / total_orders * 100)
    avg_discount = float(df["Discount_Pct"].mean() * 100)

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "aov": aov,
        "delivered_orders": delivered_orders,
        "delivery_rate": delivery_rate,
        "cancelled_orders": cancelled_orders,
        "cancellation_rate": cancellation_rate,
        "returned_orders": returned_orders,
        "return_rate": return_rate,
        "shipped_orders": shipped_orders,
        "avg_discount": avg_discount,
    }


def apply_chart_theme(
    fig: go.Figure,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    height: int = 420,
    show_legend: bool = True
) -> go.Figure:
    """
    Applies a clean, modern, student-friendly visual theme to Plotly figures.
    """
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "x": 0.02,
            "xanchor": "left",
            "font": {"size": 16, "color": COLOR_SECONDARY, "family": "Inter, sans-serif"}
        },
        height=height,
        margin={"l": 40, "r": 30, "t": 60, "b": 40},
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font={"family": "Inter, Segoe UI, sans-serif", "size": 12, "color": "#333333"},
        showlegend=show_legend,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1.0,
            "bgcolor": "rgba(255, 255, 255, 0.8)",
            "bordercolor": "rgba(0, 0, 0, 0.08)",
            "borderwidth": 1
        },
        hoverlabel={
            "bgcolor": COLOR_SECONDARY,
            "font_size": 13,
            "font_family": "Inter, sans-serif",
            "font_color": "#FFFFFF"
        }
    )

    fig.update_xaxes(
        title_text=x_title,
        showgrid=True,
        gridcolor="#F0F0F0",
        linecolor="#CCCCCC",
        zeroline=False
    )
    fig.update_yaxes(
        title_text=y_title,
        showgrid=True,
        gridcolor="#F0F0F0",
        linecolor="#CCCCCC",
        zeroline=False
    )
    return fig

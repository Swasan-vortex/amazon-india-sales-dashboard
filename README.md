# 📦 Amazon India Sales Analysis Dashboard

> **Academic Final Year Project (4th-Year B.Tech)**  
> **Domain:** Data Analytics, Business Intelligence & Interactive Dashboard Development  
> **Tech Stack:** Python 3, Streamlit, Pandas, NumPy, Plotly, OpenPyXL  

---

## 📌 1. Project Overview & Objective

The **Amazon India Sales Analysis Dashboard** is an interactive, analytical web application developed to analyze real-world e-commerce sales transactions across India. The objective of this project is to convert raw transactional data into meaningful business metrics, key performance indicators (KPIs), dynamic charts, and executive insights.

### Core Objectives:
1. **Sales & Profit Generation:** Quantify overall sales revenue (₹15.58 Crore) and net profit (₹3.32 Crore), along with net profit margins across time.
2. **Category & Product Performance:** Analyze which categories (Electronics, Home, Fashion, Beauty, Pantry) and individual items generate the highest revenue and margins.
3. **Logistics & Order Distribution:** Track completion across order statuses (*Delivered, Shipped, Cancelled, Returned*) and compare fulfillment efficiency (*Amazon FBA, Seller Flex, Merchant FBM*).
4. **Payment Preferences:** Evaluate customer payment behavior across UPI, Credit/Debit Cards, Cash on Delivery (COD), Net Banking, and Amazon Pay Later.
5. **Geographic Distribution:** Identify top revenue-generating Indian states and regional profit drivers.

---

## 📊 2. Dataset Overview

The dataset contains **10,000 verified transaction records** spanning **January 2024 to August 2026** across **13 attributes**:

| Attribute | Data Type | Description | Sample Values |
| :--- | :--- | :--- | :--- |
| `Order_ID` | String | Unique transaction identifier | `IN-AMD-100000`, `IN-AMD-100001` |
| `Order_Date` | Date | Date when order was placed | `2024-04-12`, `2025-03-11` |
| `Category` | Categorical | Broad product sector (5 unique) | `Apparel & Fashion`, `Electronics & Mobiles` |
| `Product` | Categorical | Specific product sold (25 unique) | `5G Smartphone`, `Wireless Earbuds` |
| `Quantity` | Integer | Units ordered per transaction (1 to 4) | `1`, `2`, `3`, `4` |
| `Unit_Price_INR` | Float | Base price per individual unit | `₹ 1,129.14`, `₹ 20,928.14` |
| `Discount_Pct` | Float | Discount percentage applied | `0.00`, `0.05`, `0.10`, `0.15`, `0.20`, `0.25` |
| `Total_Sales_INR` | Float | Net sales revenue generated | `₹ 2,540.56`, `₹ 79,526.93` |
| `Profit_INR` | Float | Net profit earned (₹0 for cancelled/returned) | `₹ 702.96`, `₹ 26,466.63` |
| `Payment_Method`| Categorical | Mode of customer payment (5 modes) | `UPI`, `Credit/Debit Card`, `COD` |
| `Fulfillment` | Categorical | Order logistics channel (3 methods) | `Amazon (FBA)`, `Seller Flex`, `Merchant (FBM)` |
| `Order_Status` | Categorical | Delivery lifecycle stage (4 statuses) | `Delivered`, `Shipped`, `Cancelled`, `Returned` |
| `Ship_State` | Categorical | Destination Indian State (10 states) | `Maharashtra`, `Karnataka`, `Delhi` |

---

## 🏗️ 3. Project Structure

```text
Amazon India Dashboard/
│
├── app.py                      # Main Streamlit dashboard application
├── data_loader.py              # Data loading, cleaning, feature engineering & caching
├── utils.py                    # Currency formatting, KPI calculations & Plotly chart theming
├── Amazon Sales Data India.xlsx# Primary source dataset (10,000 records)
├── requirements.txt            # Python dependencies
└── README.md                   # Academic project documentation & viva guide
```

---

## 🛠️ 4. Technology Stack & Justification

- **Python 3:** Highly flexible, readable language standard for data science.
- **Streamlit:** Python-native framework allowing rapid development of interactive web dashboards without HTML/CSS/JS boilerplate.
- **Pandas:** Vectorized data manipulation, aggregations, filtering, and cross-tabulations.
- **NumPy:** Mathematical calculations for profit margins and conditional arrays.
- **Plotly Express & Graph Objects:** Interactive, responsive, publication-quality visualizations with native hover tooltips and zoom capabilities.
- **OpenPyXL:** Engine for reading and parsing `.xlsx` Microsoft Excel files.

---

## 🚀 5. Installation & Execution Guide

### Prerequisites:
Ensure you have **Python 3.10+** installed on your system.

### Step 1: Open Terminal / Command Prompt
Navigate to the project root directory:
```bash
cd "c:\Users\Aditi Upadhyay\OneDrive\Desktop\Amazon India Dashboard"
```

### Step 2: Install Dependencies
Install all required libraries using `pip`:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Dashboard
Launch the dashboard locally:
```bash
streamlit run app.py
```
*Or using the Python module syntax:*
```bash
python -m streamlit run app.py
```

### Step 4: Open in Web Browser
Streamlit will automatically open your default browser at:
```text
http://localhost:8501
```

---

## 💡 6. Key Business Insights & Analytical Findings

1. **Category Revenue Asymmetry:**
   - *Electronics & Mobiles* generates **79.3%** of total business revenue (₹12.36 Cr) due to high unit selling prices (₹10,000 – ₹35,000), even though it accounts for only ~30% of total order volume.
   - *Pantry & Groceries* and *Beauty* are high-frequency, everyday staples with lower basket sizes but steady profit margins (~21.5%).

2. **The Indian Digital Payment Revolution:**
   - **UPI is the uncontested leader**, driving **49.7%** of all transactions (4,972 orders), reflecting India's massive adoption of instant QR and UPI payments.
   - *Cash on Delivery (COD)* accounts for **14.6%** of orders, serving customers in tier-2/3 areas who prefer cash payment at doorstep.

3. **Logistics & Fulfillment Advantage:**
   - **Amazon FBA (Fulfilled by Amazon)** handles **70.5%** of shipments with the highest successful delivery rate (**82.0%**), compared to **78.4%** for Merchant FBM.
   - Using FBA significantly reduces transit friction and customer returns.

4. **Tri-State Economic Concentration:**
   - **Maharashtra (19.0%)**, **Karnataka (15.7%)**, and **Delhi (14.4%)** generate almost **50%** of total sales revenue. The presence of major commercial hubs (Mumbai, Pune, Bengaluru, Delhi NCR) drives this concentration.

5. **Discounting & Profit Margin Stability:**
   - Profit margins remain resilient at **21.29%** across all 10 states. Moderate discounts (5% – 10%) boost volume without hurting profitability.

---

## 🎓 7. Academic Viva & Defense Questions Guide

Here are standard questions often asked by internal and external academic project examiners:

- **Q1: Why did you choose Streamlit instead of Flask or Django?**
  - *Answer:* Flask/Django are general-purpose web frameworks requiring separate frontend templates (HTML/CSS/JS) and API endpoints. Streamlit allows direct, reactive data binding between Pandas/Plotly and UI widgets in pure Python, making it ideal for data analysis capstone projects.

- **Q2: How does the application handle dashboard performance with 10,000 rows?**
  - *Answer:* We employ `@st.cache_data` in `data_loader.py`. The Excel parsing is performed once and stored in memory. Subsequent filter selections compute on in-memory vectorized Pandas arrays, executing in less than 50 milliseconds.

- **Q3: Why is net profit recorded as ₹0 for cancelled and returned orders?**
  - *Answer:* From an e-commerce accounting perspective, cancelled orders never settle and returned orders involve inventory write-backs and shipping reversals, resulting in zero realized profit.

- **Q4: What are the main limitations and future scopes of this project?**
  - *Answer:* Currently, the dataset is static Excel. Future enhancements could include connecting directly to a live PostgreSQL/MySQL database, implementing predictive machine learning models for customer lifetime value (CLV), and forecasting demand using ARIMA/Prophet.

---

## 👤 Author
- **Final Year B.Tech Student Project**
- Academic Year: 2026

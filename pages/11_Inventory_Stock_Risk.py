import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Inventory & Stock Risk", page_icon="📦", layout="wide")
load_css()

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def get_data():
    return load_sales_data()

raw_df = get_data()
df = raw_df.copy()

# Clean data
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date', 'Product Name']).reset_index(drop=True)
df['Sales Amount'] = pd.to_numeric(df['Sales Amount'], errors='coerce').fillna(0)
df['Purchase Value'] = pd.to_numeric(df['Purchase Value'], errors='coerce').fillna(0)
df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)

# Derived
df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>📦 Inventory & Stock Risk Analysis</h1>
    <p>Identify fast-moving products, dead stock, and reorder priorities based on sales velocity</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">⚙️ ANALYSIS PERIOD</div>', unsafe_allow_html=True)
    
    # How many days back to consider "recent"
    analysis_days = st.slider(
        "Recent Sales Window (Days)",
        min_value=30, max_value=365, value=90, step=30,
        help="Used to measure 'recent velocity' for stock risk"
    )
    
    st.markdown('<div class="filter-label">📍 FILTERS</div>', unsafe_allow_html=True)
    categories = df['Product Category'].dropna().unique()
    selected_categories = st.multiselect("Product Category", options=categories, default=categories)

    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Sales Zone", options=zones, default=zones)

    st.markdown("---")
    st.markdown('<div class="filter-label">⚡ RISK THRESHOLDS</div>', unsafe_allow_html=True)
    
    stockout_percentile = st.slider(
        "Stock-Out Risk Threshold (Percentile)",
        min_value=50, max_value=99, value=80, step=5,
        help="Products in the top X% by recent velocity are flagged as stock-out risk"
    )
    overstock_percentile = st.slider(
        "Overstock Risk Threshold (Percentile)",
        min_value=1, max_value=50, value=20, step=5,
        help="Products in the bottom X% by recent velocity are flagged as overstock"
    )

# Filter
filtered = df[
    (df['Product Category'].isin(selected_categories)) &
    (df['Sales Zone'].isin(selected_zones))
].copy()

if len(filtered) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# ============================================================================
# COMPUTE VELOCITY & RISK METRICS
# ============================================================================
# Latest date in the filtered dataset
max_date = filtered['Date'].max()
cutoff_date = max_date - pd.Timedelta(days=analysis_days)

# Recent data
recent = filtered[filtered['Date'] >= cutoff_date].copy()

# If no recent data, fall back to full dataset
if len(recent) == 0:
    st.warning(f"No data in the last {analysis_days} days. Showing full period data instead.")
    recent = filtered.copy()

# ============================================================================
# PRODUCT-LEVEL METRICS
# ============================================================================
# Recent velocity
recent_velocity = (
    recent.groupby('Product Name')
    .agg({
        'Sales Amount': 'sum',
        'Invoice No': 'nunique',
        'Discount': 'mean',
        'Gross Profit': 'sum'
    })
    .reset_index()
)
recent_velocity.columns = ['Product Name', 'Recent_Sales', 'Recent_Orders', 'Avg_Discount', 'Recent_Profit']

# Historical (all-time) metrics
historical = (
    filtered.groupby('Product Name')
    .agg({
        'Sales Amount': 'sum',
        'Invoice No': 'nunique',
        'Gross Profit': 'sum',
        'Product Category': 'first'
    })
    .reset_index()
)
historical.columns = ['Product Name', 'Total_Sales', 'Total_Orders', 'Total_Profit', 'Product Category']

# Merge
product_df = historical.merge(recent_velocity, on='Product Name', how='left')
product_df[['Recent_Sales', 'Recent_Orders', 'Avg_Discount', 'Recent_Profit']] = (
    product_df[['Recent_Sales', 'Recent_Orders', 'Avg_Discount', 'Recent_Profit']].fillna(0)
)

# Velocity per day
product_df['Recent_Velocity'] = product_df['Recent_Sales'] / analysis_days
product_df['Recent_Order_Velocity'] = product_df['Recent_Orders'] / analysis_days

# Velocity change ratio (recent vs historical daily rate)
product_df['Historic_Velocity'] = product_df['Total_Sales'] / max((filtered['Date'].max() - filtered['Date'].min()).days, 1)
product_df['Velocity_Change'] = np.where(
    product_df['Historic_Velocity'] > 0,
    product_df['Recent_Velocity'] / product_df['Historic_Velocity'],
    1
)

# ============================================================================
# CLASSIFY RISK
# ============================================================================
stockout_thresh = np.percentile(product_df['Recent_Velocity'], stockout_percentile)
overstock_thresh = np.percentile(product_df['Recent_Velocity'], overstock_percentile)

def classify_risk(row):
    v = row['Recent_Velocity']
    if v >= stockout_thresh:
        return "🚨 High Stock-Out Risk"
    elif v <= overstock_thresh and v < stockout_thresh:
        return "❄️ Overstock / Dead Stock"
    else:
        return "✅ Healthy"

product_df['Risk_Status'] = product_df.apply(classify_risk, axis=1)

# ============================================================================
# KPI METRICS
# ============================================================================
stockout_count = len(product_df[product_df['Risk_Status'] == '🚨 High Stock-Out Risk'])
overstock_count = len(product_df[product_df['Risk_Status'] == '❄️ Overstock / Dead Stock'])
healthy_count = len(product_df[product_df['Risk_Status'] == '✅ Healthy'])

stockout_value = product_df[product_df['Risk_Status'] == '🚨 High Stock-Out Risk']['Recent_Sales'].sum()
overstock_value = product_df[product_df['Risk_Status'] == '❄️ Overstock / Dead Stock']['Total_Sales'].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📦</div>
        <div class="metric-value">{len(product_df):,}</div>
        <div class="metric-label">Total Products</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🚨</div>
        <div class="metric-value" style="color:#e74c3c;">{stockout_count}</div>
        <div class="metric-label">Stock-Out Risk</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">❄️</div>
        <div class="metric-value" style="color:#3498db;">{overstock_count}</div>
        <div class="metric-label">Overstock Risk</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-value" style="color:#2ecc71;">{healthy_count}</div>
        <div class="metric-label">Healthy Products</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHARTS ROW 1: VELOCITY DISTRIBUTION
# ============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">📊 Velocity Distribution (Risk Classification)</div>', unsafe_allow_html=True)
    
    fig = px.histogram(
        product_df, x='Recent_Velocity', color='Risk_Status',
        nbins=30, color_discrete_map={
            '🚨 High Stock-Out Risk': '#e74c3c',
            '❄️ Overstock / Dead Stock': '#3498db',
            '✅ Healthy': '#2ecc71'
        },
        labels={'Recent_Velocity': 'Daily Sales Velocity (৳/day)', 'Risk_Status': 'Risk'}
    )
    fig.update_layout(height=400, xaxis_title='Daily Sales Velocity (৳/day)', yaxis_title='# Products', barmode='overlay')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">💰 Revenue at Risk (By Status)</div>', unsafe_allow_html=True)
    
    status_summary = product_df.groupby('Risk_Status').agg({
        'Total_Sales': 'sum',
        'Recent_Sales': 'sum'
    }).reset_index()
    
    fig = px.bar(
        status_summary, x='Risk_Status', y='Total_Sales',
        color='Risk_Status',
        color_discrete_map={
            '🚨 High Stock-Out Risk': '#e74c3c',
            '❄️ Overstock / Dead Stock': '#3498db',
            '✅ Healthy': '#2ecc71'
        },
        text='Total_Sales'
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='', yaxis_title='Total Sales (৳)')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# TOP STOCK-OUT RISK PRODUCTS (Reorder Priority)
# ============================================================================
st.markdown('<div class="section-header">🚨 Reorder Priority (Top Stock-Out Risk)</div>', unsafe_allow_html=True)
st.caption(f"Products with recent velocity ≥ ৳{stockout_thresh:,.0f}/day. **Order these first!**")

reorder_priority = product_df[product_df['Risk_Status'] == '🚨 High Stock-Out Risk'].sort_values('Recent_Velocity', ascending=False)

if len(reorder_priority) > 0:
    reorder_display = reorder_priority.head(15)[
        ['Product Name', 'Product Category', 'Recent_Velocity', 'Recent_Orders', 'Recent_Profit', 'Velocity_Change']
    ].copy()
    
    reorder_display['Recent_Velocity'] = reorder_display['Recent_Velocity'].apply(lambda x: f"৳{x:,.0f}/day")
    reorder_display['Recent_Profit'] = reorder_display['Recent_Profit'].apply(lambda x: f"৳{x:,.0f}")
    reorder_display['Velocity_Change'] = reorder_display['Velocity_Change'].apply(lambda x: f"{x:.2f}x")
    reorder_display.columns = ['Product', 'Category', 'Velocity', 'Orders', 'Recent Profit', 'Speed Change']
    
    st.dataframe(reorder_display, use_container_width=True, hide_index=True)
else:
    st.success("✅ No products currently at stock-out risk.")

st.markdown("---")

# ============================================================================
# OVERSTOCK / DEAD STOCK PRODUCTS
# ============================================================================
st.markdown('<div class="section-header">❄️ Overstock / Slow-Moving Products</div>', unsafe_allow_html=True)
st.caption(f"Products with recent velocity ≤ ৳{overstock_thresh:,.0f}/day. **Consider discounting or liquidating.**")

overstock_products = product_df[product_df['Risk_Status'] == '❄️ Overstock / Dead Stock'].sort_values('Recent_Velocity')

if len(overstock_products) > 0:
    overstock_display = overstock_products.head(15)[
        ['Product Name', 'Product Category', 'Recent_Velocity', 'Total_Sales', 'Avg_Discount', 'Velocity_Change']
    ].copy()
    
    overstock_display['Recent_Velocity'] = overstock_display['Recent_Velocity'].apply(lambda x: f"৳{x:,.0f}/day")
    overstock_display['Total_Sales'] = overstock_display['Total_Sales'].apply(lambda x: f"৳{x:,.0f}")
    overstock_display['Avg_Discount'] = overstock_display['Avg_Discount'].apply(lambda x: f"৳{x:,.0f}")
    overstock_display['Velocity_Change'] = overstock_display['Velocity_Change'].apply(lambda x: f"{x:.2f}x")
    overstock_display.columns = ['Product', 'Category', 'Velocity', 'Total Sales', 'Avg Discount', 'Speed Change']
    
    st.dataframe(overstock_display, use_container_width=True, hide_index=True)
else:
    st.success("✅ No overstock products detected.")

st.markdown("---")

# ============================================================================
# PRODUCT VELOCITY SCATTER (All Products)
# ============================================================================
st.markdown('<div class="section-header">🎯 Velocity vs Profitability Map</div>', unsafe_allow_html=True)

fig = px.scatter(
    product_df,
    x='Recent_Velocity', y='Recent_Profit',
    color='Risk_Status',
    size='Total_Sales',
    hover_name='Product Name',
    color_discrete_map={
        '🚨 High Stock-Out Risk': '#e74c3c',
        '❄️ Overstock / Dead Stock': '#3498db',
        '✅ Healthy': '#2ecc71'
    },
    labels={'Recent_Velocity': 'Daily Sales Velocity (৳/day)', 'Recent_Profit': 'Recent Gross Profit (৳)'}
)
fig.add_vline(x=stockout_thresh, line_dash="dash", line_color="red", annotation_text="Stock-Out Threshold")
fig.add_vline(x=overstock_thresh, line_dash="dash", line_color="blue", annotation_text="Overstock Threshold")
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.caption("Bubble size = Total Sales. Top-right products are high-velocity AND profitable — prioritize these.")

st.markdown("---")

# ============================================================================
# FULL PRODUCT INVENTORY TABLE
# ============================================================================
st.markdown('<div class="section-header">📋 Full Inventory & Risk Table</div>', unsafe_allow_html=True)

full_export = product_df[[
    'Product Name', 'Product Category', 'Risk_Status',
    'Recent_Velocity', 'Historic_Velocity', 'Velocity_Change',
    'Total_Sales', 'Recent_Sales', 'Total_Orders', 'Total_Profit'
]].copy()

full_export = full_export.sort_values('Recent_Velocity', ascending=False)
full_export.columns = [
    'Product', 'Category', 'Risk Status',
    'Daily Velocity (৳)', 'Historic Velocity (৳)', 'Speed Change',
    'Total Sales (৳)', 'Recent Sales (৳)', 'Orders', 'Profit (৳)'
]

# Format for display
display_full = full_export.copy()
for col in ['Daily Velocity (৳)', 'Historic Velocity (৳)', 'Total Sales (৳)', 'Recent Sales (৳)', 'Profit (৳)']:
    display_full[col] = display_full[col].apply(lambda x: f"৳{x:,.0f}")
display_full['Speed Change'] = display_full['Speed Change'].apply(lambda x: f"{x:.2f}x")

st.dataframe(display_full, use_container_width=True, hide_index=True, height=400)

# Download
csv = full_export.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Full Inventory Report (CSV)",
    data=csv,
    file_name="inventory_stock_risk.csv",
    mime="text/csv",
    type="primary"
)

st.markdown("""
<div class="dashboard-footer">
    <p>Inventory & Stock Risk | Velocity-based product risk analysis</p>
</div>
""", unsafe_allow_html=True)
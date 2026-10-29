"""
Enterprise Sales Analytics Dashboard
Professional Dashboard with Sidebar Navigation and Global Filters
"""

import streamlit as st
from utils.data_loader import load_sales_data
from utils.session_state import initialize_session_state, apply_filters, reset_filters
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import numpy as np

# Page configuration - MUST be first
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css = """
    <style>
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Sidebar Logo */
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
    }
    
    .sidebar-logo-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-logo-title {
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    .sidebar-logo-subtitle {
        font-size: 0.7rem;
        opacity: 0.7;
    }
    
    /* Filter Section */
    .filter-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: bold;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar Summary */
    .sidebar-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        margin-top: 1rem;
    }
    
    .sidebar-summary-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .sidebar-summary-label {
        font-size: 0.7rem;
        opacity: 0.8;
        text-transform: uppercase;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 1rem;
        padding: 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.3s;
        border: 1px solid #e0e0e0;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1.5rem 0 1rem 0;
        padding-left: 0.8rem;
        border-left: 4px solid #667eea;
    }
    
    /* Insight Cards */
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 0.8rem;
        padding: 1rem;
        color: white;
        height: 100%;
    }
    
    .insight-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }
    
    .insight-card p {
        margin: 0;
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    /* Footer */
    .dashboard-footer {
        text-align: center;
        padding: 2rem;
        margin-top: 2rem;
        border-top: 1px solid #e0e0e0;
        color: #7f8c8d;
        font-size: 0.75rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# Load data
@st.cache_data
def get_data():
    df = load_sales_data()
    return df

# Initialize
df = get_data()
initialize_session_state(df)

# ============================================================================
# SIDEBAR - Global Filters
# ============================================================================

with st.sidebar:
    # Logo and Title
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">📊</div>
        <div class="sidebar-logo-title">Sales Analytics</div>
        <div class="sidebar-logo-subtitle">Enterprise Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Date Range
    st.markdown('<div class="filter-label">📅 DATE RANGE</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=st.session_state.date_start, key="start_date")
    with col2:
        end_date = st.date_input("To", value=st.session_state.date_end, key="end_date")
    
    st.session_state.date_start = start_date
    st.session_state.date_end = end_date
    
    st.markdown("---")
    
    # Region Filter
    st.markdown('<div class="filter-label">📍 REGIONS</div>', unsafe_allow_html=True)
    st.session_state.selected_regions = st.multiselect(
        "Select regions",
        options=st.session_state.region_options,
        default=st.session_state.selected_regions
    )
    
    st.markdown("---")
    
    # Product Filter
    st.markdown('<div class="filter-label">🛍️ PRODUCTS</div>', unsafe_allow_html=True)
    st.session_state.selected_products = st.multiselect(
        "Select products",
        options=st.session_state.product_options,
        default=st.session_state.selected_products
    )
    
    st.markdown("---")
    
    # Customer Type Filter
    st.markdown('<div class="filter-label">👥 CUSTOMER TYPE</div>', unsafe_allow_html=True)
    st.session_state.selected_customer_types = st.multiselect(
        "Select customer types",
        options=st.session_state.customer_options,
        default=st.session_state.selected_customer_types
    )
    
    st.markdown("---")
    
    # Discount Range
    st.markdown('<div class="filter-label">💰 DISCOUNT RANGE</div>', unsafe_allow_html=True)
    discount_range = st.slider(
        "Discount percentage",
        min_value=0,
        max_value=50,
        value=(st.session_state.discount_min, st.session_state.discount_max),
        step=5
    )
    st.session_state.discount_min, st.session_state.discount_max = discount_range
    
    st.markdown("---")
    
    # Returned Filter
    st.markdown('<div class="filter-label">📦 ORDER STATUS</div>', unsafe_allow_html=True)
    st.session_state.show_only_returned = st.checkbox(
        "Show returned orders only",
        value=st.session_state.show_only_returned
    )
    
    st.markdown("---")
    
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Apply", use_container_width=True):
            apply_filters()
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            reset_filters(df)
            st.rerun()
    
    st.markdown("---")
    
    # Summary Card
    current_df = st.session_state.filtered_df
    st.markdown(f"""
    <div class="sidebar-summary">
        <div class="sidebar-summary-value">{len(current_df):,}</div>
        <div class="sidebar-summary-label">Total Records</div>
        <div class="sidebar-summary-value" style="font-size: 1.2rem;">${current_df['totalprice'].sum():,.0f}</div>
        <div class="sidebar-summary-label">Total Revenue</div>
        <div class="sidebar-summary-value" style="font-size: 1.2rem;">{current_df['customername'].nunique():,}</div>
        <div class="sidebar-summary-label">Unique Customers</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Get filtered data
filtered_df = st.session_state.filtered_df

# Main Header
st.markdown(f"""
<div class="main-header">
    <h1>📊 Enterprise Sales Analytics Dashboard</h1>
    <p>Real-time insights for data-driven decision making | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# Check if no data
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filters. Please adjust your criteria.")
    st.stop()

# ============================================================================
# KEY METRICS
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💰</div>
        <div class="metric-value">${filtered_df['totalprice'].sum():,.0f}</div>
        <div class="metric-label">Total Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    profit = filtered_df['profit'].sum() if 'profit' in filtered_df.columns else filtered_df['totalprice'].sum() * 0.3
    margin = filtered_df['profitmargin'].mean() if 'profitmargin' in filtered_df.columns else 30
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value">${profit:,.0f}</div>
        <div class="metric-label">Total Profit</div>
        <div class="metric-label" style="font-size:0.7rem;">Margin: {margin:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    return_rate = (filtered_df['returned'].sum() / len(filtered_df)) * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📦</div>
        <div class="metric-value">{return_rate:.1f}%</div>
        <div class="metric-label">Return Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_delivery = filtered_df['deliverydays'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🚚</div>
        <div class="metric-value">{avg_delivery:.1f} days</div>
        <div class="metric-label">Avg Delivery</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHARTS ROW 1
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">💰 Revenue by Region</div>', unsafe_allow_html=True)
    region_revenue = filtered_df.groupby('region')['totalprice'].sum().sort_values(ascending=False)
    fig = px.bar(
        x=region_revenue.values, 
        y=region_revenue.index, 
        orientation='h',
        color=region_revenue.values,
        color_continuous_scale='Viridis',
        text=region_revenue.values
    )
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='Revenue ($)', yaxis_title='Region')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">👥 Revenue by Customer Type</div>', unsafe_allow_html=True)
    customer_revenue = filtered_df.groupby('customertype')['totalprice'].sum().reset_index()
    fig = px.pie(
        customer_revenue, 
        values='totalprice', 
        names='customertype',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# CHARTS ROW 2
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🏆 Top 10 Products</div>', unsafe_allow_html=True)
    top_products = filtered_df.groupby('product')['totalprice'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(
        x=top_products.values, 
        y=top_products.index, 
        orientation='h',
        color=top_products.values,
        color_continuous_scale='Plasma',
        text=top_products.values
    )
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(height=500, showlegend=False, xaxis_title='Revenue ($)', yaxis_title='Product')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📈 Monthly Trend</div>', unsafe_allow_html=True)
    filtered_df['month_str'] = filtered_df['orderdate'].dt.strftime('%Y-%m')
    monthly = filtered_df.groupby('month_str')['totalprice'].sum().reset_index()
    fig = px.line(
        monthly, 
        x='month_str', 
        y='totalprice',
        markers=True,
        line_shape='linear'
    )
    fig.update_traces(line=dict(color='#667eea', width=3), marker=dict(size=8))
    fig.update_layout(height=400, xaxis_title='Month', yaxis_title='Revenue ($)')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# INSIGHTS SECTION
# ============================================================================

st.markdown('<div class="section-header">💡 Key Insights</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    top_region = filtered_df.groupby('region')['totalprice'].sum().idxmax()
    top_region_pct = (filtered_df[filtered_df['region'] == top_region]['totalprice'].sum() / filtered_df['totalprice'].sum()) * 100
    st.markdown(f"""
    <div class="insight-card">
        <h4>🎯 Top Performing Region</h4>
        <p><strong>{top_region}</strong> generates <strong>{top_region_pct:.1f}%</strong> of total revenue.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    high_discount = filtered_df[filtered_df['discount'] > 0.2]
    no_discount = filtered_df[filtered_df['discount'] == 0]
    if len(high_discount) > 0 and len(no_discount) > 0 and no_discount['profit'].mean() > 0:
        impact = (1 - high_discount['profit'].mean() / no_discount['profit'].mean()) * 100
        st.markdown(f"""
        <div class="insight-card">
            <h4>⚠️ Discount Impact</h4>
            <p>Discounts >20% reduce profit by <strong>{impact:.0f}%</strong>.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="insight-card">
            <h4>⚠️ Discount Strategy</h4>
            <p>Review your discount strategy to optimize profits.</p>
        </div>
        """, unsafe_allow_html=True)

with col3:
    vip_revenue = filtered_df[filtered_df['customertype'] == 'VIP']['totalprice'].sum()
    vip_pct = (vip_revenue / filtered_df['totalprice'].sum()) * 100 if filtered_df['totalprice'].sum() > 0 else 0
    st.markdown(f"""
    <div class="insight-card">
        <h4>👑 VIP Customers</h4>
        <p>VIP customers generate <strong>{vip_pct:.1f}%</strong> of revenue.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# DATA PREVIEW
# ============================================================================

with st.expander("📋 View Transaction Data"):
    display_cols = ['orderid', 'orderdate', 'region', 'product', 'customertype', 
                   'quantity', 'unitprice', 'discount', 'totalprice', 'deliverydays', 'returned']
    available_cols = [col for col in display_cols if col in filtered_df.columns]
    display_df = filtered_df[available_cols].copy().head(100)
    
    if 'returned' in display_df.columns:
        display_df['returned'] = display_df['returned'].apply(lambda x: '✅ Yes' if x else '❌ No')
    if 'discount' in display_df.columns:
        display_df['discount'] = (display_df['discount'] * 100).round(1).astype(str) + '%'
    
    st.dataframe(display_df, use_container_width=True)
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download Data (CSV)", csv, "sales_data.csv", "text/csv")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class="dashboard-footer">
    <p>Sales Analytics Dashboard | Powered by Streamlit & Plotly</p>
    <p>Global filters apply to all data | Data refreshes on page reload</p>
</div>
""", unsafe_allow_html=True)
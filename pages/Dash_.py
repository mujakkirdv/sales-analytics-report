import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_sales_data, load_css
from datetime import datetime

# Page config
st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">📍 SALES ZONE</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Select Zones", options=zones, default=zones)

    st.markdown('<div class="filter-label">👥 CUSTOMER TYPE</div>', unsafe_allow_html=True)
    customer_types = df['Customer Type'].dropna().unique()
    selected_types = st.multiselect("Select Customer Types", options=customer_types, default=customer_types)

    st.markdown('<div class="filter-label">🛍️ PRODUCT CATEGORY</div>', unsafe_allow_html=True)
    categories = df['Product Category'].dropna().unique()
    selected_categories = st.multiselect("Select Categories", options=categories, default=categories)

# Apply Filters
filtered_df = df[
    (df['Sales Zone'].isin(selected_zones)) & 
    (df['Customer Type'].isin(selected_types)) &
    (df['Product Category'].isin(selected_categories))
]

# Main Header
st.markdown(f"""
<div class="main-header">
    <h1>📈 Sales Dashboard</h1>
    <p>Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')} | {len(filtered_df):,} records found</p>
</div>
""", unsafe_allow_html=True)

if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# ============================================================================
# METRICS
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💰</div>
        <div class="metric-value">৳{filtered_df['Sales Amount'].sum():,.0f}</div>
        <div class="metric-label">Total Sales Amount</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🧾</div>
        <div class="metric-value">{filtered_df['Invoice No'].nunique():,}</div>
        <div class="metric-label">Total Invoices</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📦</div>
        <div class="metric-value">{filtered_df['Product Name'].nunique():,}</div>
        <div class="metric-label">Unique Products</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_invoice = filtered_df['Invoice Value'].mean() if filtered_df['Invoice Value'].mean() > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-value">৳{avg_invoice:,.0f}</div>
        <div class="metric-label">Avg Invoice Value</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHARTS
# ============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">📍 Sales by Zone</div>', unsafe_allow_html=True)
    zone_sales = filtered_df.groupby('Sales Zone')['Sales Amount'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(zone_sales, x='Sales Amount', y='Sales Zone', orientation='h',
                 color='Sales Amount', color_continuous_scale='Viridis', text='Sales Amount')
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='Sales Amount', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">👥 Sales by Customer Type</div>', unsafe_allow_html=True)
    type_sales = filtered_df.groupby('Customer Type')['Sales Amount'].sum().reset_index()
    fig = px.pie(type_sales, values='Sales Amount', names='Customer Type',
                 color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🏆 Top 10 Products</div>', unsafe_allow_html=True)
    top_products = filtered_df.groupby('Product Name')['Sales Amount'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(top_products, x='Sales Amount', y='Product Name', orientation='h',
                 color='Sales Amount', color_continuous_scale='Plasma', text='Sales Amount')
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=500, showlegend=False, xaxis_title='Sales Amount', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📈 Sales Trend by Month</div>', unsafe_allow_html=True)
    if 'Month Name' in filtered_df.columns:
        # Force chronological sorting
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        monthly = filtered_df.groupby('Month Name')['Sales Amount'].sum().reset_index()
        monthly['Month Name'] = pd.Categorical(monthly['Month Name'], categories=month_order, ordered=True)
        monthly = monthly.sort_values('Month Name')
        
        fig = px.line(monthly, x='Month Name', y='Sales Amount', markers=True)
        fig.update_traces(line=dict(color='#667eea', width=3), marker=dict(size=8))
        fig.update_layout(height=400, xaxis_title='Month', yaxis_title='Sales Amount')
        st.plotly_chart(fig, use_container_width=True)
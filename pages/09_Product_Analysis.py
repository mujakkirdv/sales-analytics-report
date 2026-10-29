import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Product Analysis", page_icon="🛍️", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Sidebar Filters
with st.sidebar:
    st.markdown('<div class="filter-label">📍 SALES ZONE</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Zones", options=zones, default=zones)
    
    st.markdown('<div class="filter-label">📦 PRODUCT CATEGORY</div>', unsafe_allow_html=True)
    categories = df['Product Category'].dropna().unique()
    selected_categories = st.multiselect("Categories", options=categories, default=categories)

# Filter Data
filtered_df = df[
    (df['Sales Zone'].isin(selected_zones)) & 
    (df['Product Category'].isin(selected_categories))
]

if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1>🛍️ Product Performance Analysis</h1>
    <p>Discover top-selling products, category revenue, and pricing insights</p>
</div>
""", unsafe_allow_html=True)

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Products", filtered_df['Product Name'].nunique())
with col2:
    st.metric("Total Categories", filtered_df['Product Category'].nunique())
with col3:
    avg_price = filtered_df['Sales Amount'].mean()
    st.metric("Avg Item Value", f"৳{avg_price:,.0f}")
with col4:
    total_qty = filtered_df['Invoice No'].nunique()
    st.metric("Total Orders", f"{total_qty:,}")

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🏆 Top 10 Best Sellers</div>', unsafe_allow_html=True)
    top_sellers = filtered_df.groupby('Product Name')['Sales Amount'].sum().nlargest(10).reset_index()
    fig = px.bar(top_sellers, x='Sales Amount', y='Product Name', orientation='h',
                 color='Sales Amount', color_continuous_scale='Viridis', text='Sales Amount')
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="Revenue (৳)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📊 Revenue by Category</div>', unsafe_allow_html=True)
    cat_rev = filtered_df.groupby('Product Category')['Sales Amount'].sum().reset_index()
    fig = px.pie(cat_rev, values='Sales Amount', names='Product Category', hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">📉 Bottom 10 Products</div>', unsafe_allow_html=True)
    bottom_sellers = filtered_df.groupby('Product Name')['Sales Amount'].sum().nsmallest(10).reset_index()
    fig = px.bar(bottom_sellers, x='Sales Amount', y='Product Name', orientation='h',
                 color='Sales Amount', color_continuous_scale='Reds', text='Sales Amount')
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="Revenue (৳)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">🏷️ Revenue by Sales Channel</div>', unsafe_allow_html=True)
    channel_rev = filtered_df.groupby('Sales Channel')['Sales Amount'].sum().reset_index()
    fig = px.bar(channel_rev, x='Sales Channel', y='Sales Amount', 
                 color='Sales Channel', text='Sales Amount')
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Revenue (৳)")
    st.plotly_chart(fig, use_container_width=True)
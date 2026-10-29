import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Zone Analysis", page_icon="🗺️", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Sidebar Filters
with st.sidebar:
    st.markdown('<div class="filter-label">📅 MONTH FILTER</div>', unsafe_allow_html=True)
    months = df['Month Name'].dropna().unique()
    selected_months = st.multiselect("Select Months", options=months, default=months)
    
    st.markdown('<div class="filter-label">📦 PRODUCT CATEGORY</div>', unsafe_allow_html=True)
    categories = df['Product Category'].dropna().unique()
    selected_categories = st.multiselect("Select Categories", options=categories, default=categories)

# Apply Filters
filtered_df = df[
    (df['Month Name'].isin(selected_months)) & 
    (df['Product Category'].isin(selected_categories))
]

if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1>🗺️ Zone & Regional Analysis</h1>
    <p>Compare sales performance, profitability, and returns across different geographic zones</p>
</div>
""", unsafe_allow_html=True)

# Create a flag for returned transactions (assuming > 0 means returned)
filtered_df['Is_Returned'] = filtered_df['Sales Return'] > 0

# ============================================================================
# KPI METRICS (Top Performing Zone)
# ============================================================================
top_zone_rev = filtered_df.groupby('Sales Zone')['Sales Amount'].sum().idxmax()
top_zone_val = filtered_df.groupby('Sales Zone')['Sales Amount'].sum().max()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Top Zone by Revenue", top_zone_rev, f"৳{top_zone_val:,.0f}")
with col2:
    st.metric("Total Zones Active", filtered_df['Sales Zone'].nunique())
with col3:
    total_profit = filtered_df['Sales Amount'].sum() - filtered_df['Purchase Value'].sum()
    st.metric("Total Gross Profit", f"৳{total_profit:,.0f}")
with col4:
    avg_discount = filtered_df['Discount'].mean()
    st.metric("Avg Discount Given", f"৳{avg_discount:,.2f}")

st.markdown("---")

# ============================================================================
# CHARTS ROW 1: Revenue & Profitability by Zone
# ============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">💰 Revenue by Zone</div>', unsafe_allow_html=True)
    zone_rev = filtered_df.groupby('Sales Zone')['Sales Amount'].sum().sort_values(ascending=True).reset_index()
    
    fig = px.bar(
        zone_rev, x='Sales Amount', y='Sales Zone', orientation='h',
        color='Sales Amount', color_continuous_scale='Viridis', text='Sales Amount'
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="Revenue (৳)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📈 Profit Margin by Zone</div>', unsafe_allow_html=True)
    # Calculate profit margin per zone
    zone_profit = filtered_df.groupby('Sales Zone').agg({
        'Sales Amount': 'sum',
        'Purchase Value': 'sum'
    }).reset_index()
    
    # Avoid division by zero
    zone_profit['Gross Profit'] = zone_profit['Sales Amount'] - zone_profit['Purchase Value']
    zone_profit['Margin %'] = (zone_profit['Gross Profit'] / zone_profit['Sales Amount']) * 100
    zone_profit = zone_profit.sort_values('Margin %', ascending=False)
    
    fig = px.bar(
        zone_profit, x='Sales Zone', y='Margin %',
        color='Margin %', color_continuous_scale='Blues', text='Margin %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Gross Margin (%)")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# CHARTS ROW 2: Returns & Discounts
# ============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🔄 Return Rate by Zone</div>', unsafe_allow_html=True)
    # Calculate return rate per zone
    zone_returns = filtered_df.groupby('Sales Zone').agg({
        'Is_Returned': 'mean', # Percentage of orders returned
        'Sales Return': 'sum'  # Total items returned
    }).reset_index()
    
    zone_returns['Return Rate %'] = zone_returns['Is_Returned'] * 100
    zone_returns = zone_returns.sort_values('Return Rate %', ascending=False)
    
    fig = px.bar(
        zone_returns, x='Sales Zone', y='Return Rate %',
        color='Return Rate %', color_continuous_scale='Reds', text='Return Rate %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Return Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">🏷️ Average Discount by Zone</div>', unsafe_allow_html=True)
    zone_discount = filtered_df.groupby('Sales Zone')['Discount'].mean().sort_values(ascending=False).reset_index()
    
    fig = px.bar(
        zone_discount, x='Sales Zone', y='Discount',
        color='Discount', color_continuous_scale='Oranges', text='Discount'
    )
    fig.update_traces(texttemplate='৳%{text:,.2f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Avg Discount (৳)")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# ZONE VS CATEGORY HEATMAP
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">🔥 Zone vs Category Performance (Heatmap)</div>', unsafe_allow_html=True)

# Create a pivot table of Sales Amount by Zone and Category
pivot_df = filtered_df.pivot_table(
    index='Sales Zone', 
    columns='Product Category', 
    values='Sales Amount', 
    aggfunc='sum'
).fillna(0)

fig = px.imshow(
    pivot_df,
    labels=dict(x="Product Category", y="Sales Zone", color="Revenue (৳)"),
    x=pivot_df.columns,
    y=pivot_df.index,
    color_continuous_scale='YlGnBu',
    aspect="auto",
    text_auto='.2s' # Show abbreviated numbers (e.g., 1.2M)
)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TOP CUSTOMERS BY ZONE
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">👑 Top 5 Customers per Zone</div>', unsafe_allow_html=True)

# Get top 5 customers per zone
top_customers = filtered_df.groupby(['Sales Zone', 'Customer Name'])['Sales Amount'].sum().reset_index()
top_customers = top_customers.sort_values(['Sales Zone', 'Sales Amount'], ascending=[True, False])
top_customers = top_customers.groupby('Sales Zone').head(5)

# Display in columns
zones = top_customers['Sales Zone'].unique()
cols = st.columns(min(len(zones), 4)) # Max 4 columns

for idx, zone in enumerate(zones):
    with cols[idx % 4]:
        st.markdown(f"**📍 {zone}**")
        zone_top = top_customers[top_customers['Sales Zone'] == zone]
        
        # Format for display
        zone_top_display = zone_top[['Customer Name', 'Sales Amount']].copy()
        zone_top_display['Sales Amount'] = zone_top_display['Sales Amount'].apply(lambda x: f"৳{x:,.0f}")
        zone_top_display.columns = ['Customer', 'Revenue']
        
        st.dataframe(zone_top_display, hide_index=True, use_container_width=True)

# Footer
st.markdown("""
<div class="dashboard-footer">
    <p>Zone Analysis | Geographical sales performance and profitability</p>
</div>
""", unsafe_allow_html=True)
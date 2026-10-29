"""
Customer Analysis Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(
    page_title="Customer Analysis",
    page_icon="👥",
    layout="wide"
)

# Load CSS
load_css()

# Load data directly (using cache)
@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Since we removed the global session state filters to make it simpler,
# we will create a local filter for this page in the sidebar.
with st.sidebar:
    st.markdown('<div class="filter-label">📍 SALES ZONE</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Select Zones", options=zones, default=zones)
    
    st.markdown('<div class="filter-label">👥 CUSTOMER TYPE</div>', unsafe_allow_html=True)
    customer_types = df['Customer Type'].dropna().unique()
    selected_types = st.multiselect("Select Customer Types", options=customer_types, default=customer_types)

# Apply filters
filtered_df = df[
    (df['Sales Zone'].isin(selected_zones)) & 
    (df['Customer Type'].isin(selected_types))
]

if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# Main Header
st.markdown("""
<div class="main-header">
    <h1>👥 Customer Analytics</h1>
    <p>Deep dive into customer behavior, segmentation, and lifetime value</p>
</div>
""", unsafe_allow_html=True)

# Customer Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Customers", filtered_df['Customer Name'].nunique())

with col2:
    avg_spend = filtered_df.groupby('Customer Name')['Sales Amount'].sum().mean()
    st.metric("Avg Customer Value", f"৳{avg_spend:,.0f}")

with col3:
    # Using Invoice No to count orders per customer
    repeat_rate = (filtered_df.groupby('Customer Name')['Invoice No'].nunique() > 1).mean() * 100
    st.metric("Repeat Rate", f"{repeat_rate:.1f}%")

with col4:
    st.metric("Avg Orders", f"{filtered_df.groupby('Customer Name')['Invoice No'].nunique().mean():.1f}")

st.markdown("---")

# Customer Segmentation
st.markdown('<div class="section-header">📊 Customer Segmentation</div>', unsafe_allow_html=True)

# Group by new column names
customer_df = filtered_df.groupby('Customer Name').agg({
    'Sales Amount': 'sum',
    'Invoice No': 'nunique',
    'Sales Return': 'sum' # Assuming 'Sales Return' indicates a return
}).reset_index()

customer_df.columns = ['Customer', 'Total Spent', 'Order Count', 'Returns']

# Calculate Return Rate
customer_df['Return Rate'] = (customer_df['Returns'] / customer_df['Order Count']) * 100

# Segment customers
# Note: You may need to adjust the bins based on your actual currency values
customer_df['Segment'] = pd.cut(customer_df['Total Spent'], 
                                 bins=[0, 1000, 5000, 20000, 10000000],
                                 labels=['Low Value', 'Medium Value', 'High Value', 'VIP'])

segment_dist = customer_df['Segment'].value_counts().reset_index()
fig = px.pie(segment_dist, values='count', names='Segment', hole=0.3,
             title='Customer Segment Distribution',
             color_discrete_sequence=px.colors.qualitative.Set3)
st.plotly_chart(fig, use_container_width=True)

# Top Customers
st.markdown('<div class="section-header">🏆 Top 10 Customers</div>', unsafe_allow_html=True)
top_customers = customer_df.nlargest(10, 'Total Spent')[['Customer', 'Total Spent', 'Order Count', 'Return Rate']]

# Format the columns for display
top_customers['Total Spent'] = top_customers['Total Spent'].apply(lambda x: f"৳{x:,.0f}")
top_customers['Return Rate'] = top_customers['Return Rate'].round(1).astype(str) + '%'

st.dataframe(top_customers, use_container_width=True, hide_index=True)

st.markdown("""
<div class="dashboard-footer">
    <p>Customer Analysis | Data sourced directly from PostgreSQL</p>
</div>
""", unsafe_allow_html=True)
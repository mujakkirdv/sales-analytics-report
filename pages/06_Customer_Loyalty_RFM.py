import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Customer Loyalty (RFM)", page_icon="🎁", layout="wide")
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
df = df.dropna(subset=['Date', 'Customer Name']).reset_index(drop=True)
df['Sales Amount'] = pd.to_numeric(df['Sales Amount'], errors='coerce').fillna(0)
df['Invoice No'] = df['Invoice No'].astype(str)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🎁 Customer Loyalty & RFM Analysis</h1>
    <p>Segment customers by Recency, Frequency, and Monetary value to drive retention</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">⚙️ RFM SETTINGS</div>', unsafe_allow_html=True)
    
    # Define the reference date (Today or max date in dataset)
    max_date = df['Date'].max()
    reference_date = st.date_input(
        "Reference Date for 'Recency'", 
        value=max_date.date(),
        help="Recency is calculated as days since last purchase from this date."
    )
    reference_date = pd.to_datetime(reference_date)

    st.markdown('<div class="filter-label">📍 FILTERS</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Sales Zone", options=zones, default=zones)

# Apply filters
filtered = df[df['Sales Zone'].isin(selected_zones)].copy()

if len(filtered) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# ============================================================================
# CALCULATE RFM METRICS
# ============================================================================
# Group by Customer
rfm = filtered.groupby('Customer Name').agg({
    'Date': lambda x: (reference_date - x.max()).days,  # Recency
    'Invoice No': 'nunique',                            # Frequency
    'Sales Amount': 'sum'                               # Monetary
}).reset_index()

rfm.columns = ['Customer', 'Recency', 'Frequency', 'Monetary']

# ============================================================================
# RFM SCORING (1 to 5)
# ============================================================================
# Recency: Lower is better (5 = recent, 1 = long ago)
# We use qcut (quantile cut) to bin into 5 groups
# To handle duplicate edges, we use rank(method='first')
rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1]).astype(int)

# Frequency: Higher is better (5 = frequent)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)

# Monetary: Higher is better (5 = big spender)
rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)

# Combined RFM Score
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
rfm['RFM_Total'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']

# ============================================================================
# CUSTOMER SEGMENTATION
# ============================================================================
def segment_customer(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2 and m <= 2:
        return "New Customers"
    elif r >= 3 and f <= 2 and m <= 2:
        return "Promising"
    elif r <= 2 and f >= 4 and m >= 4:
        return "Can't Lose Them"
    elif r <= 3 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    else:
        return "Need Attention"

rfm['Segment'] = rfm.apply(segment_customer, axis=1)

# ============================================================================
# KPI METRICS
# ============================================================================
total_customers = len(rfm)
champions = len(rfm[rfm['Segment'] == 'Champions'])
at_risk = len(rfm[rfm['Segment'] == 'At Risk'])
lost = len(rfm[rfm['Segment'] == 'Lost'])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-value">{total_customers:,}</div>
        <div class="metric-label">Total Customers</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🏆</div>
        <div class="metric-value" style="color:#2ecc71;">{champions:,}</div>
        <div class="metric-label">Champions ({(champions/total_customers*100):.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">⚠️</div>
        <div class="metric-value" style="color:#f39c12;">{at_risk:,}</div>
        <div class="metric-label">At Risk ({(at_risk/total_customers*100):.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📉</div>
        <div class="metric-value" style="color:#e74c3c;">{lost:,}</div>
        <div class="metric-label">Lost ({(lost/total_customers*100):.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHARTS ROW 1: SEGMENT DISTRIBUTION
# ============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">📊 Customer Segment Distribution</div>', unsafe_allow_html=True)
    segment_counts = rfm['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    fig = px.pie(
        segment_counts, values='Count', names='Segment', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">💰 Revenue Contribution by Segment</div>', unsafe_allow_html=True)
    segment_revenue = rfm.groupby('Segment')['Monetary'].sum().reset_index()
    
    fig = px.bar(
        segment_revenue.sort_values('Monetary', ascending=True),
        x='Monetary', y='Segment', orientation='h',
        color='Monetary', color_continuous_scale='Viridis', text='Monetary'
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='Total Revenue (৳)', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# CHARTS ROW 2: RFM SCATTER PLOTS
# ============================================================================
st.markdown('<div class="section-header">🎯 Customer Distribution (RFM)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Recency vs Monetary
    fig = px.scatter(
        rfm, x='Recency', y='Monetary', color='Segment',
        size='Frequency', hover_name='Customer',
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'Recency': 'Days Since Last Purchase', 'Monetary': 'Total Spend (৳)'},
        title="Recency vs Monetary"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Frequency vs Monetary
    fig = px.scatter(
        rfm, x='Frequency', y='Monetary', color='Segment',
        size='Recency', hover_name='Customer',
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'Frequency': 'Number of Orders', 'Monetary': 'Total Spend (৳)'},
        title="Frequency vs Monetary"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# SEGMENT DETAILS (EXPANDERS)
# ============================================================================
st.markdown('<div class="section-header">📋 Segment Deep Dive</div>', unsafe_allow_html=True)

# Define segment descriptions
segment_desc = {
    "Champions": "Bought recently, buy often, and spend the most. Reward them!",
    "Loyal Customers": "Spend good money, buy often. Upsell higher value products.",
    "Can't Lose Them": "Big spenders but haven't purchased in a while. Win them back!",
    "At Risk": "Spent big money and purchased often but haven't bought recently.",
    "New Customers": "Bought most recently but not often. Provide onboarding support.",
    "Promising": "Recent shoppers but not frequent. Create brand awareness.",
    "Need Attention": "Recent and moderate frequency. Offer discounts to keep them engaged.",
    "Lost": "Lowest recency, frequency, and monetary scores. Don't spend too much on them."
}

for segment in ["Champions", "Loyal Customers", "At Risk", "Can't Lose Them", "New Customers", "Lost"]:
    seg_df = rfm[rfm['Segment'] == segment]
    if len(seg_df) > 0:
        with st.expander(f"**{segment}** — {len(seg_df):,} Customers (৳{seg_df['Monetary'].sum():,.0f} Revenue)"):
            st.info(segment_desc.get(segment, ""))
            
            # Show top 10 customers in this segment
            top_in_segment = seg_df.nlargest(10, 'Monetary')[['Customer', 'Recency', 'Frequency', 'Monetary']].copy()
            top_in_segment.columns = ['Customer', 'Recency (Days)', 'Orders', 'Total Spend (৳)']
            top_in_segment['Total Spend (৳)'] = top_in_segment['Total Spend (৳)'].apply(lambda x: f"৳{x:,.0f}")
            
            st.dataframe(top_in_segment, hide_index=True, use_container_width=True)

# ============================================================================
# FULL CUSTOMER TABLE & EXPORT
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📋 Full Customer RFM Table</div>', unsafe_allow_html=True)

# Prepare the export dataframe
export_df = rfm.copy()
export_df = export_df[['Customer', 'Segment', 'Recency', 'Frequency', 'Monetary', 'R_Score', 'F_Score', 'M_Score', 'RFM_Score']]
export_df = export_df.sort_values('Monetary', ascending=False)

# Format for display
display_df = export_df.copy()
display_df['Monetary'] = display_df['Monetary'].apply(lambda x: f"৳{x:,.0f}")

st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

# Download CSV
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Full RFM Segmentation (CSV)",
    data=csv,
    file_name="customer_rfm_segmentation.csv",
    mime="text/csv",
    type="primary"
)

st.markdown("""
<div class="dashboard-footer">
    <p>Customer Loyalty RFM | Segment customers to drive retention and revenue</p>
</div>
""", unsafe_allow_html=True)
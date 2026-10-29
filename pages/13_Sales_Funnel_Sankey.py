import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Sales Funnel & Flow", page_icon="🔄", layout="wide")
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
df = df.dropna(subset=['Date']).reset_index(drop=True)
df['Sales Amount'] = pd.to_numeric(df['Sales Amount'], errors='coerce').fillna(0)
df['Purchase Value'] = pd.to_numeric(df['Purchase Value'], errors='coerce').fillna(0)
df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🔄 Sales Funnel & Revenue Flow</h1>
    <p>Visualize how revenue flows through your business — from channel to zone to customer</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">⚙️ FLOW CONFIGURATION</div>', unsafe_allow_html=True)
    
    # Choose flow path
    flow_option = st.selectbox(
        "Sankey Flow Path",
        [
            "Channel → Zone → Customer Type",
            "Channel → Category → Customer Type",
            "Zone → Product Category → Sales by",
            "Customer Type → Payment Method → Sales Channel"
        ]
    )
    
    metric_choice = st.radio(
        "Sankey Metric",
        ["Revenue (৳)", "Gross Profit (৳)", "Order Count"],
        horizontal=True
    )
    
    st.markdown('<div class="filter-label">📅 DATE RANGE</div>', unsafe_allow_html=True)
    
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.date_input(
        "Select Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    st.markdown('<div class="filter-label">📍 FILTERS</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Sales Zone", options=zones, default=zones)
    
    channels = df['Sales Channel'].dropna().unique()
    selected_channels = st.multiselect("Sales Channel", options=channels, default=channels)

# Apply filters
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    (df['Date'].dt.date >= start_date) &
    (df['Date'].dt.date <= end_date) &
    (df['Sales Zone'].isin(selected_zones)) &
    (df['Sales Channel'].isin(selected_channels))
].copy()

if len(filtered) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# ============================================================================
# KPI METRICS
# ============================================================================
total_revenue = filtered['Sales Amount'].sum()
total_profit = filtered['Gross Profit'].sum()
total_orders = filtered['Invoice No'].nunique()
total_customers = filtered['Customer Name'].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💰</div>
        <div class="metric-value">৳{total_revenue:,.0f}</div>
        <div class="metric-label">Total Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value">৳{total_profit:,.0f}</div>
        <div class="metric-label">Gross Profit</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🧾</div>
        <div class="metric-value">{total_orders:,}</div>
        <div class="metric-label">Total Orders</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-value">{total_customers:,}</div>
        <div class="metric-label">Unique Customers</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SANKEY DIAGRAM
# ============================================================================
st.markdown('<div class="section-header">🌊 Revenue Flow (Sankey Diagram)</div>', unsafe_allow_html=True)
st.caption(f"Flow: **{flow_option}** | Metric: **{metric_choice}**")

# Parse the selected flow into 3 columns
source_col, middle_col, target_col = [c.strip() for c in flow_option.split("→")]

# Map display names to actual column names
column_map = {
    "Channel": "Sales Channel",
    "Zone": "Sales Zone",
    "Customer Type": "Customer Type",
    "Category": "Product Category",
    "Sales by": "Sales by",
    "Payment Method": "Payment Method",
    "Product Category": "Product Category",
    "Sales Channel": "Sales Channel",
    "Sales Zone": "Sales Zone",
}

src_col = column_map.get(source_col, source_col)
mid_col = column_map.get(middle_col, middle_col)
tgt_col = column_map.get(target_col, target_col)

# Select metric column
metric_map = {
    "Revenue (৳)": "Sales Amount",
    "Gross Profit (৳)": "Gross Profit",
    "Order Count": "Invoice No"
}
metric_col = metric_map[metric_choice]
is_count_metric = metric_choice == "Order Count"

# Build Sankey from 3-level flow
# Stage 1: src → mid
stage1 = filtered.groupby([src_col, mid_col]).agg(
    value=(metric_col, 'nunique' if is_count_metric else 'sum')
).reset_index()

# Stage 2: mid → tgt
stage2 = filtered.groupby([mid_col, tgt_col]).agg(
    value=(metric_col, 'nunique' if is_count_metric else 'sum')
).reset_index()

# Collect all unique nodes in order
all_src = sorted(stage1[src_col].dropna().unique().tolist())
all_mid = sorted(stage1[mid_col].dropna().unique().tolist())
all_tgt = sorted(stage2[tgt_col].dropna().unique().tolist())

# Build node list (prefix with layer to avoid name collisions)
node_labels = (
    [f"{s} ({source_col})" for s in all_src] +
    [f"{m} ({middle_col})" for m in all_mid] +
    [f"{t} ({target_col})" for t in all_tgt]
)

# Node color palette per layer
layer1_colors = px.colors.qualitative.Set2
layer2_colors = px.colors.qualitative.Pastel
layer3_colors = px.colors.qualitative.Set3

node_colors = []
for i in range(len(all_src)):
    node_colors.append(layer1_colors[i % len(layer1_colors)])
for i in range(len(all_mid)):
    node_colors.append(layer2_colors[i % len(layer2_colors)])
for i in range(len(all_tgt)):
    node_colors.append(layer3_colors[i % len(layer3_colors)])

# Node index lookup
node_index = {label: idx for idx, label in enumerate(node_labels)}

# Build links
sources, targets, values, link_colors = [], [], [], []

# Stage 1 links
for _, row in stage1.iterrows():
    if pd.notna(row[src_col]) and pd.notna(row[mid_col]):
        src_label = f"{row[src_col]} ({source_col})"
        mid_label = f"{row[mid_col]} ({middle_col})"
        sources.append(node_index[src_label])
        targets.append(node_index[mid_label])
        values.append(row['value'])
        link_colors.append("rgba(102, 126, 234, 0.4)")

# Stage 2 links
for _, row in stage2.iterrows():
    if pd.notna(row[mid_col]) and pd.notna(row[tgt_col]):
        mid_label = f"{row[mid_col]} ({middle_col})"
        tgt_label = f"{row[tgt_col]} ({target_col})"
        sources.append(node_index[mid_label])
        targets.append(node_index[tgt_label])
        values.append(row['value'])
        link_colors.append("rgba(118, 75, 162, 0.4)")

if len(values) == 0:
    st.info("No flow data available for the selected filters.")
else:
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors,
            hovertemplate='%{label}<br>Total: %{value:,.0f}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate='%{source.label} → %{target.label}<br>Value: %{value:,.0f}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        height=600,
        font=dict(size=11),
        title_text=f"<b>{metric_choice}</b> Flow: {source_col} → {middle_col} → {target_col}",
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# SALES FUNNEL (Transaction Pipeline)
# ============================================================================
st.markdown('<div class="section-header">🔻 Sales Funnel — Order Conversion</div>', unsafe_allow_html=True)
st.caption("How many orders progress from initial invoice through successful sale to full payment.")

# Funnel stages based on your dataset
# Stage 1: Total Invoices Created
# Stage 2: Invoices with Sales Amount > 0 (real sales)
# Stage 3: Invoices with no market due (paid)
# Stage 4: Invoices with no returns (fully retained)
# Stage 5: Invoices with no returns AND no due (fully clean)

invoice_df = filtered.groupby('Invoice No').agg({
    'Sales Amount': 'sum',
    'Invoice Value': 'sum',
    'Sales Return': 'sum',
    'Market Due' if 'Market Due' in filtered.columns else 'Sales Amount': 'sum'
}).reset_index()

# Calculate stages
stage1_total = invoice_df['Invoice No'].nunique()

stage2_sold = invoice_df[invoice_df['Sales Amount'] > 0]['Invoice No'].nunique()

stage3_paid = invoice_df[
    (invoice_df['Sales Amount'] > 0) &
    (invoice_df['Invoice Value'] - invoice_df['Sales Amount'] <= 0)
]['Invoice No'].nunique()

stage4_no_return = invoice_df[
    (invoice_df['Sales Amount'] > 0) &
    (invoice_df['Sales Return'] == 0)
]['Invoice No'].nunique()

stage5_clean = invoice_df[
    (invoice_df['Sales Amount'] > 0) &
    (invoice_df['Sales Return'] == 0) &
    (invoice_df['Invoice Value'] - invoice_df['Sales Amount'] <= 0)
]['Invoice No'].nunique()

funnel_stages = [
    ("📋 Total Invoices", stage1_total),
    ("💰 Invoices with Sales", stage2_sold),
    ("✅ Fully Paid", stage3_paid),
    ("🔄 No Returns", stage4_no_return),
    ("⭐ Clean (Paid + No Returns)", stage5_clean),
]

funnel_df = pd.DataFrame(funnel_stages, columns=['Stage', 'Orders'])

fig = go.Figure(go.Funnel(
    y=funnel_df['Stage'],
    x=funnel_df['Orders'],
    textinfo="value+percent initial",
    marker=dict(color=['#667eea', '#764ba2', '#2ecc71', '#f39c12', '#e74c3c']),
    connector=dict(line=dict(color="royalblue", width=1))
))

fig.update_layout(
    height=450,
    title_text="<b>Order Funnel</b>",
    title_x=0.5,
    font=dict(size=12)
)
st.plotly_chart(fig, use_container_width=True)

st.caption("Shows how many invoices survive from creation → sale → payment → no returns → complete clean transactions.")

st.markdown("---")

# ============================================================================
# CHANNEL DEEP DIVE
# ============================================================================
st.markdown('<div class="section-header">📊 Channel Performance Breakdown</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Revenue by channel
    channel_rev = filtered.groupby('Sales Channel').agg({
        'Sales Amount': 'sum',
        'Invoice No': 'nunique'
    }).reset_index()
    
    fig = px.bar(
        channel_rev.sort_values('Sales Amount', ascending=False),
        x='Sales Channel', y='Sales Amount',
        color='Sales Amount', color_continuous_scale='Viridis',
        text='Sales Amount'
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='', yaxis_title='Revenue (৳)',
                      title="Revenue by Channel")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Average order value by channel
    channel_aov = filtered.groupby('Sales Channel').agg({
        'Sales Amount': 'sum',
        'Invoice No': 'nunique'
    }).reset_index()
    channel_aov['AOV'] = channel_aov['Sales Amount'] / channel_aov['Invoice No']
    
    fig = px.bar(
        channel_aov.sort_values('AOV', ascending=False),
        x='Sales Channel', y='AOV',
        color='AOV', color_continuous_scale='Plasma',
        text='AOV'
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='', yaxis_title='Avg Order Value (৳)',
                      title="Avg Order Value by Channel")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# FLOW DOWNLOAD
# ============================================================================
st.markdown('<div class="section-header">📥 Download Flow Data</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if len(stage1) > 0:
        csv1 = stage1.to_csv(index=False).encode('utf-8')
        st.download_button(
            f"📄 Download {source_col} → {middle_col} Data",
            data=csv1,
            file_name=f"flow_{src_col}_{mid_col}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col2:
    if len(stage2) > 0:
        csv2 = stage2.to_csv(index=False).encode('utf-8')
        st.download_button(
            f"📄 Download {middle_col} → {target_col} Data",
            data=csv2,
            file_name=f"flow_{mid_col}_{tgt_col}.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("""
<div class="dashboard-footer">
    <p>Sales Funnel & Sankey | Visualize revenue flow across dimensions</p>
</div>
""", unsafe_allow_html=True)
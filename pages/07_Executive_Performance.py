import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Executive Dashboard", page_icon="💼", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Sidebar Filters
with st.sidebar:
    st.markdown('<div class="filter-label">📅 MONTH</div>', unsafe_allow_html=True)
    months = df['Month Name'].dropna().unique()
    selected_months = st.multiselect("Select Months", options=months, default=months)
    
    st.markdown('<div class="filter-label">📍 SALES ZONE</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Select Zones", options=zones, default=zones)
    
    st.markdown('<div class="filter-label">🛒 SALES CHANNEL</div>', unsafe_allow_html=True)
    channels = df['Sales Channel'].dropna().unique()
    selected_channels = st.multiselect("Select Channels", options=channels, default=channels)

# Apply Filters
filtered_df = df[
    (df['Month Name'].isin(selected_months)) & 
    (df['Sales Zone'].isin(selected_zones)) &
    (df['Sales Channel'].isin(selected_channels))
]

if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>💼 Executive Dashboard</h1>
    <p>Strategic overview: Salesperson Performance, Market Dues, and Profitability</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FINANCIAL CALCULATIONS
# ============================================================================
# Gross Profit = Sales Amount - Purchase Value
filtered_df['Gross Profit'] = filtered_df['Sales Amount'] - filtered_df['Purchase Value']
# Market Due = Invoice Value - Sales Amount (Assuming Invoice Value is the total bill and Sales Amount is the collected amount)
filtered_df['Market Due'] = filtered_df['Invoice Value'] - filtered_df['Sales Amount']

total_revenue = filtered_df['Sales Amount'].sum()
total_profit = filtered_df['Gross Profit'].sum()
total_due = filtered_df['Market Due'].sum()
total_returns = filtered_df['Sales Return'].sum()

# ============================================================================
# KPI METRICS
# ============================================================================
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
    margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value">৳{total_profit:,.0f}</div>
        <div class="metric-label">Gross Profit ({margin:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">⚠️</div>
        <div class="metric-value">৳{total_due:,.0f}</div>
        <div class="metric-label">Total Market Due</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🔄</div>
        <div class="metric-value">৳{total_returns:,.0f}</div>
        <div class="metric-label">Total Returns</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# INDIVIDUAL PERFORMANCE (SALESPERSON)
# ============================================================================
st.markdown('<div class="section-header">🏅 Individual Salesperson Performance</div>', unsafe_allow_html=True)

# Group by Salesperson ('Sales by')
salesperson_perf = filtered_df.groupby('Sales by').agg({
    'Sales Amount': 'sum',
    'Gross Profit': 'sum',
    'Invoice No': 'nunique',
    'Sales Return': 'sum'
}).reset_index()

salesperson_perf['Margin %'] = (salesperson_perf['Gross Profit'] / salesperson_perf['Sales Amount']) * 100
salesperson_perf = salesperson_perf.sort_values('Sales Amount', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    # Top 10 Salespersons by Revenue
    top_salespersons = salesperson_perf.head(10).sort_values('Sales Amount', ascending=True)
    fig = px.bar(
        top_salespersons, x='Sales Amount', y='Sales by', orientation='h',
        color='Sales Amount', color_continuous_scale='Teal', text='Sales Amount',
        title="Top 10 Salespersons by Revenue"
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=450, showlegend=False, xaxis_title='Revenue (৳)', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Performance Leaderboard**")
    # Prepare table for display
    leaderboard = salesperson_perf[['Sales by', 'Sales Amount', 'Margin %']].head(10).copy()
    leaderboard['Sales Amount'] = leaderboard['Sales Amount'].apply(lambda x: f"৳{x:,.0f}")
    leaderboard['Margin %'] = leaderboard['Margin %'].round(1).astype(str) + '%'
    st.dataframe(leaderboard, hide_index=True, use_container_width=True)

# ============================================================================
# MARKET DUE ANALYSIS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">💸 Market Due Analysis (Outstanding Payments)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Market Due by Salesperson
    due_by_sales = filtered_df.groupby('Sales by')['Market Due'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(
        due_by_sales, x='Market Due', y='Sales by', orientation='h',
        color='Market Due', color_continuous_scale='Reds', text='Market Due',
        title="Top 10 Salespersons with Highest Market Due"
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='Due Amount (৳)', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Market Due by Customer Type
    due_by_customer = filtered_df.groupby('Customer Type')['Market Due'].sum().reset_index()
    fig = px.pie(
        due_by_customer, values='Market Due', names='Customer Type', hole=0.4,
        color_discrete_sequence=px.colors.sequential.Reds,
        title="Market Due Breakdown by Customer Type"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PROFITABILITY VS DISCOUNT
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📉 Profitability vs Discount Impact</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Revenue vs Cost by Sales Channel
    channel_perf = filtered_df.groupby('Sales Channel').agg({
        'Sales Amount': 'sum',
        'Purchase Value': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=channel_perf['Sales Channel'], y=channel_perf['Sales Amount'], name='Revenue', marker_color='#667eea'))
    fig.add_trace(go.Bar(x=channel_perf['Sales Channel'], y=channel_perf['Purchase Value'], name='Cost', marker_color='#e74c3c'))
    fig.update_layout(
        barmode='group', height=400,
        title="Revenue vs Cost by Channel",
        xaxis_title="", yaxis_title="Amount (৳)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Discount vs Profit Margin Scatter
    fig = px.scatter(
        filtered_df, x='Discount', y='Gross Profit',
        color='Sales Channel', size='Sales Amount', hover_name='Product Name',
        title="Discount vs Gross Profit (Bubble Size = Sales)",
        labels={'Discount': 'Discount (৳)', 'Gross Profit': 'Profit (৳)'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAYMENT METHOD & BANK ANALYSIS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">🏦 Payment & Banking Overview</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Revenue by Payment Method
    payment_perf = filtered_df.groupby('Payment Method')['Sales Amount'].sum().reset_index()
    fig = px.pie(
        payment_perf, values='Sales Amount', names='Payment Method', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Revenue by Payment Method"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Market Due by Bank
    bank_due = filtered_df.dropna(subset=['Bank Name'])
    bank_due = bank_due[bank_due['Bank Name'].astype(str).str.strip() != '']
    
    if len(bank_due) > 0:
        bank_due_grouped = bank_due.groupby('Bank Name')['Market Due'].sum().nlargest(8).reset_index()
        fig = px.bar(
            bank_due_grouped, x='Bank Name', y='Market Due',
            color='Market Due', color_continuous_scale='Purples', text='Market Due',
            title="Market Due by Bank"
        )
        fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Due (৳)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No bank data available in this selection.")

# ============================================================================
# STRATEGIC INSIGHTS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">💡 Strategic Executive Insights</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    top_salesperson = salesperson_perf.iloc[0]['Sales by'] if not salesperson_perf.empty else "N/A"
    top_amount = salesperson_perf.iloc[0]['Sales Amount'] if not salesperson_perf.empty else 0
    st.markdown(f"""
    <div class="insight-card">
        <h4>🏆 Star Performer</h4>
        <p><strong>{top_salesperson}</strong> is your top salesperson, generating <strong>৳{top_amount:,.0f}</strong> in revenue.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    due_ratio = (total_due / filtered_df['Invoice Value'].sum() * 100) if filtered_df['Invoice Value'].sum() > 0 else 0
    st.markdown(f"""
    <div class="insight-card">
        <h4>⚠️ Collection Risk</h4>
        <p><strong>{due_ratio:.1f}%</strong> of total invoice value is unpaid (Market Due). Follow up on collections.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if not channel_perf.empty:
        best_channel = channel_perf.loc[(channel_perf['Sales Amount'] - channel_perf['Purchase Value']).idxmax()]
        channel_profit = best_channel['Sales Amount'] - best_channel['Purchase Value']
        st.markdown(f"""
        <div class="insight-card">
            <h4>🚀 Best Channel</h4>
            <p><strong>{best_channel['Sales Channel']}</strong> is the most profitable channel with <strong>৳{channel_profit:,.0f}</strong> gross profit.</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="dashboard-footer">
    <p>Executive Dashboard | Individual Performance, Market Dues & Strategic Insights</p>
</div>
""", unsafe_allow_html=True)
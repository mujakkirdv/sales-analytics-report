import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Executive Portfolio", page_icon="🏅", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Create derived columns for analysis
df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']
df['Market Due'] = df['Invoice Value'] - df['Sales Amount']
df['Is_Returned'] = df['Sales Return'] > 0

# Header
st.markdown("""
<div class="main-header">
    <h1>🏅 Executive Portfolio</h1>
    <p>360° Performance Profile for Individual Sales Executives</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# EXECUTIVE SELECTION
# ============================================================================
st.markdown('<div class="section-header">🔍 Select Executive</div>', unsafe_allow_html=True)

# Get list of unique executives (excluding blanks)
exec_list = sorted(df['Sales by'].dropna().unique())
selected_exec = st.selectbox("Search or Select a Sales Executive", options=exec_list)

if not selected_exec:
    st.warning("Please select an executive to view their portfolio.")
    st.stop()

# Filter data for the selected executive
exec_df = df[df['Sales by'] == selected_exec].copy()

# Ensure 'Date' is a datetime object for time series
if 'Date' in exec_df.columns:
    try:
        exec_df['Date'] = pd.to_datetime(exec_df['Date'], errors='coerce')
    except:
        pass

# ============================================================================
# EXECUTIVE PROFILE & KPIs
# ============================================================================
# Basic Profile Info
primary_zone = exec_df['Sales Zone'].mode()[0] if not exec_df.empty else "Unknown"
primary_channel = exec_df['Sales Channel'].mode()[0] if not exec_df.empty else "Unknown"
total_customers = exec_df['Customer Name'].nunique()

st.markdown(f"""
<div style="background: white; padding: 1.5rem; border-radius: 1rem; border-left: 5px solid #2ecc71; margin-bottom: 2rem;">
    <h3 style="margin:0; color:#2c3e50;">👤 {selected_exec}</h3>
    <p style="margin: 0.5rem 0 0 0; color: #7f8c8d;">
        <strong>Primary Zone:</strong> {primary_zone} | 
        <strong>Primary Channel:</strong> {primary_channel} | 
        <strong>Total Customers Handled:</strong> {total_customers}
    </p>
</div>
""", unsafe_allow_html=True)

# KPI Metrics
total_sales = exec_df['Sales Amount'].sum()
total_profit = exec_df['Gross Profit'].sum()
total_due = exec_df['Market Due'].sum()
total_returns = exec_df['Sales Return'].sum()
total_invoices = exec_df['Invoice No'].nunique()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Revenue", f"৳{total_sales:,.0f}")
with col2:
    st.metric("Gross Profit", f"৳{total_profit:,.0f}")
with col3:
    st.metric("Market Due", f"৳{total_due:,.0f}")
with col4:
    st.metric("Returns Value", f"৳{total_returns:,.0f}")
with col5:
    st.metric("Total Invoices", f"{total_invoices:,}")

st.markdown("---")

# ============================================================================
# PERFORMANCE TIME SERIES (SALES VS PROFIT)
# ============================================================================
st.markdown('<div class="section-header">📈 Sales & Profit Trend</div>', unsafe_allow_html=True)

if 'Date' in exec_df.columns and exec_df['Date'].notna().any():
    # Aggregate by Date
    time_series = exec_df.groupby(exec_df['Date'].dt.date).agg({
        'Sales Amount': 'sum',
        'Gross Profit': 'sum'
    }).reset_index()
    time_series.rename(columns={'Date': 'Transaction Date'}, inplace=True)
    
    # Plot Line Chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_series['Transaction Date'], y=time_series['Sales Amount'],
        mode='lines+markers', name='Sales Amount',
        line=dict(color='#667eea', width=3), marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=time_series['Transaction Date'], y=time_series['Gross Profit'],
        mode='lines+markers', name='Gross Profit',
        line=dict(color='#2ecc71', width=2, dash='dot'), marker=dict(size=6)
    ))
    
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Amount (৳)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Time series data not available for this executive.")

# ============================================================================
# TOP CUSTOMERS & CATEGORY ANALYSIS
# ============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🏆 Top Customers Managed</div>', unsafe_allow_html=True)
    top_customers = exec_df.groupby('Customer Name')['Sales Amount'].sum().sort_values(ascending=False).head(7).reset_index()
    fig = px.bar(
        top_customers, x='Sales Amount', y='Customer Name', orientation='h',
        color='Sales Amount', color_continuous_scale='Blues', text='Sales Amount'
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=350, showlegend=False, xaxis_title='Revenue (৳)', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📦 Revenue by Product Category</div>', unsafe_allow_html=True)
    cat_dist = exec_df.groupby('Product Category')['Sales Amount'].sum().reset_index()
    fig = px.pie(
        cat_dist, values='Sales Amount', names='Product Category', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MARKET DUE ANALYSIS FOR THIS EXECUTIVE
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">💸 Outstanding Market Due Analysis</div>', unsafe_allow_html=True)

# Filter only transactions with due amounts
due_df = exec_df[exec_df['Market Due'] > 0]

if len(due_df) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        # Top customers with dues
        due_customers = due_df.groupby('Customer Name')['Market Due'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(
            due_customers, x='Market Due', y='Customer Name', orientation='h',
            color='Market Due', color_continuous_scale='Reds', text='Market Due'
        )
        fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title='Due Amount (৳)', yaxis_title='', title="Top Customers with Dues")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Due by Payment Method
        due_payment = due_df.groupby('Payment Method')['Market Due'].sum().reset_index()
        fig = px.pie(
            due_payment, values='Market Due', names='Payment Method', hole=0.4,
            color_discrete_sequence=px.colors.sequential.Reds, title="Dues by Payment Method"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.success("🎉 Great news! This executive has no outstanding market dues.")

# ============================================================================
# DETAILED TRANSACTION HISTORY & DOWNLOAD
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📋 Executive Transaction History</div>', unsafe_allow_html=True)

# Select columns to display
display_cols = [
    'Date', 'Invoice No', 'Customer Name', 'Product Name', 
    'Sales Amount', 'Gross Profit', 'Discount', 'Market Due', 'Payment Method'
]
available_cols = [col for col in display_cols if col in exec_df.columns]
history_df = exec_df[available_cols].copy()

# Format Date
if 'Date' in history_df.columns:
    history_df['Date'] = pd.to_datetime(history_df['Date']).dt.date

# Format Currency Columns
for col in ['Sales Amount', 'Gross Profit', 'Discount', 'Market Due']:
    if col in history_df.columns:
        history_df[col] = history_df[col].apply(lambda x: f"৳{x:,.2f}" if pd.notna(x) else "৳0.00")

st.dataframe(history_df, use_container_width=True, hide_index=True)

# Download Report Button
st.markdown("### 📥 Download Executive Report")
csv = exec_df[available_cols].to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"Download {selected_exec} Portfolio (CSV)",
    data=csv,
    file_name=f"{selected_exec.replace(' ', '_')}_portfolio.csv",
    mime="text/csv",
    type="primary"
)

st.markdown("""
<div class="dashboard-footer">
    <p>Executive 360 Portfolio | Individual Sales Performance & Market Due Analysis</p>
</div>
""", unsafe_allow_html=True)
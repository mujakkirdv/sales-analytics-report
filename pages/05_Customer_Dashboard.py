import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Customer Dashboard", page_icon="👤", layout="wide")
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
    <h1>👤 Customer 360 Dashboard</h1>
    <p>Individual Customer Portfolio: History, Trends, Profitability, and Dues</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CUSTOMER SELECTION
# ============================================================================
st.markdown('<div class="section-header">🔍 Select Customer</div>', unsafe_allow_html=True)

# Get list of unique customers (exclude blanks)
customer_list = sorted(df['Customer Name'].dropna().unique())
selected_customer = st.selectbox("Search or Select a Customer", options=customer_list)

if not selected_customer:
    st.warning("Please select a customer to view their portfolio.")
    st.stop()

# Filter data for the selected customer
cust_df = df[df['Customer Name'] == selected_customer].copy()

# Ensure 'Date' is a datetime object for time series
if 'Date' in cust_df.columns:
    try:
        cust_df['Date'] = pd.to_datetime(cust_df['Date'], errors='coerce')
    except:
        pass

# ============================================================================
# CUSTOMER PROFILE & KPIs
# ============================================================================
# Basic Profile Info
cust_type = cust_df['Customer Type'].iloc[0] if not cust_df.empty else "Unknown"
cust_zone = cust_df['Sales Zone'].mode()[0] if not cust_df.empty else "Unknown"
first_purchase = cust_df['Date'].min().strftime('%Y-%m-%d') if not cust_df.empty and pd.notna(cust_df['Date'].min()) else "N/A"
last_purchase = cust_df['Date'].max().strftime('%Y-%m-%d') if not cust_df.empty and pd.notna(cust_df['Date'].max()) else "N/A"

st.markdown(f"""
<div style="background: white; padding: 1.5rem; border-radius: 1rem; border-left: 5px solid #667eea; margin-bottom: 2rem;">
    <h3 style="margin:0; color:#2c3e50;">{selected_customer}</h3>
    <p style="margin: 0.5rem 0 0 0; color: #7f8c8d;">
        <strong>Type:</strong> {cust_type} | 
        <strong>Primary Zone:</strong> {cust_zone} | 
        <strong>First Purchase:</strong> {first_purchase} | 
        <strong>Last Purchase:</strong> {last_purchase}
    </p>
</div>
""", unsafe_allow_html=True)

# KPI Metrics
total_sales = cust_df['Sales Amount'].sum()
total_profit = cust_df['Gross Profit'].sum()
total_due = cust_df['Market Due'].sum()
total_returns = cust_df['Sales Return'].sum()
total_invoices = cust_df['Invoice No'].nunique()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Revenue", f"৳{total_sales:,.0f}")
with col2:
    st.metric("Total Profit", f"৳{total_profit:,.0f}")
with col3:
    st.metric("Market Due", f"৳{total_due:,.0f}")
with col4:
    st.metric("Returns Value", f"৳{total_returns:,.0f}")
with col5:
    st.metric("Total Orders", f"{total_invoices:,}")

st.markdown("---")

# ============================================================================
# TIME SERIES ANALYSIS
# ============================================================================
st.markdown('<div class="section-header">📈 Purchase Trend Over Time</div>', unsafe_allow_html=True)

if 'Date' in cust_df.columns and cust_df['Date'].notna().any():
    # Aggregate by Date
    time_series = cust_df.groupby(cust_df['Date'].dt.date).agg({
        'Sales Amount': 'sum',
        'Gross Profit': 'sum',
        'Invoice No': 'nunique'
    }).reset_index()
    time_series.rename(columns={'Date': 'Transaction Date', 'Invoice No': 'Orders'}, inplace=True)
    
    # Plot Line Chart
    fig = go.Figure()
    
    # Sales Line
    fig.add_trace(go.Scatter(
        x=time_series['Transaction Date'], y=time_series['Sales Amount'],
        mode='lines+markers', name='Sales Amount',
        line=dict(color='#667eea', width=3), marker=dict(size=8)
    ))
    
    # Profit Line
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
    st.info("Time series data not available for this customer.")

# ============================================================================
# PRODUCT & CATEGORY PREFERENCES
# ============================================================================
st.markdown('<div class="section-header">🛍️ Customer Product Preferences</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top Purchased Products
    top_products = cust_df.groupby('Product Name')['Sales Amount'].sum().sort_values(ascending=False).head(7).reset_index()
    fig = px.bar(
        top_products, x='Sales Amount', y='Product Name', orientation='h',
        color='Sales Amount', color_continuous_scale='Blues', text='Sales Amount'
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=350, showlegend=False, xaxis_title='Revenue (৳)', yaxis_title='', title="Top Products Bought")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Category Distribution
    cat_dist = cust_df.groupby('Product Category')['Sales Amount'].sum().reset_index()
    fig = px.pie(
        cat_dist, values='Sales Amount', names='Product Category', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="Spending by Category"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TRANSACTION HISTORY & DOWNLOAD
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📋 Detailed Transaction History</div>', unsafe_allow_html=True)

# Select columns to display
display_cols = [
    'Date', 'Invoice No', 'Invoice type', 'Product Name', 
    'Product Category', 'Sales Channel', 'Sales Amount', 
    'Gross Profit', 'Discount', 'Market Due', 'Sales Return', 'Payment Method'
]

available_cols = [col for col in display_cols if col in cust_df.columns]
history_df = cust_df[available_cols].copy()

# Format Date
if 'Date' in history_df.columns:
    history_df['Date'] = pd.to_datetime(history_df['Date']).dt.date

# Format Currency Columns
for col in ['Sales Amount', 'Gross Profit', 'Discount', 'Market Due', 'Sales Return']:
    if col in history_df.columns:
        history_df[col] = history_df[col].apply(lambda x: f"৳{x:,.2f}" if pd.notna(x) else "৳0.00")

st.dataframe(history_df, use_container_width=True, hide_index=True)

# Download Report Button
st.markdown("### 📥 Download Report")
csv = cust_df[available_cols].to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"Download {selected_customer} Portfolio (CSV)",
    data=csv,
    file_name=f"{selected_customer.replace(' ', '_')}_portfolio.csv",
    mime="text/csv",
    type="primary"
)

st.markdown("""
<div class="dashboard-footer">
    <p>Customer 360 Portfolio | Personalized Analytics & Transaction History</p>
</div>
""", unsafe_allow_html=True)
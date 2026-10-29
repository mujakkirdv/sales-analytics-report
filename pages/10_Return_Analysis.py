import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Return Analysis", page_icon="🔄", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Header
st.markdown("""
<div class="main-header">
    <h1>🔄 Return & Refund Analysis</h1>
    <p>Monitor return rates, refunded amounts, and problematic products</p>
</div>
""", unsafe_allow_html=True)

# Calculate overall return metrics
total_revenue = df['Sales Amount'].sum()
total_returns = df['Sales Return'].sum()
total_credited = df['Credited Amount'].sum()

# Create a flag for returned transactions (assuming > 0 means returned)
df['Is_Returned'] = df['Sales Return'] > 0
total_returned_orders = df['Is_Returned'].sum()
total_orders = len(df)
return_rate = (total_returned_orders / total_orders) * 100 if total_orders > 0 else 0

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Return Rate", f"{return_rate:.2f}%")
with col2:
    st.metric("Total Returned Orders", f"{total_returned_orders:,}")
with col3:
    st.metric("Total Refunded Value", f"৳{total_credited:,.0f}")
with col4:
    st.metric("Return Value Impact", f"{((total_credited / total_revenue) * 100):.1f}%" if total_revenue > 0 else "0%")

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">📦 Most Returned Products</div>', unsafe_allow_html=True)
    # Filter only returned items and group by product
    returned_df = df[df['Is_Returned']]
    if len(returned_df) > 0:
        top_returned = returned_df.groupby('Product Name')['Sales Return'].count().nlargest(10).reset_index()
        fig = px.bar(top_returned, x='Sales Return', y='Product Name', orientation='h',
                     color='Sales Return', color_continuous_scale='Reds', text='Sales Return')
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title="Number of Returns", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No returns found in the dataset.")

with col2:
    st.markdown('<div class="section-header">🏢 Returns by Sales Zone</div>', unsafe_allow_html=True)
    if len(returned_df) > 0:
        zone_returns = returned_df.groupby('Sales Zone')['Sales Return'].sum().reset_index()
        fig = px.pie(zone_returns, values='Sales Return', names='Sales Zone', hole=0.3,
                     color_discrete_sequence=px.colors.sequential.Reds)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No returns found in the dataset.")

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">💳 Refunds by Payment Method</div>', unsafe_allow_html=True)
    if len(returned_df) > 0:
        payment_refunds = returned_df.groupby('Payment Method')['Credited Amount'].sum().reset_index()
        fig = px.bar(payment_refunds, x='Payment Method', y='Credited Amount',
                     color='Payment Method', text='Credited Amount')
        fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Refunded Amount (৳)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No refunds found in the dataset.")

with col2:
    st.markdown('<div class="section-header">📅 Returns Over Time (By Month)</div>', unsafe_allow_html=True)
    if 'Month Name' in df.columns and len(returned_df) > 0:
        monthly_returns = returned_df.groupby('Month Name')['Sales Return'].sum().reset_index()
        # Ensure correct month order (optional but recommended)
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        monthly_returns['Month Name'] = pd.Categorical(monthly_returns['Month Name'], categories=month_order, ordered=True)
        monthly_returns = monthly_returns.sort_values('Month Name')
        
        fig = px.line(monthly_returns, x='Month Name', y='Sales Return', markers=True)
        fig.update_traces(line=dict(color='#e74c3c', width=3), marker=dict(size=8))
        fig.update_layout(height=400, xaxis_title="Month", yaxis_title="Total Returns")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Month data not available or no returns found.")
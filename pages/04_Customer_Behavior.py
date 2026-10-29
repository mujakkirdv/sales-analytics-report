import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Customer Behavior", page_icon="🧠", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 Customer Behavior & Payments</h1>
    <p>Understand customer segments, preferred payment methods, and sales channels</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">👥 Revenue by Customer Type</div>', unsafe_allow_html=True)
    cust_rev = df.groupby('Customer Type')['Sales Amount'].sum().reset_index()
    fig = px.bar(cust_rev, x='Customer Type', y='Sales Amount', color='Customer Type', text='Sales Amount')
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Revenue (৳)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">💳 Payment Method Preferences</div>', unsafe_allow_html=True)
    pay_rev = df.groupby('Payment Method')['Sales Amount'].sum().reset_index()
    fig = px.pie(pay_rev, values='Sales Amount', names='Payment Method', hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🏦 Revenue by Bank</div>', unsafe_allow_html=True)
    # Filter out blanks/NaN in Bank Name
    bank_df = df.dropna(subset=['Bank Name'])
    bank_df = bank_df[bank_df['Bank Name'].astype(str).str.strip() != '']
    
    if len(bank_df) > 0:
        bank_rev = bank_df.groupby('Bank Name')['Sales Amount'].sum().nlargest(8).reset_index()
        fig = px.bar(bank_rev, x='Sales Amount', y='Bank Name', orientation='h',
                     color='Sales Amount', color_continuous_scale='Blues', text='Sales Amount')
        fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title="Revenue (৳)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No bank data available.")

with col2:
    st.markdown('<div class="section-header">🛒 Preferred Sales Channels</div>', unsafe_allow_html=True)
    channel_counts = df['Sales Channel'].value_counts().reset_index()
    channel_counts.columns = ['Sales Channel', 'Count']
    fig = px.pie(channel_counts, values='Count', names='Sales Channel', 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Additional Insight Section
st.markdown("---")
st.markdown('<div class="section-header">💡 Behavioral Insights</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Insight 1: Most popular payment method
top_payment = df.groupby('Payment Method')['Invoice No'].count().idxmax()
st.markdown(f"""
<div class="insight-card">
    <h4>💳 Top Payment Method</h4>
    <p><strong>{top_payment}</strong> is the most frequently used payment method.</p>
</div>
""", unsafe_allow_html=True)

# Insight 2: Top Customer Type
top_cust_type = df.groupby('Customer Type')['Sales Amount'].sum().idxmax()
st.markdown(f"""
<div class="insight-card">
    <h4>👑 Top Customer Segment</h4>
    <p><strong>{top_cust_type}</strong> customers generate the highest revenue.</p>
</div>
""", unsafe_allow_html=True)

# Insight 3: Most common Bank
top_bank = df[df['Bank Name'].notna() & (df['Bank Name'] != '')]['Bank Name'].value_counts().idxmax() if len(bank_df) > 0 else "N/A"
st.markdown(f"""
<div class="insight-card">
    <h4>🏦 Top Bank</h4>
    <p><strong>{top_bank}</strong> handles the most transactions.</p>
</div>
""", unsafe_allow_html=True)
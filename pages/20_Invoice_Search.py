import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Invoice Search", page_icon="🔎", layout="wide")
load_css()

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def get_data():
    return load_sales_data()

raw_df = get_data()
df = raw_df.copy()

# Clean and prepare
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date']).reset_index(drop=True)
df['Sales Amount'] = pd.to_numeric(df['Sales Amount'], errors='coerce').fillna(0)
df['Purchase Value'] = pd.to_numeric(df['Purchase Value'], errors='coerce').fillna(0)
df['Invoice Value'] = pd.to_numeric(df['Invoice Value'], errors='coerce').fillna(0)
df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)
df['Sales VAT'] = pd.to_numeric(df['Sales VAT'], errors='coerce').fillna(0)
df['Sales Return'] = pd.to_numeric(df['Sales Return'], errors='coerce').fillna(0)
df['Credited Amount'] = pd.to_numeric(df['Credited Amount'], errors='coerce').fillna(0)
df['Market Due'] = df['Invoice Value'] - df['Sales Amount']
df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']

# Convert ID columns to string for searching
df['Invoice No'] = df['Invoice No'].astype(str)
df['Transaction ID'] = df['Transaction ID'].astype(str)
df['Customer ID'] = df['Customer ID'].astype(str)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🔎 Invoice & Transaction Search</h1>
    <p>Look up any invoice, transaction, or customer instantly</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SEARCH BAR
# ============================================================================
st.markdown('<div class="section-header">🔍 Search</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    search_type = st.radio(
        "Search By:",
        ["Invoice No", "Transaction ID", "Customer Name", "Customer ID"],
        horizontal=True
    )

with col2:
    st.write("")  # spacing
    st.write("")  # spacing

# Build suggestion list based on search type
if search_type == "Invoice No":
    suggestions = sorted(df['Invoice No'].dropna().unique().tolist())
elif search_type == "Transaction ID":
    suggestions = sorted(df['Transaction ID'].dropna().unique().tolist())
elif search_type == "Customer Name":
    suggestions = sorted(df['Customer Name'].dropna().unique().tolist())
else:
    suggestions = sorted(df['Customer ID'].dropna().unique().tolist())

search_query = st.selectbox(
    f"Type or select a {search_type}:",
    options=[""] + suggestions,
    index=0,
    help="Start typing to search — the list will filter automatically"
)

if not search_query:
    st.info("👆 Select an ID from above or type to search. Results will appear below.")
    st.stop()

# ============================================================================
# FETCH RESULTS
# ============================================================================
if search_type == "Invoice No":
    results = df[df['Invoice No'] == search_query]
elif search_type == "Transaction ID":
    results = df[df['Transaction ID'] == search_query]
elif search_type == "Customer Name":
    results = df[df['Customer Name'] == search_query]
else:
    results = df[df['Customer ID'] == search_query]

if len(results) == 0:
    st.warning(f"No records found for **{search_type}:** `{search_query}`")
    st.stop()

st.markdown("---")

# ============================================================================
# INVOICE SUMMARY CARD
# ============================================================================
# Aggregate by Invoice No for a receipt-style view
invoice_df = results.copy()

# Take the first row's metadata (they share the same invoice-level info)
first_row = invoice_df.iloc[0]

total_sales = invoice_df['Sales Amount'].sum()
total_purchase = invoice_df['Purchase Value'].sum()
total_discount = invoice_df['Discount'].sum()
total_vat = invoice_df['Sales VAT'].sum()
total_returns = invoice_df['Sales Return'].sum()
total_credited = invoice_df['Credited Amount'].sum()
total_invoice_value = invoice_df['Invoice Value'].sum()
total_due = invoice_df['Market Due'].sum()
total_profit = invoice_df['Gross Profit'].sum()

# Status determination
if total_returns > 0 and total_credited > 0:
    status_label = "🔄 RETURNED"
    status_color = "#e74c3c"
elif total_due > 0:
    status_label = "⚠️ PARTIALLY PAID"
    status_color = "#f39c12"
else:
    status_label = "✅ PAID IN FULL"
    status_color = "#2ecc71"

# ============================================================================
# RECEIPT-STYLE HEADER
# ============================================================================
st.markdown(f"""
<div style="background: white; border-radius: 1rem; padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-top: 5px solid {status_color};">
    <div style="display: flex; justify-content: space-between; align-items: start;
                border-bottom: 1px dashed #ddd; padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <div>
            <div style="font-size: 0.75rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px;">
                Invoice No
            </div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e50;">
                {first_row['Invoice No']}
            </div>
            <div style="font-size: 0.85rem; color: #7f8c8d; margin-top: 0.25rem;">
                📅 {first_row['Date'].strftime('%d %B %Y')} · {first_row.get('Month Name', '')}
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px;">
                Status
            </div>
            <div style="font-size: 1.1rem; font-weight: bold; color: {status_color};">
                {status_label}
            </div>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div>
            <div style="font-size: 0.75rem; color: #7f8c8d; text-transform: uppercase;">Customer</div>
            <div style="font-size: 1rem; font-weight: bold; color: #2c3e50;">
                {first_row['Customer Name']}
            </div>
            <div style="font-size: 0.85rem; color: #7f8c8d;">
                ID: {first_row['Customer ID']} · Type: {first_row['Customer Type']}
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: #7f8c8d; text-transform: uppercase;">Sales Rep</div>
            <div style="font-size: 1rem; font-weight: bold; color: #2c3e50;">
                {first_row['Sales by']}
            </div>
            <div style="font-size: 0.85rem; color: #7f8c8d;">
                Zone: {first_row['Sales Zone']} · Channel: {first_row['Sales Channel']}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(" ")

# ============================================================================
# ITEMS LIST (LINE ITEMS)
# ============================================================================
st.markdown('<div class="section-header">🛒 Items in this Transaction</div>', unsafe_allow_html=True)

item_display = invoice_df[[
    'Product Name', 'Product Category', 'Barcode',
    'Purchase Value', 'Sales Amount', 'Discount', 'Sales VAT', 'Sales Return'
]].copy()

item_display.columns = [
    'Product', 'Category', 'Barcode',
    'Purchase (৳)', 'Sales (৳)', 'Discount (৳)', 'VAT (৳)', 'Return (৳)'
]

# Format numeric columns
for col in ['Purchase (৳)', 'Sales (৳)', 'Discount (৳)', 'VAT (৳)', 'Return (৳)']:
    item_display[col] = item_display[col].apply(lambda x: f"{x:,.2f}")

st.dataframe(item_display, use_container_width=True, hide_index=True)

# ============================================================================
# FINANCIAL BREAKDOWN (RECEIPT TOTALS)
# ============================================================================
st.markdown('<div class="section-header">💰 Financial Breakdown</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    breakdown = pd.DataFrame({
        'Description': [
            'Gross Invoice Value',
            'Less: Discount',
            'Less: Sales VAT',
            'Less: Sales Returns',
            'Add: Credited Amount',
            '**Net Sales Amount**',
            '',
            '**Market Due (Unpaid)**'
        ],
        'Amount (৳)': [
            f"{total_invoice_value:,.2f}",
            f"-{total_discount:,.2f}",
            f"-{total_vat:,.2f}",
            f"-{total_returns:,.2f}",
            f"+{total_credited:,.2f}",
            f"**{total_sales:,.2f}**",
            '',
            f"**{total_due:,.2f}**"
        ]
    })
    st.dataframe(breakdown, use_container_width=True, hide_index=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="margin-bottom: 0.5rem;">
        <div class="metric-icon">💵</div>
        <div class="metric-value">৳{total_sales:,.0f}</div>
        <div class="metric-label">Net Sales Amount</div>
    </div>
    <div class="metric-card" style="margin-bottom: 0.5rem;">
        <div class="metric-icon">📈</div>
        <div class="metric-value">৳{total_profit:,.0f}</div>
        <div class="metric-label">Gross Profit</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon">💳</div>
        <div class="metric-value">{first_row['Payment Method']}</div>
        <div class="metric-label">Payment Method</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ADDITIONAL DETAILS
# ============================================================================
st.markdown('<div class="section-header">📋 Additional Details</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    **Invoice Type:** {first_row.get('Invoice type', 'N/A')}  
    **Month:** {first_row.get('Month Name', 'N/A')}  
    **Bank:** {first_row.get('Bank Name', 'N/A')}  
    """)

with col2:
    st.markdown(f"""
    **Sales ID:** {first_row.get('Sales ID', 'N/A')}  
    **Zone Code:** {first_row.get('Zone Code', 'N/A')}  
    **Transaction ID:** `{first_row['Transaction ID']}`
    """)

with col3:
    st.markdown(f"""
    **Remarks:** {first_row.get('Remarks', 'None')}  
    **Records:** {len(invoice_df)} item(s)  
    **Total Items:** {invoice_df['Product Name'].nunique()}
    """)

# ============================================================================
# MULTI-INVOICE MODE (If multiple invoices match)
# ============================================================================
if len(invoice_df['Invoice No'].unique()) > 1:
    st.markdown("---")
    st.markdown('<div class="section-header">📊 All Matching Invoices</div>', unsafe_allow_html=True)
    
    st.caption(f"This {search_type} matched **{len(invoice_df['Invoice No'].unique())}** invoices. Summary below.")
    
    summary = invoice_df.groupby('Invoice No').agg({
        'Date': 'first',
        'Sales Amount': 'sum',
        'Invoice Value': 'sum',
        'Market Due': 'sum',
        'Sales Return': 'sum',
        'Product Name': 'count'
    }).reset_index()
    summary.columns = ['Invoice No', 'Date', 'Sales', 'Invoice Value', 'Due', 'Returns', 'Item Count']
    summary['Date'] = pd.to_datetime(summary['Date']).dt.strftime('%d %b %Y')
    
    for col in ['Sales', 'Invoice Value', 'Due', 'Returns']:
        summary[col] = summary[col].apply(lambda x: f"৳{x:,.0f}")
    
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ============================================================================
# QUICK ACTIONS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    csv = invoice_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download This Invoice (CSV)",
        data=csv,
        file_name=f"invoice_{search_query}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    if st.button("🔄 Copy Invoice No", use_container_width=True):
        st.success(f"Invoice No: **{first_row['Invoice No']}**")

with col3:
    if st.button("👤 View Customer Portfolio", use_container_width=True):
        st.info(f"Navigate to **Customer Dashboard** and search for **{first_row['Customer Name']}**")

st.markdown("""
<div class="dashboard-footer">
    <p>Invoice Search | Fast lookup for customer support & operations</p>
</div>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Profit & Loss", page_icon="📊", layout="wide")
load_css()

@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Ensure Date is datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">📅 YEAR</div>', unsafe_allow_html=True)
    available_years = sorted(df['Year'].dropna().unique().astype(int))
    selected_years = st.multiselect("Select Years", options=available_years, default=available_years)

    st.markdown('<div class="filter-label">📍 SALES ZONE</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Select Zones", options=zones, default=zones)

    st.markdown('<div class="filter-label">🛒 SALES CHANNEL</div>', unsafe_allow_html=True)
    channels = df['Sales Channel'].dropna().unique()
    selected_channels = st.multiselect("Select Channels", options=channels, default=channels)

# Apply Filters
filtered_df = df[
    (df['Year'].isin(selected_years)) &
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
    <h1>📊 Profit & Loss Statement</h1>
    <p>Formal Income Statement: Revenue → COGS → Gross Profit → Discounts → VAT → Returns → Net Profit</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FINANCIAL CALCULATIONS
# ============================================================================
# Revenue
gross_revenue = filtered_df['Sales Amount'].sum()
invoice_revenue = filtered_df['Invoice Value'].sum()
discounts = filtered_df['Discount'].sum()
vat = filtered_df['Sales VAT'].sum()
cogs = filtered_df['Purchase Value'].sum()
returns = filtered_df['Sales Return'].sum()
credited = filtered_df['Credited Amount'].sum()

# Derived
gross_profit = gross_revenue - cogs
net_revenue = gross_revenue - discounts - vat - returns
net_profit = net_revenue - cogs + credited

# Percentages
gross_margin_pct = (gross_profit / gross_revenue * 100) if gross_revenue > 0 else 0
net_margin_pct = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
cogs_pct = (cogs / gross_revenue * 100) if gross_revenue > 0 else 0
discount_pct = (discounts / gross_revenue * 100) if gross_revenue > 0 else 0
vat_pct = (vat / gross_revenue * 100) if gross_revenue > 0 else 0
return_pct = (returns / gross_revenue * 100) if gross_revenue > 0 else 0

# ============================================================================
# KPI METRICS
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💵</div>
        <div class="metric-value">৳{gross_revenue:,.0f}</div>
        <div class="metric-label">Gross Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value">৳{gross_profit:,.0f}</div>
        <div class="metric-label">Gross Profit ({gross_margin_pct:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🏆</div>
        <div class="metric-value">৳{net_profit:,.0f}</div>
        <div class="metric-label">Net Profit ({net_margin_pct:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🧾</div>
        <div class="metric-value">৳{cogs:,.0f}</div>
        <div class="metric-label">Total COGS</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# FORMAL P&L STATEMENT (TABLE)
# ============================================================================
st.markdown('<div class="section-header">📋 Statement of Profit & Loss</div>', unsafe_allow_html=True)

# Build the P&L table
pl_data = {
    'Line Item': [
        'Gross Revenue (Sales Amount)',
        '  Less: Discounts',
        '  Less: Sales VAT',
        '  Less: Sales Returns',
        'Net Revenue',
        '  Less: Cost of Goods Sold (Purchase Value)',
        'Gross Profit',
        '  Add: Credited Amount (Refunds Received)',
        'NET PROFIT',
    ],
    'Amount (৳)': [
        f"{gross_revenue:,.2f}",
        f"({discounts:,.2f})" if discounts else "0.00",
        f"({vat:,.2f})" if vat else "0.00",
        f"({returns:,.2f})" if returns else "0.00",
        f"{net_revenue:,.2f}",
        f"({cogs:,.2f})" if cogs else "0.00",
        f"{gross_profit:,.2f}",
        f"{credited:,.2f}" if credited else "0.00",
        f"{net_profit:,.2f}",
    ],
    '% of Revenue': [
        "100.0%",
        f"{discount_pct:.1f}%",
        f"{vat_pct:.1f}%",
        f"{return_pct:.1f}%",
        f"{(net_revenue/gross_revenue*100) if gross_revenue else 0:.1f}%",
        f"{cogs_pct:.1f}%",
        f"{gross_margin_pct:.1f}%",
        f"{(credited/gross_revenue*100) if gross_revenue else 0:.1f}%",
        f"{net_margin_pct:.1f}%",
    ]
}

pl_df = pd.DataFrame(pl_data)

# Style the table
st.dataframe(
    pl_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Line Item": st.column_config.TextColumn("Line Item", width="large"),
        "Amount (৳)": st.column_config.TextColumn("Amount (৳)", width="medium"),
        "% of Revenue": st.column_config.TextColumn("% of Revenue", width="small"),
    }
)

# ============================================================================
# MONTHLY P&L TREND
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📅 Monthly P&L Trend</div>', unsafe_allow_html=True)

if 'Month Name' in filtered_df.columns:
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    monthly_pl = filtered_df.groupby('Month Name').agg({
        'Sales Amount': 'sum',
        'Purchase Value': 'sum',
        'Discount': 'sum',
        'Sales VAT': 'sum',
        'Sales Return': 'sum',
        'Credited Amount': 'sum',
    }).reset_index()

    monthly_pl['Gross Profit'] = monthly_pl['Sales Amount'] - monthly_pl['Purchase Value']
    monthly_pl['Net Profit'] = (
        monthly_pl['Sales Amount']
        - monthly_pl['Discount']
        - monthly_pl['Sales VAT']
        - monthly_pl['Sales Return']
        - monthly_pl['Purchase Value']
        + monthly_pl['Credited Amount']
    )

    monthly_pl['Month Name'] = pd.Categorical(monthly_pl['Month Name'], categories=month_order, ordered=True)
    monthly_pl = monthly_pl.sort_values('Month Name')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_pl['Month Name'], y=monthly_pl['Sales Amount'],
        name='Revenue', marker_color='#667eea'
    ))
    fig.add_trace(go.Bar(
        x=monthly_pl['Month Name'], y=monthly_pl['Purchase Value'],
        name='COGS', marker_color='#e74c3c'
    ))
    fig.add_trace(go.Scatter(
        x=monthly_pl['Month Name'], y=monthly_pl['Gross Profit'],
        name='Gross Profit', mode='lines+markers',
        line=dict(color='#2ecc71', width=3), marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=monthly_pl['Month Name'], y=monthly_pl['Net Profit'],
        name='Net Profit', mode='lines+markers',
        line=dict(color='#f39c12', width=3, dash='dash'), marker=dict(size=10)
    ))
    fig.update_layout(
        height=450,
        barmode='group',
        xaxis_title="Month", yaxis_title="Amount (৳)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# EXPENSE BREAKDOWN (PIE)
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">🥧 Revenue Deductions Breakdown</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Pie of deductions
    deductions_data = pd.DataFrame({
        'Category': ['COGS (Purchase)', 'Discounts', 'VAT', 'Returns'],
        'Amount': [cogs, discounts, vat, returns]
    })
    deductions_data = deductions_data[deductions_data['Amount'] > 0]

    if len(deductions_data) > 0:
        fig = px.pie(
            deductions_data, values='Amount', names='Category', hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, title="Deductions from Gross Revenue")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No deductions recorded.")

with col2:
    # Waterfall chart: Revenue → Net Profit
    waterfall_data = go.Figure(go.Waterfall(
        name="P&L Waterfall",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=["Gross Revenue", "Discounts", "VAT", "Returns", "COGS", "Net Profit"],
        y=[gross_revenue, -discounts, -vat, -returns, -cogs, 0],
        textposition="outside",
        text=[
            f"৳{gross_revenue:,.0f}",
            f"-৳{discounts:,.0f}",
            f"-৳{vat:,.0f}",
            f"-৳{returns:,.0f}",
            f"-৳{cogs:,.0f}",
            f"৳{net_profit:,.0f}",
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#2ecc71"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#667eea"}},
    ))
    waterfall_data.update_layout(
        height=400,
        title="Revenue to Net Profit Waterfall",
        xaxis_title="", yaxis_title="Amount (৳)",
        showlegend=False
    )
    st.plotly_chart(waterfall_data, use_container_width=True)

# ============================================================================
# KEY FINANCIAL RATIOS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">🧮 Key Financial Ratios</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    markup = (gross_profit / cogs * 100) if cogs > 0 else 0
    st.metric("Markup %", f"{markup:.1f}%", help="Gross Profit / COGS")

with col2:
    expense_ratio = ((discounts + vat + returns) / gross_revenue * 100) if gross_revenue > 0 else 0
    st.metric("Deduction Ratio", f"{expense_ratio:.1f}%", help="(Discounts + VAT + Returns) / Revenue")

with col3:
    profit_per_invoice = (net_profit / filtered_df['Invoice No'].nunique()) if filtered_df['Invoice No'].nunique() > 0 else 0
    st.metric("Profit / Invoice", f"৳{profit_per_invoice:,.0f}")

with col4:
    avg_sale = (gross_revenue / filtered_df['Invoice No'].nunique()) if filtered_df['Invoice No'].nunique() > 0 else 0
    st.metric("Avg Sale / Invoice", f"৳{avg_sale:,.0f}")

# ============================================================================
# DOWNLOAD P&L REPORT
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📥 Download P&L Report</div>', unsafe_allow_html=True)

# Full P&L report for download (with raw numbers)
report_df = pd.DataFrame({
    'Line Item': [
        'Gross Revenue', 'Discounts', 'Sales VAT', 'Sales Returns',
        'Net Revenue', 'COGS', 'Gross Profit', 'Credited Amount', 'Net Profit'
    ],
    'Amount': [gross_revenue, discounts, vat, returns, net_revenue, cogs, gross_profit, credited, net_profit]
})

col1, col2 = st.columns(2)

with col1:
    csv = report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📄 Download P&L Statement (CSV)",
        data=csv,
        file_name="profit_and_loss_statement.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True
    )

with col2:
    # Monthly P&L download
    if 'monthly_pl' in locals():
        monthly_csv = monthly_pl[['Month Name', 'Sales Amount', 'Purchase Value', 'Gross Profit', 'Net Profit']].to_csv(index=False).encode('utf-8')
        st.download_button(
            "📅 Download Monthly P&L (CSV)",
            data=monthly_csv,
            file_name="monthly_profit_and_loss.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("""
<div class="dashboard-footer">
    <p>Profit & Loss Statement | Formal Financial Reporting</p>
</div>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Alerts & Anomalies", page_icon="🔔", layout="wide")
load_css()

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Ensure Date is datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Month_Num'] = df['Date'].dt.month

# Derived columns
df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']
df['Market Due'] = df['Invoice Value'] - df['Sales Amount']

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🔔 Alerts & Anomaly Detection</h1>
    <p>Automated monitoring for unusual activity, performance drops, and risky patterns</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR — ANOMALY THRESHOLDS
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">⚙️ THRESHOLDS</div>', unsafe_allow_html=True)
    
    sales_drop_pct = st.slider(
        "Sales Drop Alert (%)",
        min_value=5, max_value=50, value=20, step=5,
        help="Alert if monthly sales drop by more than this % vs prior month"
    )
    
    return_rate_threshold = st.slider(
        "High Return Rate (%)",
        min_value=5, max_value=50, value=15, step=1,
        help="Alert if a product's return rate exceeds this %"
    )
    
    due_threshold = st.slider(
        "Overdue Due Alert (৳)",
        min_value=1000, max_value=100000, value=10000, step=1000,
        help="Alert if a customer's total due exceeds this amount"
    )
    
    discount_threshold = st.slider(
        "Excessive Discount (%)",
        min_value=5, max_value=50, value=25, step=5,
        help="Alert if discount % of sales exceeds this"
    )
    
    st.markdown("---")
    st.markdown('<div class="filter-label">📅 PERIOD</div>', unsafe_allow_html=True)
    available_years = sorted(df['Year'].dropna().unique().astype(int), reverse=True)
    selected_year = st.selectbox("Year", options=available_years)

# Filter to selected year
df_year = df[df['Year'] == selected_year].copy()

if len(df_year) == 0:
    st.warning(f"No data for {selected_year}.")
    st.stop()

# ============================================================================
# RUN ALL ANOMALY DETECTIONS
# ============================================================================

alerts = []  # list of dicts: {type, severity, title, message, data}

# --- ALERT 1: Monthly Sales Drop ---
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_sales = df_year.groupby('Month_Num')['Sales Amount'].sum().reset_index()
monthly_sales = monthly_sales.sort_values('Month_Num')
monthly_sales['Prev_Sales'] = monthly_sales['Sales Amount'].shift(1)
monthly_sales['Change_Pct'] = (monthly_sales['Sales Amount'] - monthly_sales['Prev_Sales']) / monthly_sales['Prev_Sales'] * 100

for _, row in monthly_sales.iterrows():
    if pd.notna(row['Change_Pct']) and row['Change_Pct'] < -sales_drop_pct:
        month_name = month_order[int(row['Month_Num']) - 1]
        alerts.append({
            "type": "Sales Drop",
            "severity": "high",
            "icon": "📉",
            "title": f"Sales dropped {abs(row['Change_Pct']):.1f}% in {month_name}",
            "message": f"Revenue fell from ৳{row['Prev_Sales']:,.0f} to ৳{row['Sales Amount']:,.0f}. Investigate the cause."
        })

# --- ALERT 2: High Return Rate by Product ---
product_stats = df_year.groupby('Product Name').agg({
    'Sales Amount': 'sum',
    'Sales Return': 'sum',
    'Invoice No': 'nunique'
}).reset_index()
product_stats['Return_Rate'] = (product_stats['Sales Return'] / product_stats['Sales Amount'] * 100).round(1)
high_return = product_stats[product_stats['Return_Rate'] > return_rate_threshold].sort_values('Return_Rate', ascending=False)

for _, row in high_return.head(5).iterrows():
    alerts.append({
        "type": "High Return Rate",
        "severity": "high",
        "icon": "🔄",
        "title": f"{row['Product Name']} — {row['Return_Rate']}% return rate",
        "message": f"Total returns: ৳{row['Sales Return']:,.0f} out of ৳{row['Sales Amount']:,.0f} in sales."
    })

# --- ALERT 3: Overdue Market Due by Customer ---
customer_due = df_year.groupby('Customer Name')['Market Due'].sum().reset_index()
customer_due = customer_due[customer_due['Market Due'] > due_threshold].sort_values('Market Due', ascending=False)

for _, row in customer_due.head(5).iterrows():
    alerts.append({
        "type": "Overdue Payment",
        "severity": "high",
        "icon": "⚠️",
        "title": f"{row['Customer Name']} owes ৳{row['Market Due']:,.0f}",
        "message": f"Outstanding balance exceeds the {due_threshold:,}৳ threshold. Follow up on collection."
    })

# --- ALERT 4: Excessive Discount ---
discount_by_product = df_year.groupby('Product Name').agg({
    'Sales Amount': 'sum',
    'Discount': 'sum'
}).reset_index()
discount_by_product['Discount_Pct'] = (discount_by_product['Discount'] / discount_by_product['Sales Amount'] * 100).round(1)
high_discount = discount_by_product[discount_by_product['Discount_Pct'] > discount_threshold].sort_values('Discount_Pct', ascending=False)

for _, row in high_discount.head(5).iterrows():
    alerts.append({
        "type": "Excessive Discount",
        "severity": "medium",
        "icon": "🏷️",
        "title": f"{row['Product Name']} — {row['Discount_Pct']}% discount",
        "message": f"Discount of ৳{row['Discount']:,.0f} on ৳{row['Sales Amount']:,.0f} in sales. Margin may be under pressure."
    })

# --- ALERT 5: Negative Profit Products ---
neg_profit = df_year[df_year['Gross Profit'] < 0].groupby('Product Name').agg({
    'Gross Profit': 'sum',
    'Sales Amount': 'sum'
}).reset_index()
neg_profit = neg_profit.sort_values('Gross Profit').head(5)

for _, row in neg_profit.iterrows():
    alerts.append({
        "type": "Loss-Making Product",
        "severity": "high",
        "icon": "🔴",
        "title": f"{row['Product Name']} — ৳{row['Gross Profit']:,.0f} loss",
        "message": f"Sales: ৳{row['Sales Amount']:,.0f}. Purchase cost exceeds sales price — review pricing."
    })

# --- ALERT 6: Outlier Transactions (3σ Rule) ---
sales_mean = df_year['Sales Amount'].mean()
sales_std = df_year['Sales Amount'].std()
outliers = df_year[df_year['Sales Amount'] > sales_mean + 3 * sales_std]

if len(outliers) > 0:
    alerts.append({
        "type": "Statistical Outlier",
        "severity": "low",
        "icon": "🔍",
        "title": f"{len(outliers)} unusually large transaction(s)",
        "message": f"Transactions exceed ৳{sales_mean + 3 * sales_std:,.0f} (mean + 3σ). Verify for data entry errors."
    })

# --- ALERT 7: Zero-Sales Zones (Low-performing Zones) ---
zone_sales = df_year.groupby('Sales Zone')['Sales Amount'].sum().reset_index()
zone_mean = zone_sales['Sales Amount'].mean()
low_zones = zone_sales[zone_sales['Sales Amount'] < zone_mean * 0.3].sort_values('Sales Amount')

for _, row in low_zones.iterrows():
    alerts.append({
        "type": "Underperforming Zone",
        "severity": "medium",
        "icon": "📍",
        "title": f"{row['Sales Zone']} is underperforming",
        "message": f"Only ৳{row['Sales Amount']:,.0f} vs. average of ৳{zone_mean:,.0f} across zones."
    })

# ============================================================================
# SUMMARY KPIs
# ============================================================================
critical = sum(1 for a in alerts if a['severity'] == 'high')
medium = sum(1 for a in alerts if a['severity'] == 'medium')
low = sum(1 for a in alerts if a['severity'] == 'low')

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🚨</div>
        <div class="metric-value" style="color:#e74c3c;">{critical}</div>
        <div class="metric-label">Critical Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">⚠️</div>
        <div class="metric-value" style="color:#f39c12;">{medium}</div>
        <div class="metric-label">Warnings</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">ℹ️</div>
        <div class="metric-value" style="color:#3498db;">{low}</div>
        <div class="metric-label">Info</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-value">{len(alerts)}</div>
        <div class="metric-label">Total Alerts</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# ALERTS DISPLAY (Cards)
# ============================================================================
st.markdown('<div class="section-header">🚨 Active Alerts</div>', unsafe_allow_html=True)

if not alerts:
    st.success("✅ No anomalies detected. Your business looks healthy!")
else:
    severity_color = {
        "high": "#e74c3c",
        "medium": "#f39c12",
        "low": "#3498db"
    }
    severity_label = {
        "high": "CRITICAL",
        "medium": "WARNING",
        "low": "INFO"
    }
    
    for alert in alerts:
        color = severity_color[alert['severity']]
        label = severity_label[alert['severity']]
        st.markdown(f"""
        <div style="background: white; padding: 1rem 1.5rem; margin-bottom: 0.75rem;
                    border-radius: 0.75rem; border-left: 5px solid {color};
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="display:flex; align-items:center; gap:0.75rem;">
                <span style="font-size:1.8rem;">{alert['icon']}</span>
                <div style="flex:1;">
                    <div style="font-size:0.7rem; font-weight:bold; color:{color};
                                text-transform:uppercase; letter-spacing:1px;">
                        {label} · {alert['type']}
                    </div>
                    <div style="font-size:1rem; font-weight:bold; color:#2c3e50; margin-top:0.2rem;">
                        {alert['title']}
                    </div>
                    <div style="font-size:0.85rem; color:#7f8c8d; margin-top:0.3rem;">
                        {alert['message']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# VISUAL ANOMALY DETECTION — CHARTS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📊 Visual Anomaly Detection</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Monthly sales trend with anomaly markers
    st.markdown("**📈 Monthly Sales with Anomaly Markers**")
    
    monthly_plot = monthly_sales.copy()
    monthly_plot['Month_Name'] = monthly_plot['Month_Num'].map(lambda x: month_order[int(x) - 1])
    
    colors = ['#e74c3c' if (pd.notna(chg) and chg < -sales_drop_pct) else '#667eea' 
              for chg in monthly_plot['Change_Pct']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_plot['Month_Name'], y=monthly_plot['Sales Amount'],
        marker_color=colors, name='Monthly Sales',
        text=monthly_plot['Sales Amount'].apply(lambda x: f"৳{x:,.0f}"),
        textposition='outside'
    ))
    fig.update_layout(
        height=400, xaxis_title="", yaxis_title="Sales (৳)",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Red bars indicate months where sales dropped by more than the alert threshold.")

with col2:
    # Return rate by product (with threshold line)
    st.markdown("**🔄 Return Rate by Product (Top 10)**")
    
    top_return_products = product_stats.sort_values('Return_Rate', ascending=False).head(10)
    
    colors_ret = ['#e74c3c' if v > return_rate_threshold else '#667eea' for v in top_return_products['Return_Rate']]
    
    fig = go.Figure(go.Bar(
        y=top_return_products['Product Name'], x=top_return_products['Return_Rate'],
        orientation='h', marker_color=colors_ret,
        text=top_return_products['Return_Rate'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside'
    ))
    fig.add_vline(x=return_rate_threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Threshold {return_rate_threshold}%")
    fig.update_layout(
        height=400, xaxis_title="Return Rate (%)", yaxis_title="",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# OUTLIER TRANSACTIONS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">🔍 Outlier Transactions (3σ Rule)</div>', unsafe_allow_html=True)

if len(outliers) > 0:
    st.write(f"Found **{len(outliers)}** transactions with unusually large sales (above ৳{sales_mean + 3 * sales_std:,.0f}).")
    
    display_cols = ['Date', 'Invoice No', 'Customer Name', 'Product Name', 'Sales Amount', 'Sales by', 'Sales Zone']
    available_cols = [c for c in display_cols if c in outliers.columns]
    
    outlier_display = outliers[available_cols].copy()
    outlier_display['Sales Amount'] = outlier_display['Sales Amount'].apply(lambda x: f"৳{x:,.0f}")
    
    st.dataframe(outlier_display, use_container_width=True, hide_index=True)
else:
    st.success("✅ No outlier transactions detected.")

# ============================================================================
# CUSTOMER RISK MATRIX
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">⚠️ Customer Risk Matrix (Due vs. Returns)</div>', unsafe_allow_html=True)

customer_risk = df_year.groupby('Customer Name').agg({
    'Market Due': 'sum',
    'Sales Return': 'sum',
    'Sales Amount': 'sum'
}).reset_index()
customer_risk['Return_Pct'] = (customer_risk['Sales Return'] / customer_risk['Sales Amount'] * 100).round(1)
customer_risk = customer_risk[customer_risk['Market Due'] > 0]

if len(customer_risk) > 0:
    fig = px.scatter(
        customer_risk,
        x='Market Due', y='Return_Pct',
        size='Sales Amount', color='Return_Pct',
        hover_name='Customer Name',
        color_continuous_scale='Reds',
        labels={'Market Due': 'Outstanding Due (৳)', 'Return_Pct': 'Return Rate (%)'},
        title="Customers with Outstanding Due — Risk Assessment"
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Top-right quadrant: High due AND high return rate — highest risk customers.")
else:
    st.success("✅ No customers with outstanding dues.")

# ============================================================================
# EXPORT ALERTS
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📥 Export Alerts</div>', unsafe_allow_html=True)

if alerts:
    alerts_export = pd.DataFrame(alerts)
    csv = alerts_export[['severity', 'type', 'title', 'message']].to_csv(index=False).encode('utf-8')
    st.download_button(
        "📄 Download Alerts Report (CSV)",
        data=csv,
        file_name=f"alerts_{selected_year}.csv",
        mime="text/csv",
        type="primary"
    )

st.markdown("""
<div class="dashboard-footer">
    <p>Alerts & Anomaly Detection | Automated Business Monitoring</p>
</div>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Time Intelligence", page_icon="🗓️", layout="wide")
load_css()

# ============================================================================
# LOAD DATA & DERIVED COLUMNS
# ============================================================================
@st.cache_data
def get_data():
    return load_sales_data()

df = get_data()

# Ensure numeric columns are correct
df['Sales Amount'] = pd.to_numeric(df['Sales Amount'], errors='coerce').fillna(0)
df['Purchase Value'] = pd.to_numeric(df['Purchase Value'], errors='coerce').fillna(0)

# ✅ Create derived columns BEFORE any filtering/grouping
df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']
df['Market Due'] = df['Invoice Value'] - df['Sales Amount']

# Ensure Date is datetime and extract time components
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Month_Name'] = df['Date'].dt.strftime('%B')
    df['Day'] = df['Date'].dt.day
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df['Week_of_Year'] = df['Date'].dt.isocalendar().week
    df['Quarter'] = df['Date'].dt.quarter
    df['Weekday_Num'] = df['Date'].dt.weekday  # 0=Monday, 6=Sunday

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🗓️ Time Intelligence & Seasonality</h1>
    <p>Discover your business rhythms: day-of-week patterns, monthly trends, and seasonal peaks</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">📅 YEAR</div>', unsafe_allow_html=True)
    available_years = sorted(df['Year'].dropna().unique().astype(int), reverse=True)
    selected_years = st.multiselect("Select Years", options=available_years, default=available_years)

    st.markdown('<div class="filter-label">📍 SALES ZONE</div>', unsafe_allow_html=True)
    zones = df['Sales Zone'].dropna().unique()
    selected_zones = st.multiselect("Select Zones", options=zones, default=zones)

    st.markdown('<div class="filter-label">🛒 SALES CHANNEL</div>', unsafe_allow_html=True)
    channels = df['Sales Channel'].dropna().unique()
    selected_channels = st.multiselect("Select Channels", options=channels, default=channels)

# Apply filters
filtered = df[
    (df['Year'].isin(selected_years)) &
    (df['Sales Zone'].isin(selected_zones)) &
    (df['Sales Channel'].isin(selected_channels))
]

if len(filtered) == 0:
    st.warning("⚠️ No data matches the selected filters.")
    st.stop()

# Common month order for sorting
month_order_full = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December']

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Trend Overview",
    "📅 Calendar Heatmap",
    "📆 Day & Month Patterns",
    "📈 Year-over-Year"
])

# ============================================================================
# TAB 1: TREND OVERVIEW
# ============================================================================
with tab1:
    # Daily sales trend
    daily = filtered.groupby(filtered['Date'].dt.date).agg({
        'Sales Amount': 'sum',
        'Gross Profit': 'sum'
    }).reset_index()
    daily.columns = ['Date', 'Sales Amount', 'Gross Profit']
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily = daily.sort_values('Date')

    # Calculate 7-day moving average
    daily['7-Day Avg'] = daily['Sales Amount'].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily['Date'], y=daily['Sales Amount'],
        mode='lines', name='Daily Sales',
        line=dict(color='#667eea', width=1.5), opacity=0.6
    ))
    fig.add_trace(go.Scatter(
        x=daily['Date'], y=daily['7-Day Avg'],
        mode='lines', name='7-Day Moving Average',
        line=dict(color='#e74c3c', width=3)
    ))
    fig.update_layout(
        height=450, xaxis_title="Date", yaxis_title="Sales (৳)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        best_day = daily.loc[daily['Sales Amount'].idxmax()]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏆</div>
            <div class="metric-value">৳{best_day['Sales Amount']:,.0f}</div>
            <div class="metric-label">Best Day ({best_day['Date'].strftime('%d %b %Y')})</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        worst_day = daily.loc[daily['Sales Amount'].idxmin()]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📉</div>
            <div class="metric-value">৳{worst_day['Sales Amount']:,.0f}</div>
            <div class="metric-label">Worst Day ({worst_day['Date'].strftime('%d %b %Y')})</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_daily = daily['Sales Amount'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">৳{avg_daily:,.0f}</div>
            <div class="metric-label">Avg Daily Sales</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Monthly revenue by year
    st.markdown('<div class="section-header">📅 Monthly Revenue by Year</div>', unsafe_allow_html=True)

    monthly_by_year = filtered.groupby(['Year', 'Month_Name'])['Sales Amount'].sum().reset_index()
    monthly_by_year['Month_Name'] = pd.Categorical(monthly_by_year['Month_Name'], categories=month_order_full, ordered=True)
    monthly_by_year = monthly_by_year.sort_values(['Year', 'Month_Name'])

    fig = px.line(
        monthly_by_year, x='Month_Name', y='Sales Amount', color='Year',
        markers=True, color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig.update_layout(
        height=450, xaxis_title="Month", yaxis_title="Sales (৳)",
        legend_title="Year"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2: CALENDAR HEATMAP
# ============================================================================
with tab2:
    st.markdown('<div class="section-header">🔥 GitHub-Style Calendar Heatmap</div>', unsafe_allow_html=True)
    st.caption("Each square = one day. Darker = more sales. Hover for exact values.")

    heatmap_year = st.selectbox("Select Year for Heatmap", options=sorted(selected_years, reverse=True), index=0)
    year_data = filtered[filtered['Year'] == heatmap_year]

    if len(year_data) == 0:
        st.warning(f"No data for {heatmap_year}.")
    else:
        daily_year = year_data.groupby(year_data['Date'].dt.date)['Sales Amount'].sum().reset_index()
        daily_year.columns = ['Date', 'Sales']
        daily_year['Date'] = pd.to_datetime(daily_year['Date'])

        daily_year['Week'] = daily_year['Date'].dt.isocalendar().week
        daily_year['Weekday'] = daily_year['Date'].dt.weekday

        pivot = daily_year.pivot_table(index='Weekday', columns='Week', values='Sales', aggfunc='sum').fillna(0)

        for d in range(7):
            if d not in pivot.index:
                pivot.loc[d] = 0
        pivot = pivot.sort_index()

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=[f"W{int(c)}" for c in pivot.columns],
            y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            colorscale='Viridis',
            hovertemplate='Week %{x}<br>Day: %{y}<br>Sales: ৳%{z:,.0f}<extra></extra>',
            colorbar=dict(title="Sales (৳)")
        ))
        fig.update_layout(
            height=300, xaxis_title="Week of Year", yaxis_title="",
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Year × Month Heatmap
    st.markdown('<div class="section-header">📅 Year × Month Heatmap</div>', unsafe_allow_html=True)

    ym_data = filtered.groupby(['Year', 'Month_Name'])['Sales Amount'].sum().reset_index()
    ym_data['Month_Name'] = pd.Categorical(ym_data['Month_Name'], categories=month_order_full, ordered=True)
    ym_data = ym_data.sort_values(['Year', 'Month_Name'])

    ym_pivot = ym_data.pivot_table(index='Year', columns='Month_Name', values='Sales Amount', aggfunc='sum').fillna(0)

    fig = px.imshow(
        ym_pivot.values,
        x=[str(c) for c in ym_pivot.columns],
        y=[str(i) for i in ym_pivot.index],
        labels=dict(x="Month", y="Year", color="Sales (৳)"),
        color_continuous_scale='YlOrRd',
        aspect='auto',
        text_auto='.2s'
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 3: DAY & MONTH PATTERNS
# ============================================================================
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">📆 Sales by Day of Week</div>', unsafe_allow_html=True)

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_data = filtered.groupby('Day_of_Week')['Sales Amount'].sum().reset_index()
        dow_data['Day_of_Week'] = pd.Categorical(dow_data['Day_of_Week'], categories=weekday_order, ordered=True)
        dow_data = dow_data.sort_values('Day_of_Week')

        best_dow = dow_data.loc[dow_data['Sales Amount'].idxmax(), 'Day_of_Week']
        colors_dow = ['#e74c3c' if d == best_dow else '#667eea' for d in dow_data['Day_of_Week']]

        fig = go.Figure(go.Bar(
            x=dow_data['Day_of_Week'], y=dow_data['Sales Amount'],
            marker_color=colors_dow,
            text=dow_data['Sales Amount'].apply(lambda x: f"৳{x:,.0f}"),
            textposition='outside'
        ))
        fig.update_layout(height=400, xaxis_title="", yaxis_title="Sales (৳)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"🏆 Best day: **{best_dow}**")

    with col2:
        st.markdown('<div class="section-header">📅 Total Sales by Month</div>', unsafe_allow_html=True)

        month_stats = filtered.groupby('Month_Name')['Sales Amount'].sum().reset_index()
        month_stats['Month_Name'] = pd.Categorical(month_stats['Month_Name'], categories=month_order_full, ordered=True)
        month_stats = month_stats.sort_values('Month_Name')

        best_month = month_stats.loc[month_stats['Sales Amount'].idxmax(), 'Month_Name']
        colors_month = ['#2ecc71' if m == best_month else '#3498db' for m in month_stats['Month_Name']]

        fig = go.Figure(go.Bar(
            x=month_stats['Month_Name'], y=month_stats['Sales Amount'],
            marker_color=colors_month,
            text=month_stats['Sales Amount'].apply(lambda x: f"৳{x:,.0f}"),
            textposition='outside'
        ))
        fig.update_layout(height=400, xaxis_title="", yaxis_title="Sales (৳)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"🏆 Best month: **{best_month}**")

    st.markdown("---")

    # Quarterly breakdown
    st.markdown('<div class="section-header">📊 Quarterly Revenue Distribution</div>', unsafe_allow_html=True)

    quarterly = filtered.groupby(['Year', 'Quarter'])['Sales Amount'].sum().reset_index()
    quarterly['Quarter_Label'] = 'Q' + quarterly['Quarter'].astype(str)
    quarterly['Year_Quarter'] = quarterly['Year'].astype(str) + ' ' + quarterly['Quarter_Label']

    fig = px.bar(
        quarterly, x='Year_Quarter', y='Sales Amount',
        color='Quarter_Label', text='Sales Amount',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig.update_traces(texttemplate='৳%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, xaxis_title="", yaxis_title="Sales (৳)")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 4: YEAR-OVER-YEAR
# ============================================================================
with tab4:
    if len(selected_years) < 2:
        st.info("Please select at least 2 years in the sidebar to enable Year-over-Year comparison.")
    else:
        st.markdown('<div class="section-header">📈 Year-over-Year Comparison</div>', unsafe_allow_html=True)

        yoy = filtered.groupby('Year').agg({
            'Sales Amount': 'sum',
            'Invoice No': 'nunique',
            'Customer Name': 'nunique'
        }).reset_index()
        yoy.columns = ['Year', 'Total Sales', 'Invoices', 'Unique Customers']

        yoy['Sales Growth %'] = yoy['Total Sales'].pct_change() * 100
        yoy['Invoices Growth %'] = yoy['Invoices'].pct_change() * 100

        display_yoy = yoy.copy()
        display_yoy['Total Sales'] = display_yoy['Total Sales'].apply(lambda x: f"৳{x:,.0f}")
        display_yoy['Sales Growth %'] = display_yoy['Sales Growth %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "—")
        display_yoy['Invoices Growth %'] = display_yoy['Invoices Growth %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "—")

        st.dataframe(display_yoy, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Side-by-side monthly comparison
        st.markdown('<div class="section-header">📅 Monthly Comparison Across Years</div>', unsafe_allow_html=True)

        yoy_monthly = filtered.groupby(['Year', 'Month_Name'])['Sales Amount'].sum().reset_index()
        yoy_monthly['Month_Name'] = pd.Categorical(yoy_monthly['Month_Name'], categories=month_order_full, ordered=True)
        yoy_monthly = yoy_monthly.sort_values(['Month_Name', 'Year'])

        fig = px.bar(
            yoy_monthly, x='Month_Name', y='Sales Amount', color='Year',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set1,
            text='Sales Amount'
        )
        fig.update_traces(texttemplate='৳%{text:,.0s}', textposition='outside')
        fig.update_layout(height=450, xaxis_title="", yaxis_title="Sales (৳)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Month-over-Month Growth
        st.markdown('<div class="section-header">📊 Month-over-Month Growth Rate</div>', unsafe_allow_html=True)

        mom = filtered.groupby(['Year', 'Month_Name'])['Sales Amount'].sum().reset_index()
        mom['Month_Name'] = pd.Categorical(mom['Month_Name'], categories=month_order_full, ordered=True)
        mom = mom.sort_values(['Year', 'Month_Name'])
        mom['Growth %'] = mom.groupby('Year')['Sales Amount'].pct_change() * 100
        mom = mom.dropna(subset=['Growth %'])

        if len(mom) > 0:
            mom['Label'] = mom['Year'].astype(str) + ' ' + mom['Month_Name'].astype(str).str[:3]
            colors_g = ['#2ecc71' if x >= 0 else '#e74c3c' for x in mom['Growth %']]

            fig = go.Figure(go.Bar(
                x=mom['Label'], y=mom['Growth %'],
                marker_color=colors_g,
                text=mom['Growth %'].apply(lambda x: f"{x:+.1f}%"),
                textposition='outside'
            ))
            fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
            fig.update_layout(
                height=400, xaxis_title="", yaxis_title="MoM Growth (%)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🟢 Green = growth from prior month. 🔴 Red = decline from prior month.")

        st.markdown("---")

        # Seasonality Insights
        st.markdown('<div class="section-header">💡 Seasonality Insights</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            peak = filtered.groupby('Month_Name')['Sales Amount'].sum().idxmax()
            st.markdown(f"""
            <div class="insight-card">
                <h4>🌞 Peak Month</h4>
                <p><strong>{peak}</strong> is consistently your highest revenue month.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            peak_dow = filtered.groupby('Day_of_Week')['Sales Amount'].sum().idxmax()
            st.markdown(f"""
            <div class="insight-card">
                <h4>📅 Peak Weekday</h4>
                <p><strong>{peak_dow}</strong> generates the most revenue each week.</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            peak_q = filtered.groupby('Quarter')['Sales Amount'].sum().idxmax()
            st.markdown(f"""
            <div class="insight-card">
                <h4>📊 Peak Quarter</h4>
                <p><strong>Q{peak_q}</strong> is your strongest quarter overall.</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# EXPORT
# ============================================================================
st.markdown("---")
st.markdown('<div class="section-header">📥 Export Time Data</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    daily_export = filtered.groupby(filtered['Date'].dt.date)['Sales Amount'].sum().reset_index()
    daily_export.columns = ['Date', 'Sales Amount']
    csv = daily_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📄 Download Daily Sales (CSV)",
        data=csv,
        file_name="daily_sales.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    if len(selected_years) >= 2:
        yoy_export = filtered.groupby(['Year', 'Month_Name'])['Sales Amount'].sum().reset_index()
        csv2 = yoy_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📄 Download Monthly by Year (CSV)",
            data=csv2,
            file_name="monthly_by_year.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("""
<div class="dashboard-footer">
    <p>Time Intelligence | Discover when your business performs best</p>
</div>
""", unsafe_allow_html=True)
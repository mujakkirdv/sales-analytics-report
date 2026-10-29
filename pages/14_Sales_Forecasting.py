import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression
from utils.data_loader import load_sales_data, load_css


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Sales Forecasting",
    page_icon="🔮",
    layout="wide"
)

load_css()


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def get_data():
    return load_sales_data()


raw_df = get_data()

if raw_df is None or raw_df.empty:
    st.error("No sales data available. Please check your data source.")
    st.stop()


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================
required_cols = [
    "Date",
    "Sales Amount",
    "Purchase Value",
    "Invoice No",
    "Sales Zone",
    "Sales Channel",
    "Product Name"
]

missing = [col for col in required_cols if col not in raw_df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()


# ============================================================
# DATA CLEANING AND PREPROCESSING
# ============================================================
df = raw_df.copy()

# Convert dates safely
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df = df.dropna(subset=["Date"]).copy()

# Convert numeric columns
df["Sales Amount"] = pd.to_numeric(
    df["Sales Amount"],
    errors="coerce"
).fillna(0)

df["Purchase Value"] = pd.to_numeric(
    df["Purchase Value"],
    errors="coerce"
).fillna(0)

# Calculate gross profit
df["Gross Profit"] = (
    df["Sales Amount"] - df["Purchase Value"]
)

# Create the first day of each month
df["Month_Start"] = df["Date"].dt.to_period("M").dt.to_timestamp()

df = df.dropna(subset=["Month_Start"]).copy()

if df.empty:
    st.error("No valid sales records were found after cleaning the data.")
    st.stop()


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="main-header">
        <h1>🔮 Sales Forecasting & Projections</h1>
        <p>Predict future revenue using historical trends and moving averages</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================
with st.sidebar:

    st.markdown(
        '<div class="filter-label">⚙️ FORECAST SETTINGS</div>',
        unsafe_allow_html=True
    )

    forecast_months = st.slider(
        "Forecast Horizon (Months)",
        min_value=1,
        max_value=12,
        value=3,
        step=1
    )

    st.markdown(
        '<div class="filter-label">📍 FILTER DATA</div>',
        unsafe_allow_html=True
    )

    zones = sorted(
        df["Sales Zone"].dropna().unique().tolist(),
        key=str
    )

    selected_zones = st.multiselect(
        "Sales Zone",
        options=zones,
        default=zones
    )

    channels = sorted(
        df["Sales Channel"].dropna().unique().tolist(),
        key=str
    )

    selected_channels = st.multiselect(
        "Sales Channel",
        options=channels,
        default=channels
    )


# ============================================================
# APPLY FILTERS
# ============================================================
filtered = df[
    df["Sales Zone"].isin(selected_zones)
    & df["Sales Channel"].isin(selected_channels)
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


# ============================================================
# MONTHLY AGGREGATION
# ============================================================
monthly_data = (
    filtered.groupby("Month_Start", as_index=False)
    .agg(
        {
            "Sales Amount": "sum",
            "Gross Profit": "sum",
            "Invoice No": "nunique"
        }
    )
    .sort_values("Month_Start")
    .reset_index(drop=True)
)

monthly_data.rename(
    columns={"Invoice No": "Invoices"},
    inplace=True
)

if len(monthly_data) < 3:
    st.warning(
        "Not enough historical data to generate a reliable trend. "
        "At least 3 distinct months are required."
    )
    st.stop()


# ============================================================
# LINEAR REGRESSION FORECAST
# ============================================================
# Use sequential integer month indexes rather than dates.
# This prevents mixing datetime objects with integers.

monthly_data["Month_Index"] = np.arange(
    len(monthly_data),
    dtype=int
)

X = monthly_data[["Month_Index"]].to_numpy(dtype=float)

y_sales = monthly_data["Sales Amount"].to_numpy(dtype=float)
y_profit = monthly_data["Gross Profit"].to_numpy(dtype=float)

# Train sales model
model_sales = LinearRegression()
model_sales.fit(X, y_sales)

# Train profit model
model_profit = LinearRegression()
model_profit.fit(X, y_profit)


# ============================================================
# GENERATE FUTURE MONTHS
# ============================================================
last_month = monthly_data["Month_Start"].max()

# Create future month-start dates without datetime arithmetic
future_dates = pd.date_range(
    start=last_month + pd.offsets.MonthBegin(1),
    periods=forecast_months,
    freq="MS"
)

future_indices = np.arange(
    len(monthly_data),
    len(monthly_data) + forecast_months,
    dtype=float
).reshape(-1, 1)

# Predict future values
predicted_sales = model_sales.predict(future_indices)
predicted_profit = model_profit.predict(future_indices)

# Prevent negative forecast values
predicted_sales = np.clip(predicted_sales, 0, None)
predicted_profit = np.clip(predicted_profit, 0, None)

future_df = pd.DataFrame(
    {
        "Month_Start": future_dates,
        "Forecasted Sales": predicted_sales,
        "Forecasted Profit": predicted_profit
    }
)


# ============================================================
# CALCULATE KPIs
# ============================================================
total_forecasted_sales = future_df["Forecasted Sales"].sum()

total_forecasted_profit = future_df["Forecasted Profit"].sum()

avg_monthly_forecast = future_df["Forecasted Sales"].mean()

last_actual_month = float(
    monthly_data["Sales Amount"].iloc[-1]
)

first_forecast_month = float(
    future_df["Forecasted Sales"].iloc[0]
)

if last_actual_month > 0:
    growth_pct = (
        (first_forecast_month - last_actual_month)
        / last_actual_month
    ) * 100
else:
    growth_pct = 0.0


# ============================================================
# DISPLAY KPI CARDS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">
                ৳{total_forecasted_sales:,.0f}
            </div>
            <div class="metric-label">
                Total Forecasted Sales ({forecast_months}mo)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-value">
                ৳{total_forecasted_profit:,.0f}
            </div>
            <div class="metric-label">
                Total Forecasted Profit
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">
                ৳{avg_monthly_forecast:,.0f}
            </div>
            <div class="metric-label">
                Average Monthly Forecast
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    if growth_pct >= 0:
        growth_color = "#2ecc71"
        growth_icon = "⬆️"
    else:
        growth_color = "#e74c3c"
        growth_icon = "⬇️"

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{growth_icon}</div>
            <div class="metric-value"
                 style="color: {growth_color};">
                {growth_pct:+.1f}%
            </div>
            <div class="metric-label">
                Next-Month Growth
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("---")


# ============================================================
# HISTORICAL VS FORECASTED SALES CHART
# ============================================================
st.markdown(
    '<div class="section-header">📈 Historical vs Forecasted Sales</div>',
    unsafe_allow_html=True
)

fig = go.Figure()

# Historical sales
fig.add_trace(
    go.Scatter(
        x=monthly_data["Month_Start"],
        y=monthly_data["Sales Amount"],
        mode="lines+markers",
        name="Historical Sales",
        line=dict(color="#667eea", width=3),
        marker=dict(size=8)
    )
)

# Historical profit
fig.add_trace(
    go.Scatter(
        x=monthly_data["Month_Start"],
        y=monthly_data["Gross Profit"],
        mode="lines+markers",
        name="Historical Profit",
        line=dict(
            color="#2ecc71",
            width=2,
            dash="dot"
        ),
        marker=dict(size=6)
    )
)

# Forecasted sales
fig.add_trace(
    go.Scatter(
        x=future_df["Month_Start"],
        y=future_df["Forecasted Sales"],
        mode="lines+markers",
        name="Forecasted Sales",
        line=dict(
            color="#e74c3c",
            width=3,
            dash="dash"
        ),
        marker=dict(
            size=10,
            symbol="diamond"
        )
    )
)

# FIX: Use add_shape instead of add_vline.
# This avoids Plotly's datetime annotation arithmetic error.
now_date = monthly_data["Month_Start"].max()

fig.add_shape(
    type="line",
    x0=now_date,
    x1=now_date,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(
        color="gray",
        width=2,
        dash="dash"
    )
)

fig.add_annotation(
    x=now_date,
    y=1,
    xref="x",
    yref="paper",
    text="Last Actual Month",
    showarrow=False,
    xanchor="left",
    yanchor="bottom",
    yshift=5
)

fig.update_layout(
    height=500,
    xaxis_title="Month",
    yaxis_title="Amount (৳)",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.markdown("---")


# ============================================================
# FORECAST BREAKDOWN TABLE
# ============================================================
st.markdown(
    '<div class="section-header">📋 Forecast Breakdown</div>',
    unsafe_allow_html=True
)

display_forecast = future_df.copy()

display_forecast["Month"] = (
    display_forecast["Month_Start"]
    .dt.strftime("%B %Y")
)

display_forecast["Forecasted Sales"] = (
    display_forecast["Forecasted Sales"]
    .map(lambda value: f"৳{value:,.0f}")
)

display_forecast["Forecasted Profit"] = (
    display_forecast["Forecasted Profit"]
    .map(lambda value: f"৳{value:,.0f}")
)

st.dataframe(
    display_forecast[
        [
            "Month",
            "Forecasted Sales",
            "Forecasted Profit"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


st.markdown("---")


# ============================================================
# PROJECTED PRODUCT DEMAND
# ============================================================
st.markdown(
    '<div class="section-header">📦 Projected Product Demand</div>',
    unsafe_allow_html=True
)

# Determine the first day of the month three months before
# the latest actual month, using a pandas date offset.
recent_cutoff = (
    last_month - pd.DateOffset(months=2)
)

recent_df = filtered[
    filtered["Date"] >= recent_cutoff
].copy()

if recent_df.empty:

    st.info(
        "No recent sales data is available for product demand analysis."
    )

else:

    product_sales = (
        recent_df.dropna(subset=["Product Name"])
        .groupby("Product Name", as_index=False)
        ["Sales Amount"]
        .sum()
    )

    # Top 10 products
    recent_products = (
        product_sales
        .nlargest(10, "Sales Amount")
        .sort_values("Sales Amount", ascending=True)
    )

    # Bottom 10 products
    slow_products = (
        product_sales
        .nsmallest(10, "Sales Amount")
        .sort_values("Sales Amount", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "**🔥 Top 10 Products to Restock (Recent 3 Months)**"
        )

        fig_top = px.bar(
            recent_products,
            x="Sales Amount",
            y="Product Name",
            orientation="h",
            color="Sales Amount",
            color_continuous_scale="Greens",
            text="Sales Amount"
        )

        fig_top.update_traces(
            texttemplate="৳%{text:,.0f}",
            textposition="outside"
        )

        fig_top.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Recent Sales (৳)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    with col2:

        st.markdown("**📉 Slow-Moving Products**")

        fig_slow = px.bar(
            slow_products,
            x="Sales Amount",
            y="Product Name",
            orientation="h",
            color="Sales Amount",
            color_continuous_scale="Reds",
            text="Sales Amount"
        )

        fig_slow.update_traces(
            texttemplate="৳%{text:,.0f}",
            textposition="outside"
        )

        fig_slow.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Recent Sales (৳)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_slow,
            use_container_width=True
        )


st.markdown("---")


# ============================================================
# FORECAST NOTES AND INSIGHTS
# ============================================================
st.markdown(
    '<div class="section-header">💡 Forecast Notes</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

# Historical average
historical_avg = monthly_data["Sales Amount"].mean()

with col1:

    st.markdown(
        f"""
        <div class="insight-card">
            <h4>📊 Historical Average</h4>
            <p>
                Average monthly sales over the historical period:
                <strong>৳{historical_avg:,.0f}</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Sales trend
sales_slope = float(model_sales.coef_[0])

if sales_slope > 0:
    trend_direction = "upward"
elif sales_slope < 0:
    trend_direction = "downward"
else:
    trend_direction = "stable"

with col2:

    st.markdown(
        f"""
        <div class="insight-card">
            <h4>📈 Trend Direction</h4>
            <p>
                Sales are trending <strong>{trend_direction}</strong>,
                with a fitted change of approximately
                <strong>৳{abs(sales_slope):,.0f}</strong> per month.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Model R-squared
r2_score = float(model_sales.score(X, y_sales))

# R-squared can be negative for poor-fitting models.
# Show it as a goodness-of-fit score, not true forecast confidence.
with col3:

    st.markdown(
        f"""
        <div class="insight-card">
            <h4>🎯 Model Fit (R²)</h4>
            <p>
                Historical sales model R²:
                <strong>{r2_score:.1%}</strong>.
                This measures historical fit, not guaranteed forecast accuracy.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# METHODOLOGY NOTE
# ============================================================
st.info(
    "**Forecast methodology:** This dashboard uses simple linear "
    "regression on monthly sales and profit. Forecasts are directional "
    "estimates based on historical trends. The model does not explicitly "
    "account for seasonality, promotions, or future market changes. "
    "For seasonal businesses, consider evaluating seasonal forecasting "
    "models such as SARIMA or Prophet."
)


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="dashboard-footer">
        <p>
            Sales Forecasting | Directional predictions based on
            historical trends
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

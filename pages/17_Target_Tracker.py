import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="Target Tracker", page_icon="🎯", layout="wide")
load_css()

# ============================================================================
# TARGET STORAGE (Local JSON File)
# ============================================================================
TARGET_FILE = "targets.json"

def load_targets():
    """Load targets from JSON file."""
    if os.path.exists(TARGET_FILE):
        try:
            with open(TARGET_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_targets(targets):
    """Save targets to JSON file."""
    with open(TARGET_FILE, "w") as f:
        json.dump(targets, f, indent=4)

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

# Load targets
targets = load_targets()

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🎯 KPI Target vs. Achievement Tracker</h1>
    <p>Set monthly revenue targets and track progress across zones, salespeople, and channels</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Overall Performance", "🏢 Per Zone / Executive", "⚙️ Manage Targets"])

# ============================================================================
# TAB 1: OVERALL PERFORMANCE
# ============================================================================
with tab1:
    # Determine overall target
    overall_target = targets.get("overall", {}).get("monthly_revenue", 0)
    
    # Current month's actual
    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year
    
    current_month_df = df[
        (df['Month Name'] == current_month) & 
        (df['Year'] == current_year)
    ]
    current_actual = current_month_df['Sales Amount'].sum()
    
    # Achievement %
    achievement_pct = (current_actual / overall_target * 100) if overall_target > 0 else 0
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value">৳{overall_target:,.0f}</div>
            <div class="metric-label">Monthly Target</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">৳{current_actual:,.0f}</div>
            <div class="metric-label">Actual ({current_month})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Color based on achievement
        if achievement_pct >= 100:
            color = "#2ecc71"
            status = "✅ Achieved"
        elif achievement_pct >= 75:
            color = "#f39c12"
            status = "⚠️ On Track"
        else:
            color = "#e74c3c"
            status = "❌ Behind"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value" style="color:{color};">{achievement_pct:.1f}%</div>
            <div class="metric-label">{status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        gap = overall_target - current_actual
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{'🎉' if gap <= 0 else '📉'}</div>
            <div class="metric-value" style="color:{'#2ecc71' if gap <= 0 else '#e74c3c'};">
                ৳{abs(gap):,.0f}
            </div>
            <div class="metric-label">{'Surplus' if gap <= 0 else 'Gap to Target'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Progress Bar
    st.markdown('<div class="section-header">📈 Progress Towards Target</div>', unsafe_allow_html=True)
    
    progress_value = min(achievement_pct / 100, 1.0)
    st.progress(progress_value, text=f"{achievement_pct:.1f}% of ৳{overall_target:,.0f} monthly target")
    
    st.markdown("---")
    
    # Monthly Target vs Actual (Full Year)
    st.markdown('<div class="section-header">📅 Monthly Target vs. Actual (Full Year)</div>', unsafe_allow_html=True)
    
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Get monthly actuals for current year
    monthly_actuals = df[df['Year'] == current_year].groupby('Month Name')['Sales Amount'].sum().reset_index()
    monthly_actuals['Month Name'] = pd.Categorical(monthly_actuals['Month Name'], categories=month_order, ordered=True)
    monthly_actuals = monthly_actuals.sort_values('Month Name')
    
    # Get per-month targets (if defined, else use overall)
    per_month_targets = targets.get("monthly_breakdown", {})
    
    monthly_actuals['Target'] = monthly_actuals['Month Name'].astype(str).map(per_month_targets).fillna(overall_target)
    monthly_actuals['Achievement %'] = (monthly_actuals['Sales Amount'] / monthly_actuals['Target'] * 100).round(1)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_actuals['Month Name'], y=monthly_actuals['Sales Amount'],
        name='Actual Sales', marker_color='#667eea'
    ))
    fig.add_trace(go.Scatter(
        x=monthly_actuals['Month Name'], y=monthly_actuals['Target'],
        name='Target', mode='lines+markers',
        line=dict(color='#e74c3c', width=3, dash='dash'), marker=dict(size=10)
    ))
    fig.update_layout(
        height=450, xaxis_title="Month", yaxis_title="Amount (৳)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Achievement table
    st.markdown("**Monthly Breakdown:**")
    display_df = monthly_actuals[['Month Name', 'Target', 'Sales Amount', 'Achievement %']].copy()
    display_df.columns = ['Month', 'Target (৳)', 'Actual (৳)', 'Achievement %']
    display_df['Target (৳)'] = display_df['Target (৳)'].apply(lambda x: f"৳{x:,.0f}")
    display_df['Actual (৳)'] = display_df['Actual (৳)'].apply(lambda x: f"৳{x:,.0f}")
    display_df['Achievement %'] = display_df['Achievement %'].astype(str) + '%'
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 2: PER ZONE / EXECUTIVE
# ============================================================================
with tab2:
    st.markdown('<div class="section-header">🏢 Target Achievement by Dimension</div>', unsafe_allow_html=True)
    
    dimension = st.radio(
        "Select dimension:",
        ["Sales Zone", "Sales by (Executive)", "Sales Channel"],
        horizontal=True
    )
    
    # Time range selector
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    selected_month = st.selectbox("Select Month", options=month_order, index=datetime.now().month - 1)
    selected_year = st.selectbox("Select Year", options=sorted(df['Year'].dropna().unique().astype(int), reverse=True))
    
    # Filter to selected month/year
    period_df = df[(df['Month Name'] == selected_month) & (df['Year'] == selected_year)]
    
    if len(period_df) == 0:
        st.warning("No data for the selected period.")
        st.stop()
    
    # Group by dimension
    actuals = period_df.groupby(dimension)['Sales Amount'].sum().reset_index()
    actuals.columns = [dimension, 'Actual']
    
    # Get targets for this dimension
    dim_targets = targets.get(dimension, {})
    actuals['Target'] = actuals[dimension].map(dim_targets).fillna(0)
    
    if actuals['Target'].sum() == 0:
        st.info(f"⚠️ No targets set for **{dimension}** yet. Go to the 'Manage Targets' tab to define them.")
    else:
        # Calculate achievement
        actuals['Achievement %'] = (actuals['Actual'] / actuals['Target'] * 100).round(1)
        actuals = actuals.sort_values('Achievement %', ascending=True)
        
        # Bar chart comparing actual vs target
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=actuals[dimension], x=actuals['Actual'],
            name='Actual', orientation='h',
            marker_color='#667eea', text=actuals['Actual'].apply(lambda x: f"৳{x:,.0f}"),
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            y=actuals[dimension], x=actuals['Target'],
            name='Target', orientation='h',
            marker_color='#e74c3c', text=actuals['Target'].apply(lambda x: f"৳{x:,.0f}"),
            textposition='outside'
        ))
        fig.update_layout(
            height=max(400, len(actuals) * 40),
            barmode='group',
            xaxis_title="Amount (৳)", yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Achievement % Visualization
        st.markdown("---")
        st.markdown(f"**Achievement % by {dimension}**")
        
        colors = ['#2ecc71' if v >= 100 else '#f39c12' if v >= 75 else '#e74c3c' for v in actuals['Achievement %']]
        
        fig = go.Figure(go.Bar(
            x=actuals['Achievement %'], y=actuals[dimension], orientation='h',
            marker_color=colors,
            text=actuals['Achievement %'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        fig.add_vline(x=100, line_dash="dash", line_color="black", annotation_text="100% Target")
        fig.update_layout(
            height=max(400, len(actuals) * 40),
            xaxis_title="Achievement %", yaxis_title="",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary table
        st.markdown("**Detailed Breakdown:**")
        summary_df = actuals.copy()
        summary_df['Target'] = summary_df['Target'].apply(lambda x: f"৳{x:,.0f}")
        summary_df['Actual'] = summary_df['Actual'].apply(lambda x: f"৳{x:,.0f}")
        summary_df['Achievement %'] = summary_df['Achievement %'].astype(str) + '%'
        summary_df.columns = [dimension, 'Target', 'Actual', 'Achievement %']
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 3: MANAGE TARGETS
# ============================================================================
with tab3:
    st.markdown('<div class="section-header">⚙️ Set & Manage Targets</div>', unsafe_allow_html=True)
    
    st.info("💡 Targets are saved to a local `targets.json` file. They persist between app restarts.")
    
    # Overall target
    st.markdown("### 1️⃣ Overall Monthly Target")
    
    with st.form("overall_target_form"):
        current_overall = targets.get("overall", {}).get("monthly_revenue", 0)
        overall_target = st.number_input(
            "Overall Monthly Revenue Target (৳)",
            min_value=0.0,
            value=float(current_overall),
            step=10000.0
        )
        
        if st.form_submit_button("💾 Save Overall Target", type="primary"):
            targets.setdefault("overall", {})["monthly_revenue"] = overall_target
            save_targets(targets)
            st.success(f"Overall target set to ৳{overall_target:,.0f}")
            st.rerun()
    
    st.markdown("---")
    
    # Per-dimension targets
    st.markdown("### 2️⃣ Set Targets by Dimension")
    
    dimension_choice = st.selectbox(
        "Choose dimension to set targets for:",
        ["Sales Zone", "Sales by (Executive)", "Sales Channel"]
    )
    
    # Get list of unique values for that dimension
    unique_values = sorted(df[dimension_choice].dropna().unique())
    
    existing_dim_targets = targets.get(dimension_choice, {})
    
    with st.form(f"dim_targets_{dimension_choice}"):
        st.markdown(f"**Set monthly targets for each {dimension_choice}:**")
        
        new_targets = {}
        cols = st.columns(2)
        for i, val in enumerate(unique_values):
            with cols[i % 2]:
                current_val = existing_dim_targets.get(val, 0)
                new_targets[val] = st.number_input(
                    f"{val}",
                    min_value=0.0,
                    value=float(current_val),
                    step=5000.0,
                    key=f"target_{dimension_choice}_{val}"
                )
        
        if st.form_submit_button(f"💾 Save {dimension_choice} Targets", type="primary"):
            targets[dimension_choice] = new_targets
            save_targets(targets)
            st.success(f"Targets saved for {dimension_choice}!")
            st.rerun()
    
    st.markdown("---")
    
    # View current targets
    st.markdown("### 3️⃣ Current Targets Overview")
    
    if targets:
        st.markdown(f"**Overall Monthly Target:** ৳{targets.get('overall', {}).get('monthly_revenue', 0):,.0f}")
        
        for dim in ["Sales Zone", "Sales by (Executive)", "Sales Channel"]:
            dim_targets = targets.get(dim, {})
            if dim_targets:
                with st.expander(f"📋 {dim} Targets ({len(dim_targets)} items)"):
                    target_df = pd.DataFrame(list(dim_targets.items()), columns=[dim, 'Target (৳)'])
                    target_df['Target (৳)'] = target_df['Target (৳)'].apply(lambda x: f"৳{x:,.0f}")
                    st.dataframe(target_df, use_container_width=True, hide_index=True)
    else:
        st.info("No targets set yet.")
    
    st.markdown("---")
    
    # Danger zone
    st.markdown("### 🚨 Danger Zone")
    if st.button("🗑️ Clear All Targets", type="secondary"):
        if os.path.exists(TARGET_FILE):
            os.remove(TARGET_FILE)
        st.success("All targets cleared!")
        st.rerun()

st.markdown("""
<div class="dashboard-footer">
    <p>Target Tracker | KPI Goal Management & Achievement Analysis</p>
</div>
""", unsafe_allow_html=True)
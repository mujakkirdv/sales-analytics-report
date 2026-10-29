import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, silhouette_score
)
from sklearn.preprocessing import StandardScaler
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="ML Models", page_icon="🤖", layout="wide")
load_css()

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def get_data():
    return load_sales_data()

raw_df = get_data()
df = raw_df.copy()

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date']).reset_index(drop=True)

for col in ['Sales Amount', 'Purchase Value', 'Invoice Value', 'Discount',
            'Sales VAT', 'Sales Return', 'Credited Amount']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']
df['Market Due'] = df['Invoice Value'] - df['Sales Amount']
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Month_Start'] = df['Date'].dt.to_period('M').dt.to_timestamp()

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🤖 Machine Learning Models</h1>
    <p>5 predictive models trained on your sales data — regression, clustering, classification & anomaly detection</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Linear Regression",
    "🌲 Random Forest",
    "🎯 K-Means Clustering",
    "🔮 Logistic Regression",
    "🚨 Isolation Forest"
])

# ============================================================================
# TAB 1: LINEAR REGRESSION — Monthly Sales Forecast
# ============================================================================
with tab1:
    st.markdown('<div class="section-header">📈 Linear Regression — Sales Forecast</div>', unsafe_allow_html=True)
    st.write("Predicts monthly sales based on historical trend. Best for businesses with stable growth.")

    monthly = df.groupby('Month_Start').agg({'Sales Amount': 'sum'}).reset_index().sort_values('Month_Start')
    monthly['Index'] = np.arange(len(monthly))

    if len(monthly) < 3:
        st.warning("Need at least 3 months of data.")
    else:
        X = monthly[['Index']].values
        y = monthly['Sales Amount'].values

        # Train/test split (80/20)
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        model = LinearRegression().fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred) if len(y_test) > 1 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("MAE", f"৳{mae:,.0f}")
        col2.metric("RMSE", f"৳{rmse:,.0f}")
        col3.metric("R² Score", f"{r2:.3f}")
        col4.metric("Trend / Month", f"৳{model.coef_[0]:,.0f}")

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly['Month_Start'][:split], y=y_train,
                                  mode='lines+markers', name='Training Data', line=dict(color='#667eea')))
        fig.add_trace(go.Scatter(x=monthly['Month_Start'][split:], y=y_test,
                                  mode='lines+markers', name='Actual (Test)', line=dict(color='#2ecc71')))
        fig.add_trace(go.Scatter(x=monthly['Month_Start'][split:], y=y_pred,
                                  mode='lines+markers', name='Predicted',
                                  line=dict(color='#e74c3c', dash='dash')))
        fig.update_layout(height=400, title="Linear Regression Fit",
                           xaxis_title="Month", yaxis_title="Sales (৳)",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        # Equation
        st.info(f"**Model Equation:** Sales = ৳{model.intercept_:,.0f} + ৳{model.coef_[0]:,.0f} × Month_Index")

# ============================================================================
# TAB 2: RANDOM FOREST — Monthly Sales Forecast
# ============================================================================
with tab2:
    st.markdown('<div class="section-header">🌲 Random Forest Regressor</div>', unsafe_allow_html=True)
    st.write("Non-linear ensemble model. Captures complex patterns — better than linear if your sales are volatile.")

    if len(monthly) < 6:
        st.warning("Need at least 6 months of data for Random Forest.")
    else:
        # Build features
        monthly['Lag1'] = monthly['Sales Amount'].shift(1)
        monthly['Lag2'] = monthly['Sales Amount'].shift(2)
        monthly['Rolling3'] = monthly['Sales Amount'].rolling(3).mean()
        rf_df = monthly.dropna().reset_index(drop=True)

        features = ['Lag1', 'Lag2', 'Rolling3']
        X = rf_df[features].values
        y = rf_df['Sales Amount'].values

        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred) if len(y_test) > 1 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("MAE", f"৳{mae:,.0f}")
        col2.metric("RMSE", f"৳{rmse:,.0f}")
        col3.metric("R² Score", f"{r2:.3f}")

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=rf_df['Month_Start'][split:], y=y_test,
                                  mode='lines+markers', name='Actual', line=dict(color='#2ecc71')))
        fig.add_trace(go.Scatter(x=rf_df['Month_Start'][split:], y=y_pred,
                                  mode='lines+markers', name='Predicted',
                                  line=dict(color='#e74c3c', dash='dash')))
        fig.update_layout(height=400, title="Random Forest Predictions",
                           xaxis_title="Month", yaxis_title="Sales (৳)")
        st.plotly_chart(fig, use_container_width=True)

        # Feature importance
        importance = pd.DataFrame({
            'Feature': features,
            'Importance': rf.feature_importances_
        }).sort_values('Importance', ascending=True)
        fig = px.bar(importance, x='Importance', y='Feature', orientation='h',
                     color='Importance', color_continuous_scale='Viridis',
                     text='Importance', title="Feature Importance")
        fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 3: K-MEANS — Customer Clustering (RFM)
# ============================================================================
with tab3:
    st.markdown('<div class="section-header">🎯 K-Means Customer Clustering (RFM)</div>', unsafe_allow_html=True)
    st.write("Groups customers into clusters based on Recency, Frequency, and Monetary value.")

    n_clusters = st.slider("Number of Clusters (K)", min_value=2, max_value=8, value=4, step=1)

    # Build RFM
    ref_date = df['Date'].max()
    rfm = df.groupby('Customer Name').agg({
        'Date': lambda x: (ref_date - x.max()).days,
        'Invoice No': 'nunique',
        'Sales Amount': 'sum'
    }).reset_index()
    rfm.columns = ['Customer', 'Recency', 'Frequency', 'Monetary']

    if len(rfm) < n_clusters:
        st.warning(f"Need at least {n_clusters} customers.")
    else:
        # Scale
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])

        # Fit K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        rfm['Cluster'] = kmeans.fit_predict(X_scaled)
        sil_score = silhouette_score(X_scaled, rfm['Cluster'])

        col1, col2, col3 = st.columns(3)
        col1.metric("Clusters", n_clusters)
        col2.metric("Customers", len(rfm))
        col3.metric("Silhouette Score", f"{sil_score:.3f}")

        # Cluster summary
        summary = rfm.groupby('Cluster').agg({
            'Customer': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean'
        }).reset_index()
        summary.columns = ['Cluster', 'Customers', 'Avg Recency', 'Avg Frequency', 'Avg Monetary']
        summary['Avg Recency'] = summary['Avg Recency'].round(0).astype(int)
        summary['Avg Frequency'] = summary['Avg Frequency'].round(1)
        summary['Avg Monetary'] = summary['Avg Monetary'].round(0).astype(int)

        st.markdown("**Cluster Profiles:**")
        display_summary = summary.copy()
        display_summary['Avg Monetary'] = display_summary['Avg Monetary'].apply(lambda x: f"৳{x:,.0f}")
        st.dataframe(display_summary, use_container_width=True, hide_index=True)

        # 3D scatter
        fig = px.scatter_3d(
            rfm, x='Recency', y='Frequency', z='Monetary',
            color=rfm['Cluster'].astype(str),
            hover_name='Customer',
            title=f"Customer Clusters (K={n_clusters})",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 4: LOGISTIC REGRESSION — High-Value Product Classifier
# ============================================================================
with tab4:
    st.markdown('<div class="section-header">🔮 Logistic Regression — High-Value Product Classifier</div>', unsafe_allow_html=True)
    st.write("Predicts whether a product is **high-value** (top 30% by revenue) or not, based on its sales patterns.")

    # Build product features
    prod = df.groupby('Product Name').agg({
        'Sales Amount': 'sum',
        'Purchase Value': 'sum',
        'Discount': 'mean',
        'Invoice No': 'nunique'
    }).reset_index()
    prod.columns = ['Product', 'Revenue', 'Cost', 'Avg_Discount', 'Orders']
    prod['Profit'] = prod['Revenue'] - prod['Cost']
    prod['Margin'] = np.where(prod['Revenue'] > 0, prod['Profit'] / prod['Revenue'], 0)

    if len(prod) < 10:
        st.warning("Need at least 10 products.")
    else:
        # Binary label: top 30% by revenue
        threshold = prod['Revenue'].quantile(0.7)
        prod['Is_High_Value'] = (prod['Revenue'] >= threshold).astype(int)

        features = ['Cost', 'Avg_Discount', 'Orders', 'Margin']
        X = prod[features].values
        y = prod['Is_High_Value'].values

        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        logreg = LogisticRegression(max_iter=1000, random_state=42)
        logreg.fit(X_train, y_train)
        y_pred = logreg.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Accuracy", f"{acc:.1%}")
        col2.metric("Precision", f"{prec:.1%}")
        col3.metric("Recall", f"{rec:.1%}")
        col4.metric("F1 Score", f"{f1:.1%}")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        fig = px.imshow(
            cm, text_auto=True,
            labels=dict(x="Predicted", y="Actual", color="Count"),
            x=['Low Value', 'High Value'],
            y=['Low Value', 'High Value'],
            color_continuous_scale='Blues',
            title="Confusion Matrix"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Coefficients
        coef_df = pd.DataFrame({
            'Feature': features,
            'Coefficient': logreg.coef_[0]
        }).sort_values('Coefficient', ascending=True)
        fig = px.bar(coef_df, x='Coefficient', y='Feature', orientation='h',
                     color='Coefficient', color_continuous_scale='RdBu',
                     title="Feature Impact on 'High-Value' Prediction")
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Threshold: Products with revenue ≥ ৳{threshold:,.0f} are classified as High Value.")

# ============================================================================
# TAB 5: ISOLATION FOREST — Anomaly Detection
# ============================================================================
with tab5:
    st.markdown('<div class="section-header">🚨 Isolation Forest — Anomaly Detection</div>', unsafe_allow_html=True)
    st.write("Unsupervised model that flags **unusual transactions** (extreme amounts, rare patterns, etc.) without any labels.")

    contamination = st.slider(
        "Expected Anomaly Rate (%)",
        min_value=1, max_value=20, value=5, step=1,
        help="Approximate percentage of transactions you expect to be anomalies"
    )

    # Build per-invoice features
    inv = df.groupby('Invoice No').agg({
        'Sales Amount': 'sum',
        'Discount': 'sum',
        'Sales Return': 'sum',
        'Market Due': 'sum',
        'Product Name': 'count'
    }).reset_index()
    inv.columns = ['Invoice No', 'Sales', 'Discount', 'Returns', 'Due', 'Items']

    features = ['Sales', 'Discount', 'Returns', 'Due', 'Items']
    X = inv[features].values

    iso = IsolationForest(contamination=contamination / 100, random_state=42)
    inv['Anomaly'] = iso.fit_predict(X)  # -1 = anomaly, 1 = normal
    inv['Anomaly_Label'] = np.where(inv['Anomaly'] == -1, 'Anomaly', 'Normal')
    inv['Anomaly_Score'] = -iso.score_samples(X)  # higher = more anomalous

    n_anomalies = (inv['Anomaly'] == -1).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Invoices", len(inv))
    col2.metric("Anomalies Detected", n_anomalies)
    col3.metric("Anomaly Rate", f"{n_anomalies / len(inv) * 100:.1f}%")
    col4.metric("Contamination Setting", f"{contamination}%")

    # Scatter: Sales vs Discount
    fig = px.scatter(
        inv, x='Sales', y='Discount',
        color='Anomaly_Label',
        color_discrete_map={'Anomaly': '#e74c3c', 'Normal': '#667eea'},
        hover_data=['Invoice No', 'Returns', 'Due', 'Items'],
        title="Anomaly Map — Sales vs Discount",
        labels={'Sales': 'Sales (৳)', 'Discount': 'Discount (৳)'}
    )
    fig.update_traces(marker=dict(size=8, opacity=0.7))
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Top anomalies table
    st.markdown("**Top 10 Anomalies Detected:**")
    top_anomalies = inv[inv['Anomaly'] == -1].nlargest(10, 'Anomaly_Score')[
        ['Invoice No', 'Sales', 'Discount', 'Returns', 'Due', 'Items', 'Anomaly_Score']
    ].copy()
    for c in ['Sales', 'Discount', 'Returns', 'Due']:
        top_anomalies[c] = top_anomalies[c].apply(lambda x: f"৳{x:,.0f}")
    top_anomalies['Anomaly_Score'] = top_anomalies['Anomaly_Score'].round(3)
    st.dataframe(top_anomalies, use_container_width=True, hide_index=True)

    # Download
    csv = inv[inv['Anomaly'] == -1].to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download All Anomalies (CSV)",
        data=csv,
        file_name="anomalies_detected.csv",
        mime="text/csv",
        type="primary"
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class="dashboard-footer">
    <p>Machine Learning Models | 5 predictive models trained on your sales data</p>
</div>
""", unsafe_allow_html=True)
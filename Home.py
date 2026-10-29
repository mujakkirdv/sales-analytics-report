import streamlit as st
import os
from datetime import datetime
from utils.qr_generator import generate_qr

# ============================================================================
# CONFIGURATION — EDIT THESE TO MATCH YOUR PROJECT
# ============================================================================
GITHUB_REPO_URL = "https://github.com/mujakkirdv/sales-analytics-project"
EDA_NOTEBOOK_URL = "https://github.com/mujakkirdv/sales-analytics-project/blob/main/notebooks/eda.ipynb"
LINKEDIN_URL = "https://linkedin.com/in/mujakkir-dv"
EMAIL = "mujakkir.dv@gmail.com"
AUTHOR_NAME = "Mujakir Ahmad"

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Sales Analytics and Automated Report Web Application for Business",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = os.path.join("assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">📊</div>
        <div class="sidebar-logo-title">Sales Analytics</div>
        <div class="sidebar-logo-subtitle">Enterprise Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("👈 Use the sidebar to navigate to the Dashboard and other pages.")
    st.markdown("---")
    st.markdown("**🔗 Project Links**")
    st.markdown(f"[📂 GitHub Repo]({GITHUB_REPO_URL})")
    st.markdown(f"[📓 EDA Notebook]({EDA_NOTEBOOK_URL})")
    st.markdown("---")
    st.caption(f"Built by **{AUTHOR_NAME}** · {datetime.now().year}")

# ============================================================================
# HERO HEADER
# ============================================================================
st.markdown(f"""
<div class="main-header">
    <h1>🏢 Sales Analytics and Automated Report Web Application for Business</h1>
    <p>Real-time insights for data-driven decision making | {datetime.now().strftime('%Y-%m-%d')}</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SHARE & QR CODE SECTION
# ============================================================================
st.markdown('<div class="section-header">🔗 Share This Project</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 📱 Scan · Share · Explore
    This project is open source and available on GitHub. Share it with your team, 
    add it to your portfolio, or fork it to build your own version.
    """)
    
    # Buttons row
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        st.link_button(
            "📂 View on GitHub",
            GITHUB_REPO_URL,
            use_container_width=True,
            type="primary"
        )
    
    with btn_col2:
        st.link_button(
            "📓 Open EDA Notebook",
            EDA_NOTEBOOK_URL,
            use_container_width=True
        )
    
    with btn_col3:
        st.link_button(
            "💼 LinkedIn",
            LINKEDIN_URL,
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Quick stats / highlights
    st.markdown("""
    **📊 Project Highlights:**
    - **20+ analytical pages** covering sales, customers, products, and operations
    - **PostgreSQL backend** with live SQL queries
    - **Interactive charts** powered by Plotly
    - **AI-powered chatbot** for natural-language queries
    - **PDF report generator** for executive summaries
    - **RFM segmentation**, **forecasting**, and **anomaly detection**
    """)

with col2:
    st.markdown("**📱 Scan to Open the Repo**")
    try:
        qr_buffer = generate_qr(GITHUB_REPO_URL, size=8)
        st.image(qr_buffer, caption="Scan with your phone camera", width=280)
    except Exception as e:
        st.warning(f"QR generation failed: {e}")
    
    st.caption("Point your phone camera at the QR code to open the GitHub repository.")

st.markdown("---")

# ============================================================================
# OVERVIEW
# ============================================================================
st.markdown('<div class="section-header">🚀 Platform Overview</div>', unsafe_allow_html=True)

st.markdown("""
This platform provides comprehensive analytics for your sales data. It connects directly 
to your **PostgreSQL** database and turns raw transactions into **actionable insights** 
across every dimension of your business.
""")

# ============================================================================
# FEATURE CARDS
# ============================================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 1rem; 
                border-top: 4px solid #667eea; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                height: 100%;">
        <div style="font-size: 2.5rem;">📈</div>
        <h3 style="color: #2c3e50; margin-top: 0.5rem;">Sales Analytics</h3>
        <p style="color: #7f8c8d; font-size: 0.9rem;">
            Track revenue, profit margins, and trends across zones, channels, and time periods.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 1rem; 
                border-top: 4px solid #2ecc71; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                height: 100%;">
        <div style="font-size: 2.5rem;">👥</div>
        <h3 style="color: #2c3e50; margin-top: 0.5rem;">Customer Intelligence</h3>
        <p style="color: #7f8c8d; font-size: 0.9rem;">
            360° customer portfolios, RFM segmentation, and behavioral insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 1rem; 
                border-top: 4px solid #f39c12; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                height: 100%;">
        <div style="font-size: 2.5rem;">🤖</div>
        <h3 style="color: #2c3e50; margin-top: 0.5rem;">AI-Powered</h3>
        <p style="color: #7f8c8d; font-size: 0.9rem;">
            Chatbot, forecasting, and anomaly detection for predictive insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(" ")

# ============================================================================
# NAVIGATION GUIDE
# ============================================================================
st.markdown('<div class="section-header">🧭 Navigation Guide</div>', unsafe_allow_html=True)

st.markdown("""
**Use the sidebar to explore these pages:**

| Page | What You'll Find |
|---|---|
| 📊 **Dashboard** | High-level KPIs, revenue trends, top zones |
| 💼 **Executive Dashboard** | Profitability, market due, channel performance |
| 📋 **Profit & Loss** | Formal P&L statement with COGS, VAT, returns |
| 🏅 **Executive Portfolio** | Individual salesperson performance |
| 🎯 **Target Tracker** | Monthly KPI goals vs. actuals |
| 👥 **Customer Analysis** | Demographics, top customers, spend patterns |
| 👤 **Customer Dashboard** | Individual customer history (360°) |
| 🎁 **Customer Loyalty (RFM)** | Champions, At Risk, Lost segments |
| 🧠 **Customer Behavior** | Payment methods, banks, channels |
| 🛍️ **Product Analysis** | Best sellers, category revenue |
| 🔄 **Return Analysis** | Return rates, refund impact |
| 🗺️ **Zone Analysis** | Geographic performance with heatmaps |
| 🗓️ **Time Intelligence** | Seasonality, day-of-week, YoY |
| 🔮 **Sales Forecasting** | Predictive revenue (1–12 months) |
| 📦 **Inventory & Stock Risk** | Stock-out and overstock detection |
| 🔔 **Alerts & Anomalies** | Automated unusual-activity detection |
| 🌊 **Sales Funnel (Sankey)** | Revenue flow from channel → customer |
| 🔎 **Invoice Search** | Fast transaction lookup |
| 🛠️ **Data Explorer** | View, edit, insert, delete records |
| 📄 **PDF Report Generator** | Multi-page business reports |
| 🤖 **AI Chatbot** | Ask questions in plain English |
""")

st.markdown("---")

# ============================================================================
# TECH STACK
# ============================================================================
st.markdown('<div class="section-header">🛠️ Built With</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

techs = [
    ("🐍", "Python", "3.10+"),
    ("🎈", "Streamlit", "1.30+"),
    ("🐘", "PostgreSQL", "14+"),
    ("📊", "Plotly", "5.17+"),
    ("🤖", "Scikit-learn", "1.3+"),
]

for col, (icon, name, version) in zip([col1, col2, col3, col4, col5], techs):
    with col:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; 
                    background: #f8f9fa; border-radius: 0.5rem;">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="font-weight: bold; color: #2c3e50; margin-top: 0.5rem;">{name}</div>
            <div style="font-size: 0.75rem; color: #7f8c8d;">{version}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# AUTHOR / CONTACT
# ============================================================================
st.markdown('<div class="section-header">👤 About the Author</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"""
    **{AUTHOR_NAME}**  
    Data Analytics & Business Intelligence
    
    This project was built as a comprehensive demonstration of end-to-end analytics 
    development — from **database design** through **machine learning** to 
    **production-grade UI**. It showcases practical skills in:
    
    - **Data Engineering**: PostgreSQL schema design and SQLAlchemy ORM
    - **Analytics**: Pandas transformations and statistical analysis
    - **Visualization**: Plotly interactive charts and Matplotlib PDF exports
    - **Machine Learning**: Linear regression forecasting and RFM clustering
    - **UI/UX**: Streamlit multi-page apps with custom CSS theming
    - **Business Acumen**: P&L statements, KPIs, and target tracking
    """)

with col2:
    st.markdown("**📬 Connect**")
    st.link_button("📧 Email", f"mailto:{EMAIL}", use_container_width=True)
    st.link_button("💼 LinkedIn", LINKEDIN_URL, use_container_width=True)
    st.link_button("🐙 GitHub", GITHUB_REPO_URL, use_container_width=True)
    st.link_button("📓 EDA Notebook", EDA_NOTEBOOK_URL, use_container_width=True)

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown(f"""
<div style="text-align: center; padding: 2rem; margin-top: 2rem;
            border-top: 1px solid #e0e0e0; color: #7f8c8d; font-size: 0.85rem;">
    <p style="margin: 0;">
        <strong>Sales Analytics and Automated Report Web Application for Business</strong> · Built with ❤️ and ☕ by {AUTHOR_NAME}
    </p>
    <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem;">
        © {datetime.now().year} · Open Source under MIT License
    </p>
</div>
""", unsafe_allow_html=True)
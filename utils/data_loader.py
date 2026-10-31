import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from the root .env file (local dev)
load_dotenv()


def _get_secret(key, default=None):
    """
    Get a credential from Streamlit Secrets (cloud) OR .env (local).

    Priority:
        1. Streamlit Cloud Secrets (st.secrets)
        2. Local .env / environment variables
        3. Provided default
    """
    # Try Streamlit Cloud secrets first
    try:
        return st.secrets[key]
    except (FileNotFoundError, KeyError):
        pass

    # Fall back to environment variables (.env)
    return os.getenv(key, default)


@st.cache_resource
def get_db_engine():
    """Creates and caches the database engine."""
    user     = _get_secret("DB_USER")
    password = _get_secret("DB_PASSWORD")
    host     = _get_secret("DB_HOST")
    port     = _get_secret("DB_PORT", "5432")   # safe default
    dbname   = _get_secret("DB_NAME")

    # Validate required credentials before building the connection
    missing = []
    for name, value in {
        "DB_USER": user,
        "DB_PASSWORD": password,
        "DB_HOST": host,
        "DB_NAME": dbname,
    }.items():
        if not value:
            missing.append(name)

    if missing:
        raise ValueError(
            f"Missing required database credentials: {missing}. "
            f"Locally: add them to your .env file. "
            f"On Streamlit Cloud: add them to Settings → Secrets."
        )

    # Ensure port is a valid string (avoid "None" being passed)
    port = str(port) if port else "5432"

    conn_str = (
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    )
    return create_engine(conn_str)


@st.cache_data(ttl=600)
def load_sales_data(query=None):
    """
    Fetches data from PostgreSQL and caches it.
    Also ensures numeric columns are properly typed.
    """
    engine = get_db_engine()
    table_name = _get_secret("DB_TABLE", "sales")

    with st.spinner("Loading data from PostgreSQL..."):
        if query:
            df = pd.read_sql(query, engine)
        else:
            df = pd.read_sql_table(table_name, engine)

    # --- DATA CLEANING ---
    numeric_cols = [
        "Purchase Value", "Invoice Value", "Discount",
        "Sales Amount", "Sales VAT", "Sales Return", "Credited Amount",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("৳", "", regex=False)
                .str.replace("$", "", regex=False),
                errors="coerce",
            ).fillna(0)

    return df


def load_css():
    """
    Loads the custom CSS file.
    NOTE: Do NOT add @st.cache_resource here — it breaks CSS on multi-page apps.
    """
    css_file = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")

    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found at {css_file}")

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def _get_secret(key, default=None):
    """Read from Streamlit Secrets (cloud) then .env (local)."""
    try:
        return st.secrets[key]
    except (FileNotFoundError, KeyError):
        return os.getenv(key, default)


@st.cache_resource
def get_db_engine():
    user     = _get_secret("DB_USER")
    password = _get_secret("DB_PASSWORD")
    host     = _get_secret("DB_HOST")
    port     = _get_secret("DB_PORT", "5432")
    dbname   = _get_secret("DB_NAME")

    # Validate
    missing = [
        name for name, value in {
            "DB_USER": user,
            "DB_PASSWORD": password,
            "DB_HOST": host,
            "DB_NAME": dbname,
        }.items() if not value
    ]
    if missing:
        raise ValueError(
            f"Missing database credentials: {missing}. "
            f"Add them to your local .env OR to Streamlit Cloud → Settings → Secrets."
        )

    port = str(port) if port else "5432"
    conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(conn_str)


@st.cache_data(ttl=600)
def load_sales_data(query=None):
    engine = get_db_engine()
    schema = _get_secret("DB_SCHEMA", "public")
    table  = _get_secret("DB_TABLE", "sales")
    fallback = _get_secret("FALLBACK_TABLE", "pos_sales_data")

    with st.spinner("Loading data from PostgreSQL..."):
        if query:
            df = pd.read_sql(query, engine)
        else:
            try:
                df = pd.read_sql_table(table, engine, schema=schema)
            except Exception as e:
                # Try fallback table if the primary is not found
                st.warning(f"⚠️ Table '{table}' not found, trying '{fallback}'...")
                try:
                    df = pd.read_sql_table(fallback, engine, schema=schema)
                except Exception:
                    raise e  # show original error if fallback also fails

    # Numeric safety
    for col in [
        "Purchase Value", "Invoice Value", "Discount",
        "Sales Amount", "Sales VAT", "Sales Return", "Credited Amount",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("৳", "", regex=False)
                .str.replace("$", "", regex=False),
                errors="coerce",
            ).fillna(0)

    return df


def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found at {css_file}")

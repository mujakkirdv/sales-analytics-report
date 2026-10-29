import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from the root .env file
load_dotenv()

@st.cache_resource
def get_db_engine():
    """Creates and caches the database engine."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    
    # Postgres connection string format (FORCED to use psycopg2 driver)
    conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(conn_str)

@st.cache_data(ttl=600)  # Caches data for 10 minutes
def load_sales_data(query=None):
    """
    Fetches data from PostgreSQL and caches it.
    Also ensures numeric columns are properly typed.
    """
    engine = get_db_engine()
    table_name = os.getenv("DB_TABLE")
    
    with st.spinner("Loading data from PostgreSQL..."):
        if query:
            df = pd.read_sql(query, engine)
        else:
            df = pd.read_sql_table(table_name, engine)
    
    # --- DATA CLEANING ---
    # Make sure your numeric columns are actual numbers, not strings
    numeric_cols = [
        'Purchase Value', 'Invoice Value', 'Discount', 
        'Sales Amount', 'Sales VAT', 'Sales Return', 'Credited Amount'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            # Remove commas/currency symbols, then convert to float
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',', '').str.replace('৳', '').str.replace('$', ''),
                errors='coerce'
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
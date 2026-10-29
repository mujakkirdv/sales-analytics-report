import streamlit as st
import pandas as pd
from utils.data_loader import load_sales_data, get_db_engine, load_css
from sqlalchemy import text

# Page config
st.set_page_config(
    page_title="Data Explorer",
    page_icon="🔍",
    layout="wide"
)

# Load CSS
load_css()

st.markdown("""
<div class="main-header">
    <h1>🔍 Data Explorer (CRUD)</h1>
    <p>View, Insert, Update, and Delete records directly from the database</p>
</div>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
engine = get_db_engine()

# Define the exact columns from your dataset
COLUMNS = [
    'Date', 'Transaction ID', 'Invoice No', 'Invoice type', 'Customer Name',
    'Customer ID', 'Customer Type', 'Barcode', 'Product Name',
    'Product Category', 'Sales by', 'Sales ID', 'Sales Zone', 'Zone Code',
    'Sales Channel', 'Purchase Value', 'Invoice Value', 'Discount',
    'Sales Amount', 'Sales VAT', 'Sales Return', 'Credited Amount',
    'Payment Method', 'Bank Name', 'Remarks', 'Month Name'
]

# Numeric columns that need float formatting
NUMERIC_COLS = [
    'Purchase Value', 'Invoice Value', 'Discount', 'Sales Amount', 
    'Sales VAT', 'Sales Return', 'Credited Amount'
]

# ============================================================================
# TABS FOR CRUD OPERATIONS
# ============================================================================
tab1, tab2, tab3 = st.tabs(["📖 View & Edit / Delete", "➕ Insert New Record", "🛠️ Bulk Actions"])

# ============================================================================
# TAB 1: VIEW, EDIT, DELETE
# ============================================================================
with tab1:
    st.subheader("Search & Filter Data")
    
    # Load current data
    df = load_sales_data()
    
    # Simple search box to filter by Customer Name or Invoice No
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("Search by Customer Name or Invoice No", "")
    with col2:
        # Pagination limit
        limit = st.number_input("Rows to display", min_value=10, max_value=1000, value=50, step=10)
    
    # Apply search filter
    if search_query:
        filtered_df = df[
            df['Customer Name'].astype(str).str.contains(search_query, case=False, na=False) |
            df['Invoice No'].astype(str).str.contains(search_query, case=False, na=False)
        ]
    else:
        filtered_df = df
        
    display_df = filtered_df.head(limit).copy()

    st.info("💡 **How to use:** Click on a cell to edit. Select a row on the left to delete. Click 'Save Changes' when done.")
    
    # Use st.data_editor for interactive editing
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic", # Allows deleting rows
        use_container_width=True,
        hide_index=True,
        key="data_editor"
    )
    
    if st.button("💾 Save Changes to Database", type="primary"):
        try:
            # Process edits row by row
            for index, row in edited_df.iterrows():
                # Find the matching row in the original df using a unique ID (Transaction ID)
                # NOTE: Ensure 'Transaction ID' is unique in your dataset!
                trans_id = row['Transaction ID']
                original_row = df[df['Transaction ID'] == trans_id]
                
                if original_row.empty:
                    continue # Row was deleted or not found
                
                # Check for changes
                changes = {}
                for col in COLUMNS:
                    # Handle NaNs
                    orig_val = original_row.iloc[0][col] if pd.notna(original_row.iloc[0][col]) else None
                    new_val = row[col] if pd.notna(row[col]) else None
                    
                    if str(orig_val) != str(new_val):
                        changes[col] = new_val
                
                # If there are changes, run an UPDATE query
                if changes:
                    set_clause = ", ".join([f'"{k}" = :{k}' for k in changes.keys()])
                    query = text(f'UPDATE sales SET {set_clause} WHERE "Transaction ID" = :trans_id')
                    
                    # Add trans_id to parameters
                    changes['trans_id'] = trans_id
                    
                    with engine.connect() as conn:
                        conn.execute(query, changes)
                        conn.commit()
            
            st.success("Database updated successfully!")
            st.cache_data.clear() # Clear cache so new data loads
            st.rerun()
            
        except Exception as e:
            st.error(f"Error updating database: {e}")

    # --- DELETE ROW FUNCTIONALITY ---
    st.markdown("---")
    st.subheader("🗑️ Delete a Record")
    delete_id = st.text_input("Enter Transaction ID to delete:")
    
    if st.button("Delete Record", type="primary"):
        if delete_id:
            try:
                with engine.connect() as conn:
                    # Check if exists first
                    check = conn.execute(text('SELECT * FROM sales WHERE "Transaction ID" = :id'), {"id": delete_id}).fetchone()
                    if check:
                        conn.execute(text('DELETE FROM sales WHERE "Transaction ID" = :id'), {"id": delete_id})
                        conn.commit()
                        st.success(f"Record {delete_id} deleted successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.warning("Transaction ID not found.")
            except Exception as e:
                st.error(f"Error deleting record: {e}")
        else:
            st.warning("Please enter a Transaction ID.")

# ============================================================================
# TAB 2: INSERT NEW RECORD
# ============================================================================
with tab2:
    st.subheader("Add a Single New Record")
    
    with st.form("insert_form"):
        st.write("Fill in the details below to insert a new row.")
        
        # Create columns for the form layout
        form_cols = st.columns(3)
        
        form_data = {}
        for i, col in enumerate(COLUMNS):
            with form_cols[i % 3]:
                # Provide default values for numeric fields
                if col in NUMERIC_COLS:
                    form_data[col] = st.number_input(col, value=0.0, step=0.01)
                else:
                    form_data[col] = st.text_input(col, value="")
        
        submit_btn = st.form_submit_button("Insert Record")
        
        if submit_btn:
            try:
                # Build dynamic INSERT query
                cols_str = ", ".join([f'"{k}"' for k in COLUMNS])
                vals_str = ", ".join([f':{k.replace(" ", "_")}' for k in COLUMNS])
                
                query = text(f'INSERT INTO sales ({cols_str}) VALUES ({vals_str})')
                
                # Format params (replace spaces in column names for the params dict)
                params = {k.replace(" ", "_"): v for k, v in form_data.items()}
                
                with engine.connect() as conn:
                    conn.execute(query, params)
                    conn.commit()
                    
                st.success("Record inserted successfully!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error inserting record: {e}")

# ============================================================================
# TAB 3: BULK ACTIONS
# ============================================================================
with tab3:
    st.subheader("Bulk Upload via CSV")
    st.info("Upload a CSV file with the exact same column headers as the database to append rows.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file)
            
            # Basic validation: Check if all required columns are present
            missing_cols = [col for col in COLUMNS if col not in new_data.columns]
            
            if missing_cols:
                st.error(f"Missing columns in CSV: {missing_cols}")
            else:
                # Keep only the columns that exist in the DB
                new_data = new_data[COLUMNS]
                
                st.write("Preview of data to be inserted:")
                st.dataframe(new_data.head())
                
                if st.button("Append to Database", type="primary"):
                    with st.spinner("Inserting data..."):
                        # Use pandas to_sql with 'append' mode
                        new_data.to_sql('sales', engine, if_exists='append', index=False)
                    st.success(f"Successfully inserted {len(new_data)} rows!")
                    st.cache_data.clear()
                    st.rerun()
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
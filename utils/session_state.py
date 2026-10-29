"""
Session state management for global filters
"""

import streamlit as st

def initialize_session_state(df):
    """Initialize all session state variables"""
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        
        # Date range filter
        st.session_state.date_start = df['orderdate'].min().date()
        st.session_state.date_end = df['orderdate'].max().date()
        
        # Multi-select filters
        st.session_state.selected_regions = ['All']
        st.session_state.selected_products = ['All']
        st.session_state.selected_customer_types = ['All']
        
        # Numeric filters
        st.session_state.discount_min = 0
        st.session_state.discount_max = 50
        
        # Boolean filters
        st.session_state.show_only_returned = False
        
        # Store original and filtered data
        st.session_state.original_df = df.copy()
        st.session_state.filtered_df = df.copy()
        
        # Get unique values for filters
        st.session_state.region_options = ['All'] + sorted(df['region'].unique().tolist())
        st.session_state.product_options = ['All'] + sorted(df['product'].unique().tolist())
        st.session_state.customer_options = ['All'] + sorted(df['customertype'].unique().tolist())
    
    return st.session_state

def apply_filters():
    """Apply all filters to the dataframe"""
    
    df = st.session_state.original_df.copy()
    
    # Date filter
    df = df[
        (df['orderdate'].dt.date >= st.session_state.date_start) &
        (df['orderdate'].dt.date <= st.session_state.date_end)
    ]
    
    # Region filter
    if st.session_state.selected_regions and 'All' not in st.session_state.selected_regions:
        df = df[df['region'].isin(st.session_state.selected_regions)]
    
    # Product filter
    if st.session_state.selected_products and 'All' not in st.session_state.selected_products:
        df = df[df['product'].isin(st.session_state.selected_products)]
    
    # Customer type filter
    if st.session_state.selected_customer_types and 'All' not in st.session_state.selected_customer_types:
        df = df[df['customertype'].isin(st.session_state.selected_customer_types)]
    
    # Discount filter
    df = df[
        (df['discount'] * 100 >= st.session_state.discount_min) &
        (df['discount'] * 100 <= st.session_state.discount_max)
    ]
    
    # Returned filter
    if st.session_state.show_only_returned:
        df = df[df['returned'] == True]
    
    st.session_state.filtered_df = df
    return df

def reset_filters(df):
    """Reset all filters to default values"""
    
    st.session_state.date_start = df['orderdate'].min().date()
    st.session_state.date_end = df['orderdate'].max().date()
    st.session_state.selected_regions = ['All']
    st.session_state.selected_products = ['All']
    st.session_state.selected_customer_types = ['All']
    st.session_state.discount_min = 0
    st.session_state.discount_max = 50
    st.session_state.show_only_returned = False
    
    return apply_filters()
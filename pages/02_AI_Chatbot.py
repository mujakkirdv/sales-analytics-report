import streamlit as st
import pandas as pd
import numpy as np
import re
from utils.data_loader import load_sales_data, load_css

# Page config
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")
load_css()

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def get_data():
    return load_sales_data()

raw_df = get_data()
df = raw_df.copy()

# Clean
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date']).reset_index(drop=True)
for col in ['Sales Amount', 'Purchase Value', 'Invoice Value', 'Discount',
            'Sales VAT', 'Sales Return', 'Credited Amount']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']
df['Market Due'] = df['Invoice Value'] - df['Sales Amount']
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Month_Name'] = df['Date'].dt.strftime('%B')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def fmt_money(val):
    """Format a number as currency."""
    return f"৳{val:,.0f}"


def filter_by_period(query_lower, data):
    """Filter data based on time period keywords in the question."""
    current_year = data['Year'].max()
    
    # Year detection (e.g., "2024", "this year", "last year")
    year_match = re.search(r'\b(20\d{2})\b', query_lower)
    if year_match:
        year = int(year_match.group(1))
        return data[data['Year'] == year], f"in {year}"
    
    if "this year" in query_lower or "current year" in query_lower:
        return data[data['Year'] == current_year], f"in {current_year}"
    if "last year" in query_lower or "previous year" in query_lower:
        return data[data['Year'] == current_year - 1], f"in {current_year - 1}"
    
    # Month detection
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    for i, month in enumerate(months, start=1):
        if month in query_lower:
            return data[data['Month'] == i], f"in {month.capitalize()}"
    
    if "this month" in query_lower:
        latest_month = data['Month'].max()
        return data[data['Month'] == latest_month], f"this month"
    
    return data, "overall"


# ============================================================================
# CORE INTELLIGENCE ENGINE
# ============================================================================

def answer_question(query, data):
    """Parse a natural language question and return a rich answer."""
    q = query.lower().strip()
    filtered, period = filter_by_period(q, data)

    if len(filtered) == 0:
        return {
            "text": f"⚠️ No data found {period}. Try a different period.",
            "dataframe": None,
            "chart": None
        }

    # --- REVENUE / SALES ---
    if any(k in q for k in ['revenue', 'sales', 'total sales', 'how much did we sell', 'turnover']):
        total = filtered['Sales Amount'].sum()
        orders = filtered['Invoice No'].nunique()
        avg = total / orders if orders > 0 else 0
        return {
            "text": f"💰 **Total Revenue {period}:** {fmt_money(total)}\n\n"
                    f"📦 **Orders:** {orders:,}\n\n"
                    f"📊 **Average Order Value:** {fmt_money(avg)}",
            "dataframe": None,
            "chart": None
        }

    # --- PROFIT ---
    if any(k in q for k in ['profit', 'margin', 'earnings']):
        total_sales = filtered['Sales Amount'].sum()
        total_profit = filtered['Gross Profit'].sum()
        margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
        return {
            "text": f"📈 **Gross Profit {period}:** {fmt_money(total_profit)}\n\n"
                    f"💵 **Total Revenue:** {fmt_money(total_sales)}\n\n"
                    f"📊 **Profit Margin:** {margin:.1f}%",
            "dataframe": None,
            "chart": None
        }

    # --- TOP CUSTOMERS ---
    if any(k in q for k in ['top customer', 'best customer', 'who buys the most', 'top buyer']):
        # Find number (default 5)
        n_match = re.search(r'top (\d+)', q)
        n = int(n_match.group(1)) if n_match else 5
        top = filtered.groupby('Customer Name')['Sales Amount'].sum().nlargest(n).reset_index()
        top.columns = ['Customer', 'Revenue']
        top['Revenue'] = top['Revenue'].apply(fmt_money)
        return {
            "text": f"🏆 **Top {n} Customers {period}:**",
            "dataframe": top,
            "chart": None
        }

    # --- TOP PRODUCTS ---
    if any(k in q for k in ['top product', 'best seller', 'best selling', 'top selling']):
        n_match = re.search(r'top (\d+)', q)
        n = int(n_match.group(1)) if n_match else 5
        top = filtered.groupby('Product Name')['Sales Amount'].sum().nlargest(n).reset_index()
        top.columns = ['Product', 'Revenue']
        top['Revenue'] = top['Revenue'].apply(fmt_money)
        return {
            "text": f"🛍️ **Top {n} Products {period}:**",
            "dataframe": top,
            "chart": None
        }

    # --- ZONE PERFORMANCE ---
    if any(k in q for k in ['top zone', 'best zone', 'which zone', 'zone perform', 'best performing zone']):
        top_zone = filtered.groupby('Sales Zone')['Sales Amount'].sum().sort_values(ascending=False)
        if len(top_zone) > 0:
            return {
                "text": f"📍 **Zone Performance {period}:**\n\n"
                        f"🥇 **Best zone:** {top_zone.index[0]} — {fmt_money(top_zone.iloc[0])}\n\n"
                        f"🥈 **Second:** {top_zone.index[1]} — {fmt_money(top_zone.iloc[1])}" if len(top_zone) > 1 else "",
                "dataframe": top_zone.reset_index().rename(columns={
                    'Sales Zone': 'Zone', 'Sales Amount': 'Revenue'
                }).assign(Revenue=lambda x: x['Revenue'].apply(fmt_money)),
                "chart": None
            }

    # --- RETURNS ---
    if any(k in q for k in ['return', 'refund', 'returned']):
        total_returns = filtered['Sales Return'].sum()
        return_count = len(filtered[filtered['Sales Return'] > 0])
        return_rate = (total_returns / filtered['Sales Amount'].sum() * 100) if filtered['Sales Amount'].sum() > 0 else 0
        return {
            "text": f"🔄 **Returns Analysis {period}:**\n\n"
                    f"💸 **Total Return Value:** {fmt_money(total_returns)}\n\n"
                    f"📊 **Return Rate:** {return_rate:.2f}%\n\n"
                    f"🧾 **Returned Transactions:** {return_count:,}",
            "dataframe": None,
            "chart": None
        }

    # --- MARKET DUE ---
    if any(k in q for k in ['due', 'owed', 'outstanding', 'unpaid', 'market due']):
        total_due = filtered['Market Due'].sum()
        customers_with_due = filtered[filtered['Market Due'] > 0]['Customer Name'].nunique()
        return {
            "text": f"⚠️ **Market Due Analysis {period}:**\n\n"
                    f"💰 **Total Outstanding:** {fmt_money(total_due)}\n\n"
                    f"👥 **Customers with Due:** {customers_with_due:,}",
            "dataframe": None,
            "chart": None
        }

    # --- SALES BY EXECUTIVE ---
    if any(k in q for k in ['sales by', 'salesperson', 'sales exec', 'executive', 'rep', 'top rep', 'who sold']):
        top_rep = filtered.groupby('Sales by')['Sales Amount'].sum().sort_values(ascending=False).reset_index()
        top_rep.columns = ['Salesperson', 'Revenue']
        top_rep['Revenue'] = top_rep['Revenue'].apply(fmt_money)
        return {
            "text": f"🏅 **Salesperson Performance {period}:**",
            "dataframe": top_rep,
            "chart": None
        }

    # --- INVOICES / ORDERS ---
    if any(k in q for k in ['how many orders', 'how many invoice', 'number of orders', 'total orders']):
        orders = filtered['Invoice No'].nunique()
        return {
            "text": f"🧾 **Total Orders {period}:** {orders:,}",
            "dataframe": None,
            "chart": None
        }

    # --- CUSTOMER COUNT ---
    if any(k in q for k in ['how many customers', 'number of customers', 'total customers', 'unique customers']):
        customers = filtered['Customer Name'].nunique()
        return {
            "text": f"👥 **Unique Customers {period}:** {customers:,}",
            "dataframe": None,
            "chart": None
        }

    # --- PRODUCT COUNT ---
    if any(k in q for k in ['how many products', 'number of products', 'unique products']):
        products = filtered['Product Name'].nunique()
        return {
            "text": f"🛍️ **Unique Products {period}:** {products:,}",
            "dataframe": None,
            "chart": None
        }

    # --- COMPARISON ---
    if any(k in q for k in ['compare', 'versus', 'vs']):
        if 'this year' in q and 'last year' in q:
            this_year = data[data['Year'] == data['Year'].max()]['Sales Amount'].sum()
            last_year = data[data['Year'] == data['Year'].max() - 1]['Sales Amount'].sum()
            growth = ((this_year - last_year) / last_year * 100) if last_year > 0 else 0
            return {
                "text": f"📊 **Year-over-Year Comparison:**\n\n"
                        f"**This Year:** {fmt_money(this_year)}\n\n"
                        f"**Last Year:** {fmt_money(last_year)}\n\n"
                        f"**Growth:** {growth:+.1f}%",
                "dataframe": None,
                "chart": None
            }

    # --- HELP / GREETING ---
    if any(k in q for k in ['help', 'what can you do', 'hello', 'hi', 'hey', 'commands']):
        return {
            "text": """👋 **Hello! I'm your AI Sales Assistant.**

I can answer questions about your sales data. Here are some examples:

📊 **Sales Metrics:**
- "What was my total revenue?"
- "How many orders did we have this year?"
- "Show me the profit margin"

🏆 **Rankings:**
- "Who are my top 5 customers?"
- "What are my top 10 products?"
- "Which zone performed best?"
- "Show me the top salesperson"

🔄 **Returns & Dues:**
- "How many returns did we have?"
- "What is my market due?"

📅 **Time-based:**
- "What were the sales in January?"
- "Compare this year vs last year"

Try typing one of these!""",
            "dataframe": None,
            "chart": None
        }

    # --- FALLBACK ---
    return {
        "text": f"🤔 I'm not sure how to answer that.\n\n"
                f"I can help with: **revenue, profit, orders, customers, products, zones, "
                f"returns, dues, and salespeople.**\n\n"
                f"Try asking something like *'What was my total revenue this year?'* or "
                f"type **help** to see all examples.",
        "dataframe": None,
        "chart": None
    }


# ============================================================================
# UI
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Sales Assistant</h1>
    <p>Ask natural-language questions about your sales data — instant insights, no SQL needed</p>
</div>
""", unsafe_allow_html=True)

# Sidebar info
with st.sidebar:
    st.markdown('<div class="filter-label">💡 SUGGESTED QUESTIONS</div>', unsafe_allow_html=True)
    suggestions = [
        "What was my total revenue?",
        "Who are my top 5 customers?",
        "Top 10 products",
        "What is my profit?",
        "Which zone performed best?",
        "How many returns did we have?",
        "What is my market due?",
        "Top salesperson",
        "Show sales for January",
        "Compare this year vs last year",
    ]
    for s in suggestions:
        if st.button(s, key=f"sug_{s}", use_container_width=True):
            st.session_state.pending_question = s
            st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI Sales Assistant. Ask me anything about your sales data. Try **'what was my total revenue?'** or **'help'** to see examples."}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "dataframe" in msg and msg["dataframe"] is not None:
            st.dataframe(msg["dataframe"], use_container_width=True, hide_index=True)

# Handle pending question from sidebar
if "pending_question" in st.session_state and st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None
else:
    user_input = st.chat_input("Ask a question about your data...")

# Process user input
if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = answer_question(user_input, df)
        st.markdown(answer["text"])
        if answer["dataframe"] is not None:
            st.dataframe(answer["dataframe"], use_container_width=True, hide_index=True)
    
    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer["text"],
        "dataframe": answer["dataframe"]
    })

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI Sales Assistant. Ask me anything about your sales data."}
    ]
    st.rerun()

st.markdown("""
<div class="dashboard-footer">
    <p>AI Sales Assistant | Natural language queries — no SQL required</p>
</div>
""", unsafe_allow_html=True)
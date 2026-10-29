import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime
from utils.data_loader import load_sales_data, load_css

# ReportLab
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Matplotlib for chart rendering
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="PDF Report Generator", page_icon="📄", layout="wide")
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
df['Sales Amount'] = pd.to_numeric(df['Sales Amount'], errors='coerce').fillna(0)
df['Purchase Value'] = pd.to_numeric(df['Purchase Value'], errors='coerce').fillna(0)
df['Gross Profit'] = df['Sales Amount'] - df['Purchase Value']
df['Market Due'] = df['Invoice Value'] - df['Sales Amount']

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>📄 PDF Report Generator</h1>
    <p>Generate a professional, multi-page PDF report with charts, KPIs, and insights</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR — REPORT CONFIGURATION
# ============================================================================
with st.sidebar:
    st.markdown('<div class="filter-label">⚙️ REPORT CONFIGURATION</div>', unsafe_allow_html=True)
    
    report_title = st.text_input("Report Title", value="Sales Performance Report")
    company_name = st.text_input("Company Name", value="NU Sales Analytics")
    prepared_by = st.text_input("Prepared By", value="Executive Team")
    
    st.markdown("---")
    st.markdown('<div class="filter-label">📅 REPORTING PERIOD</div>', unsafe_allow_html=True)
    
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.date_input(
        "Select Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    st.markdown("---")
    st.markdown('<div class="filter-label">📑 SECTIONS TO INCLUDE</div>', unsafe_allow_html=True)
    
    include_kpis = st.checkbox("Executive Summary (KPIs)", value=True)
    include_zone = st.checkbox("Zone Performance", value=True)
    include_products = st.checkbox("Top Products", value=True)
    include_customers = st.checkbox("Customer Analysis", value=True)
    include_trend = st.checkbox("Monthly Trend", value=True)
    include_returns = st.checkbox("Returns Analysis", value=True)
    include_executives = st.checkbox("Executive Performance", value=True)

# Apply period filter
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    (df['Date'].dt.date >= start_date) &
    (df['Date'].dt.date <= end_date)
].copy()

if len(filtered) == 0:
    st.warning("⚠️ No data matches the selected period.")
    st.stop()

# ============================================================================
# PREVIEW OF REPORT DATA
# ============================================================================
st.markdown('<div class="section-header">📊 Report Preview</div>', unsafe_allow_html=True)

st.info(f"📅 **Reporting Period:** {start_date.strftime('%d %b %Y')} → {end_date.strftime('%d %b %Y')} ({len(filtered):,} records)")

col1, col2, col3, col4 = st.columns(4)
total_sales = filtered['Sales Amount'].sum()
total_profit = filtered['Gross Profit'].sum()
total_orders = filtered['Invoice No'].nunique()
total_due = filtered['Market Due'].sum()

with col1:
    st.metric("Total Revenue", f"৳{total_sales:,.0f}")
with col2:
    st.metric("Gross Profit", f"৳{total_profit:,.0f}")
with col3:
    st.metric("Orders", f"{total_orders:,}")
with col4:
    st.metric("Outstanding Due", f"৳{total_due:,.0f}")

st.markdown("---")

# ============================================================================
# CHART GENERATION HELPERS (Matplotlib → PNG bytes)
# ============================================================================

def fig_to_bytes(fig):
    """Convert matplotlib figure to PNG bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def make_bar_chart(data_series, title, color='#667eea', horizontal=False):
    """Generate a bar chart."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    if horizontal:
        ax.barh(data_series.index, data_series.values, color=color)
        ax.set_xlabel('Revenue (৳)')
    else:
        ax.bar(data_series.index, data_series.values, color=color)
        ax.set_ylabel('Revenue (৳)')
        plt.xticks(rotation=45, ha='right')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_bytes(fig)

def make_line_chart(x, y, title, color='#667eea'):
    """Generate a line chart."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(x, y, marker='o', color=color, linewidth=2, markersize=6)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_ylabel('Amount (৳)')
    plt.xticks(rotation=45, ha='right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return fig_to_bytes(fig)

def make_pie_chart(data_series, title):
    """Generate a pie chart."""
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(data_series.values, labels=data_series.index, autopct='%1.1f%%', startangle=90)
    ax.set_title(title, fontsize=11, fontweight='bold')
    plt.tight_layout()
    return fig_to_bytes(fig)

# ============================================================================
# PDF BUILDER
# ============================================================================
def build_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6, alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=20, alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        'Section', parent=styles['Heading1'],
        fontSize=15, textColor=colors.HexColor('#667eea'),
        spaceBefore=15, spaceAfter=10, borderPadding=4
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#2c3e50')
    )
    
    story = []

    # ---- COVER PAGE ----
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph(report_title, title_style))
    story.append(Paragraph(f"{company_name}", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Cover info table
    cover_info = [
        ["Prepared By:", prepared_by],
        ["Reporting Period:", f"{start_date.strftime('%d %B %Y')} – {end_date.strftime('%d %B %Y')}"],
        ["Generated On:", datetime.now().strftime('%d %B %Y %H:%M')],
        ["Total Records:", f"{len(filtered):,}"],
    ]
    cover_table = Table(cover_info, colWidths=[2*inch, 4*inch])
    cover_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#667eea')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cover_table)
    story.append(PageBreak())

    # ---- SECTION 1: EXECUTIVE SUMMARY ----
    if include_kpis:
        story.append(Paragraph("1. Executive Summary", section_style))
        story.append(Paragraph("Key performance indicators for the reporting period.", body_style))
        story.append(Spacer(1, 0.2*inch))

        kpi_data = [
            ["Metric", "Value"],
            ["Total Revenue", f"৳{total_sales:,.0f}"],
            ["Gross Profit", f"৳{total_profit:,.0f}"],
            ["Gross Margin %", f"{(total_profit/total_sales*100):.1f}%" if total_sales else "0%"],
            ["Total Orders", f"{total_orders:,}"],
            ["Avg Order Value", f"৳{(total_sales/total_orders):,.0f}" if total_orders else "0"],
            ["Unique Customers", f"{filtered['Customer Name'].nunique():,}"],
            ["Unique Products", f"{filtered['Product Name'].nunique():,}"],
            ["Outstanding Market Due", f"৳{total_due:,.0f}"],
            ["Total Returns", f"৳{filtered['Sales Return'].sum():,.0f}"],
        ]
        
        kpi_table = Table(kpi_data, colWidths=[3*inch, 3*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f6f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(kpi_table)
        story.append(PageBreak())

    # ---- SECTION 2: ZONE PERFORMANCE ----
    if include_zone:
        story.append(Paragraph("2. Zone Performance", section_style))
        zone_data = filtered.groupby('Sales Zone')['Sales Amount'].sum().sort_values(ascending=False)
        if len(zone_data) > 0:
            img_bytes = make_bar_chart(zone_data, "Revenue by Sales Zone", color='#667eea', horizontal=True)
            story.append(Image(img_bytes, width=6.5*inch, height=3.2*inch))
            story.append(Spacer(1, 0.15*inch))

            zone_table_data = [["Zone", "Revenue (৳)", "% of Total"]]
            for zone, val in zone_data.items():
                pct = (val / total_sales * 100) if total_sales else 0
                zone_table_data.append([str(zone), f"৳{val:,.0f}", f"{pct:.1f}%"])

            zone_table = Table(zone_table_data, colWidths=[2*inch, 2*inch, 1.5*inch])
            zone_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(zone_table)
        story.append(PageBreak())

    # ---- SECTION 3: TOP PRODUCTS ----
    if include_products:
        story.append(Paragraph("3. Top 10 Products", section_style))
        top_products = filtered.groupby('Product Name')['Sales Amount'].sum().nlargest(10).sort_values()
        if len(top_products) > 0:
            img_bytes = make_bar_chart(top_products, "Top 10 Products by Revenue", color='#2ecc71', horizontal=True)
            story.append(Image(img_bytes, width=6.5*inch, height=3.2*inch))
            story.append(Spacer(1, 0.15*inch))

            prod_table_data = [["Product", "Revenue (৳)"]]
            for prod, val in top_products.sort_values(ascending=False).items():
                prod_table_data.append([str(prod)[:40], f"৳{val:,.0f}"])

            prod_table = Table(prod_table_data, colWidths=[4.5*inch, 1.5*inch])
            prod_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(prod_table)
        story.append(PageBreak())

    # ---- SECTION 4: MONTHLY TREND ----
    if include_trend:
        story.append(Paragraph("4. Monthly Sales Trend", section_style))
        monthly = filtered.groupby(filtered['Date'].dt.strftime('%Y-%m'))['Sales Amount'].sum()
        if len(monthly) > 1:
            img_bytes = make_line_chart(monthly.index, monthly.values, "Monthly Revenue Trend", color='#e74c3c')
            story.append(Image(img_bytes, width=6.5*inch, height=3.2*inch))
            story.append(Spacer(1, 0.15*inch))

            # Insight text
            if len(monthly) >= 2:
                first_val = monthly.iloc[0]
                last_val = monthly.iloc[-1]
                change_pct = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0
                trend_word = "grown" if change_pct > 0 else "declined"
                story.append(Paragraph(
                    f"Revenue has <b>{trend_word} {abs(change_pct):.1f}%</b> from the first "
                    f"month ({monthly.index[0]}) to the last month ({monthly.index[-1]}).",
                    body_style
                ))
        story.append(PageBreak())

    # ---- SECTION 5: CUSTOMER ANALYSIS ----
    if include_customers:
        story.append(Paragraph("5. Customer Analysis", section_style))
        
        cust_data = filtered.groupby('Customer Name')['Sales Amount'].sum().nlargest(10).sort_values()
        if len(cust_data) > 0:
            img_bytes = make_bar_chart(cust_data, "Top 10 Customers by Revenue", color='#f39c12', horizontal=True)
            story.append(Image(img_bytes, width=6.5*inch, height=3.2*inch))
            story.append(Spacer(1, 0.15*inch))

        # Customer type pie chart
        cust_type = filtered.groupby('Customer Type')['Sales Amount'].sum()
        if len(cust_type) > 1:
            img_bytes = make_pie_chart(cust_type, "Revenue by Customer Type")
            story.append(Image(img_bytes, width=4*inch, height=3.2*inch))
        story.append(PageBreak())

    # ---- SECTION 6: RETURNS ----
    if include_returns:
        story.append(Paragraph("6. Returns & Refunds Analysis", section_style))
        
        total_sales_val = filtered['Sales Amount'].sum()
        total_returns_val = filtered['Sales Return'].sum()
        return_rate = (total_returns_val / total_sales_val * 100) if total_sales_val > 0 else 0

        returns_table_data = [
            ["Metric", "Value"],
            ["Total Sales", f"৳{total_sales_val:,.0f}"],
            ["Total Returns", f"৳{total_returns_val:,.0f}"],
            ["Return Rate", f"{return_rate:.2f}%"],
            ["Total Credited Amount", f"৳{filtered['Credited Amount'].sum():,.0f}"],
        ]
        returns_table = Table(returns_table_data, colWidths=[3*inch, 3*inch])
        returns_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(returns_table)
        story.append(Spacer(1, 0.2*inch))

        # Top returned products
        top_returns = filtered.groupby('Product Name')['Sales Return'].sum().nlargest(10).sort_values()
        if len(top_returns) > 0 and top_returns.sum() > 0:
            img_bytes = make_bar_chart(top_returns, "Top 10 Products by Return Value", color='#e74c3c', horizontal=True)
            story.append(Image(img_bytes, width=6.5*inch, height=3.2*inch))
        story.append(PageBreak())

    # ---- SECTION 7: EXECUTIVE PERFORMANCE ----
    if include_executives:
        story.append(Paragraph("7. Sales Executive Performance", section_style))
        
        exec_perf = filtered.groupby('Sales by').agg({
            'Sales Amount': 'sum',
            'Gross Profit': 'sum',
            'Invoice No': 'nunique'
        }).reset_index().sort_values('Sales Amount', ascending=False).head(10)

        if len(exec_perf) > 0:
            exec_table_data = [["Executive", "Revenue (৳)", "Profit (৳)", "Orders", "Margin %"]]
            for _, row in exec_perf.iterrows():
                margin = (row['Gross Profit'] / row['Sales Amount'] * 100) if row['Sales Amount'] > 0 else 0
                exec_table_data.append([
                    str(row['Sales by'])[:25],
                    f"৳{row['Sales Amount']:,.0f}",
                    f"৳{row['Gross Profit']:,.0f}",
                    f"{row['Invoice No']:,}",
                    f"{margin:.1f}%"
                ])

            exec_table = Table(exec_table_data, colWidths=[1.5*inch, 1.3*inch, 1.3*inch, 0.8*inch, 0.9*inch])
            exec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(exec_table)

    # ---- FOOTER ON LAST PAGE ----
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"<i>Report generated on {datetime.now().strftime('%d %B %Y at %H:%M')} | "
        f"Confidential – For internal use only</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                       textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# GENERATE REPORT BUTTON
# ============================================================================
st.markdown('<div class="section-header">📄 Generate Report</div>', unsafe_allow_html=True)

st.write(f"**Report will include:**")
selected_sections = []
if include_kpis: selected_sections.append("✅ Executive Summary")
if include_zone: selected_sections.append("✅ Zone Performance")
if include_products: selected_sections.append("✅ Top Products")
if include_trend: selected_sections.append("✅ Monthly Trend")
if include_customers: selected_sections.append("✅ Customer Analysis")
if include_returns: selected_sections.append("✅ Returns Analysis")
if include_executives: selected_sections.append("✅ Executive Performance")

for s in selected_sections:
    st.write(s)

st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                pdf_buffer = build_pdf()
                st.success("✅ Report generated successfully!")
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"sales_report_{start_date}_{end_date}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

with col2:
    st.markdown("""
    **💡 Tips:**
    - Adjust the date range to focus on a specific period
    - Toggle sections on/off to customize the report
    - The report is generated **on-demand** — it doesn't run every page load
    - Charts are rendered with matplotlib for crisp PDF output
    """)

st.markdown("""
<div class="dashboard-footer">
    <p>PDF Report Generator | Professional multi-page business reports</p>
</div>
""", unsafe_allow_html=True)
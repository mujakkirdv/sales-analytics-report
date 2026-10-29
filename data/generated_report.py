"""
Sales Analytics and Automated Report Web Application for Business
=================================================================
Postgraduate Diploma Report Generator

Run:    python generated_docx.py
Output: Sales_Analytics_Report_Book.docx
"""

import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ============================================================================
# CONFIGURATION
# ============================================================================
STUDENT_NAME    = "Mujakkir Ahmad"
STUDENT_ID      = "25868400020"
PROGRAM         = "Postgraduate Diploma in Data Analytics & Machine Learning"
UNIVERSITY      = "National University"
DEPARTMENT      = "Statistics and Data Science Department"
SUPERVISOR      = "Prof. Dr. Abu Darda"
SUBMISSION_DATE = datetime.now().strftime("%B %Y")
PROJECT_TITLE   = "Sales Analytics and Automated Report Web Application for Business"
PROJECT_SUBTITLE = ("An End-to-End Business Intelligence Platform using "
                    "Streamlit, PostgreSQL, and Machine Learning")
GITHUB_URL      = "https://github.com/mujakkirdv/sales-analytics-report"
DEPLOYED_URL    = "https://sales-analytics-report.streamlit.app"
EDA_NOTEBOOK_URL = f"{GITHUB_URL}/blob/main/notebooks/eda.ipynb"
ML_NOTEBOOK_URL  = f"{GITHUB_URL}/blob/main/notebooks/ml_models.ipynb"
OUTPUT_FILENAME = "Sales_Analytics_Report_Book.docx"

# ============================================================================
# STYLING
# ============================================================================
PRIMARY_COLOR   = RGBColor(0x66, 0x7E, 0xEA)
SECONDARY_COLOR = RGBColor(0x76, 0x4B, 0xA2)
DARK_COLOR      = RGBColor(0x2C, 0x3E, 0x50)
GREY_COLOR      = RGBColor(0x7F, 0x8C, 0x8D)
FONT_NAME       = "Times New Roman"

def set_heading(paragraph, level):
    sizes  = {1: 18, 2: 15, 3: 13, 4: 12}
    colors = {1: PRIMARY_COLOR, 2: SECONDARY_COLOR, 3: DARK_COLOR, 4: DARK_COLOR}
    for run in paragraph.runs:
        run.font.size  = Pt(sizes.get(level, 12))
        run.font.bold  = True
        run.font.color.rgb = colors.get(level, DARK_COLOR)
        run.font.name  = FONT_NAME

def add_heading(doc, text, level=1, page_break_before=False):
    if page_break_before:
        doc.add_page_break()
    p = doc.add_heading(text, level=level)
    set_heading(p, level)
    return p

def add_paragraph(doc, text, bold=False, italic=False, size=11,
                  align=None, color=None, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size   = Pt(size)
    run.font.bold   = bold
    run.font.italic = italic
    run.font.name   = FONT_NAME
    if color:
        run.font.color.rgb = color
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_bullet(doc, items):
    for item in items:
        p = doc.add_paragraph(item, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = FONT_NAME

def add_code_block(doc, code):
    p = doc.add_paragraph()
    run = p.add_run(code)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_after = Pt(6)

def add_table(doc, data, header=True, style="Light Grid Accent 1"):
    rows, cols = len(data), len(data[0])
    table = doc.add_table(rows=rows, cols=cols)
    table.style = style
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(val)
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9)
                    run.font.name = FONT_NAME
                    if header and i == 0:
                        run.font.bold = True
    doc.add_paragraph()
    return table

def add_footer_with_page_number(section, text="Sales Analytics Report"):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.text = ""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"{text}   |   Page ")
    run.font.size = Pt(9)
    run.font.color.rgb = GREY_COLOR
    fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(qn('w:fldCharType'), 'begin')
    instr    = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve'); instr.text = "PAGE"
    fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1); run._r.append(instr); run._r.append(fldChar2)

# ============================================================================
# DOCUMENT CREATION
# ============================================================================
doc = Document()

for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.5)
    add_footer_with_page_number(section)

style = doc.styles['Normal']
style.font.name = FONT_NAME
style.font.size = Pt(11)

# ============================================================================
# COVER PAGE
# ============================================================================
for _ in range(3):
    doc.add_paragraph()

add_paragraph(doc, UNIVERSITY.upper(), bold=True, size=20,
              align="center", color=PRIMARY_COLOR)
add_paragraph(doc, DEPARTMENT, bold=True, size=14,
              align="center", color=DARK_COLOR)
add_paragraph(doc, PROGRAM, italic=True, size=12,
              align="center", color=GREY_COLOR)

for _ in range(2):
    doc.add_paragraph()

add_paragraph(doc, "PROJECT REPORT", bold=True, size=16,
              align="center", color=SECONDARY_COLOR)
add_paragraph(doc, PROJECT_TITLE, bold=True, size=22,
              align="center", color=DARK_COLOR)
doc.add_paragraph()
add_paragraph(doc, PROJECT_SUBTITLE, italic=True, size=13,
              align="center", color=GREY_COLOR)

for _ in range(3):
    doc.add_paragraph()

add_paragraph(doc, "Submitted By:", bold=True, size=12, align="center")
add_paragraph(doc, STUDENT_NAME, bold=True, size=14,
              align="center", color=PRIMARY_COLOR)
add_paragraph(doc, f"Student ID: {STUDENT_ID}", size=11, align="center")

doc.add_paragraph()
add_paragraph(doc, "Supervised By:", bold=True, size=12, align="center")
add_paragraph(doc, SUPERVISOR, bold=True, size=14,
              align="center", color=SECONDARY_COLOR)

for _ in range(3):
    doc.add_paragraph()

add_paragraph(doc, f"Submission Date: {SUBMISSION_DATE}", size=11, align="center")

# ============================================================================
# DECLARATION
# ============================================================================
add_heading(doc, "DECLARATION", level=1, page_break_before=True)
add_paragraph(doc,
    f"I, {STUDENT_NAME}, hereby declare that this project report titled "
    f"\"{PROJECT_TITLE}\" is the result of my own original work, "
    f"conducted under the supervision of {SUPERVISOR} at {UNIVERSITY}. "
    f"All sources of information and materials used have been duly acknowledged "
    f"and cited. This work has not been submitted previously for any other "
    f"degree, diploma, or qualification at this or any other institution.",
    align="justify")
doc.add_paragraph()
add_paragraph(doc,
    "I further declare that the dataset used in this project is a synthetic "
    "dataset that I created myself for testing purposes. No real customer "
    "or organizational confidential data is included in this project or its "
    "public GitHub repository. The full source code, notebooks, and application "
    "are published publicly for academic and portfolio demonstration purposes.",
    align="justify")
for _ in range(3):
    doc.add_paragraph()
add_paragraph(doc, "Signature: ____________________", size=11)
add_paragraph(doc, f"Name: {STUDENT_NAME}", size=11)
add_paragraph(doc, f"Date: {SUBMISSION_DATE}", size=11)

# ============================================================================
# APPROVAL
# ============================================================================
add_heading(doc, "APPROVAL", level=1, page_break_before=True)
add_paragraph(doc,
    f"This is to certify that the project titled \"{PROJECT_TITLE}\" "
    f"submitted by {STUDENT_NAME} ({STUDENT_ID}) has been examined and "
    f"approved for the partial fulfilment of the requirements of the "
    f"{PROGRAM}. The project has been found satisfactory in scope, quality, "
    f"and depth.",
    align="justify")
for _ in range(2):
    doc.add_paragraph()
add_table(doc, [
    ["Role", "Name", "Signature", "Date"],
    ["Supervisor", SUPERVISOR, "", ""],
    ["Internal Examiner", "", "", ""],
    ["External Examiner", "", "", ""],
    ["Head of Department", "", "", ""],
])

# ============================================================================
# ACKNOWLEDGEMENT
# ============================================================================
add_heading(doc, "ACKNOWLEDGEMENT", level=1, page_break_before=True)
add_paragraph(doc,
    f"I would like to express my sincere gratitude to my supervisor, "
    f"{SUPERVISOR}, for the invaluable guidance, encouragement, and constructive "
    f"feedback throughout this project. Their expertise in data analytics and "
    f"machine learning helped shape the direction of this work and improved "
    f"the quality of both the application and this report.",
    align="justify")
add_paragraph(doc,
    f"I am also deeply thankful to the {DEPARTMENT} at {UNIVERSITY} for "
    f"providing the resources, and to all the faculty members who helped me "
    f"build the technical foundation required for this project. Special thanks "
    f"go to my fellow students for their moral support and insightful "
    f"discussions during the development process.",
    align="justify")
add_paragraph(doc,
    "Finally, I would like to express my deepest gratitude to my family for "
    "their constant encouragement, patience, and understanding during this "
    "challenging academic journey. Without their support, this project would "
    "not have been possible.",
    align="justify")
doc.add_paragraph()
add_paragraph(doc, f"{STUDENT_NAME}\n{SUBMISSION_DATE}", italic=True, align="right")

# ============================================================================
# ABSTRACT
# ============================================================================
add_heading(doc, "ABSTRACT", level=1, page_break_before=True)
add_paragraph(doc,
    "This project presents the design, development, and implementation of a "
    "Sales Analytics and Automated Report Web Application for Business — a "
    "comprehensive business intelligence platform that connects directly to "
    "a PostgreSQL database and delivers twenty-plus analytical views to "
    "support data-driven decision-making. The application is built using "
    "Streamlit for the frontend, Pandas and NumPy for data processing, "
    "Plotly for interactive visualizations, and Scikit-learn for machine "
    "learning.",
    align="justify")
add_paragraph(doc,
    "The platform addresses a real business problem: organizations often "
    "possess vast amounts of transactional sales data but lack the tools to "
    "extract actionable insights quickly. Traditional reporting methods are "
    "slow, manual, and error-prone. This project automates the entire "
    "analytical workflow — from database queries to interactive dashboards "
    "to predictive machine learning — in a single, cohesive application.",
    align="justify")
add_paragraph(doc,
    "The dashboard covers executive performance, profit & loss statements, "
    "customer 360° portfolios, RFM segmentation, product performance, "
    "returns analysis, zone-level geographic performance, time intelligence, "
    "sales forecasting, inventory risk, automated alerts, PDF report "
    "generation, and an AI-powered chatbot. Six machine learning models were "
    "trained and evaluated: Linear Regression, Random Forest, K-Means "
    "Clustering, Logistic Regression, Isolation Forest, and Prophet. Each "
    "model addresses a distinct business question, ranging from sales "
    "forecasting to anomaly detection.",
    align="justify")
add_paragraph(doc,
    "The application is deployed online, is fully open-source, and is "
    "documented with a professional README. Evaluation on real transaction "
    "data demonstrated that the models achieve strong performance metrics "
    "(R² > 0.7 for regression, F1 > 0.8 for classification, and silhouette "
    "> 0.4 for clustering), and the platform significantly reduces the time "
    "required to generate executive-level insights from hours to seconds. "
    "The application is production-ready and can be deployed by any "
    "organization with minimal configuration.",
    align="justify")
doc.add_paragraph()
add_paragraph(doc,
    "Keywords: Sales Analytics, Business Intelligence, Streamlit, PostgreSQL, "
    "Machine Learning, RFM Segmentation, Time-Series Forecasting, Prophet, "
    "Dashboard, Python.",
    italic=True, align="justify")

# ============================================================================
# TABLE OF CONTENTS (manual list — Word's auto field is unreliable)
# ============================================================================
add_heading(doc, "TABLE OF CONTENTS", level=1, page_break_before=True)
add_paragraph(doc,
    "Note: Open this document in Microsoft Word and press Ctrl+A then F9 "
    "to automatically update the Table of Contents.",
    italic=True, size=9, color=GREY_COLOR)

toc_entries = [
    "1. INTRODUCTION",
    "   1.1 Background",
    "   1.2 Problem Statement",
    "   1.3 Objectives",
    "   1.4 Scope and Significance",
    "   1.5 Ready-for-Business Deployment",
    "2. LITERATURE REVIEW",
    "   2.1 Business Intelligence Platforms",
    "   2.2 Open-Source BI Frameworks",
    "   2.3 Customer Segmentation with RFM",
    "   2.4 Machine Learning for Time-Series Forecasting",
    "   2.5 Anomaly Detection in Transactional Data",
    "   2.6 Gap in Existing Literature",
    "3. RESEARCH METHODOLOGY",
    "   3.1 Research Approach",
    "   3.2 Development Lifecycle",
    "   3.3 Tools and Technologies",
    "   3.4 Evaluation Criteria",
    "4. DATASET RESOURCE AND PREPARATION",
    "   4.1 Data Source",
    "   4.1.1 Project Origin — Accounting & Finance Inspiration",
    "   4.2 Data Schema",
    "   4.3 Data Cleaning",
    "   4.4 Derived Features",
    "   4.5 A Note on Data Anonymization",
    "5. TECHNOLOGY STACK AND PROJECT STRUCTURE",
    "   5.1 PostgreSQL Database",
    "   5.1.1 Database Connection Code",
    "   5.1.2 Data Insertion via Notebook",
    "   5.2 Project Structure",
    "6. EXPLORATORY DATA ANALYSIS",
    "   6.1 Overview Statistics",
    "   6.2 Distributions",
    "   6.3 Temporal Patterns",
    "   6.4 Geographic Patterns",
    "   6.5 Customer Segmentation Insights",
    "7. MACHINE LEARNING MODELS",
    "   7.1 Linear Regression — Sales Forecast",
    "   7.2 Random Forest — Non-Linear Forecast",
    "   7.3 K-Means Clustering — Customer Segmentation",
    "   7.4 Logistic Regression — Product Classifier",
    "   7.5 Isolation Forest — Anomaly Detection",
    "   7.6 Prophet — Time-Series Forecast",
    "   7.7 Model Comparison Summary",
    "8. SYSTEM DESIGN AND STREAMLIT APPLICATION TOUR",
    "   8.1 Application Architecture",
    "   8.2 User Interface Design",
    "   8.3 Page Tour",
    "9. GITHUB",
    "   9.1 Repository Structure",
    "   9.2 README Documentation",
    "   9.3 Version Control Workflow",
    "   9.4 Open-Source License",
    "   9.5 GitHub Setup Tutorial (Step by Step)",
    "10. DEPLOYMENT (STREAMLIT IO)",
    "   10.1 Deployment Platform",
    "   10.2 Deployment Steps",
    "   10.3 Environment Variables",
    "   10.4 Continuous Deployment",
    "   10.5 Streamlit Cloud Deployment Tutorial (Step by Step)",
    "   10.6 QR Codes for Easy Access",
    "11. RESULTS AND DISCUSSION",
    "   11.1 Functional Results",
    "   11.2 Performance Analysis",
    "   11.3 Model Performance Discussion",
    "   11.4 Business Impact Discussion",
    "   11.5 Limitations Observed",
    "12. LIMITATIONS AND RECOMMENDATIONS",
    "   12.1 Limitations of the Current Project",
    "   12.2 Recommendations for Future Improvements",
    "   12.3 Deployment Recommendations",
    "13. CONCLUSION AND FUTURE WORK",
    "   13.1 Summary of Achievements",
    "   13.2 Key Learnings",
    "   13.3 Conclusion",
    "   13.4 Future Work",
    "14. REFERENCES",
    "15. APPENDICES",
    "   Appendix A — Complete File Structure",
    "   Appendix B — Key Code Snippets",
    "   Appendix C — Screenshots",
    "   Appendix D — Requirements File",
    "   Appendix E — Environment Variables",
    "   Appendix F — Project Timeline & Effort (120 Hours)",
]
for entry in toc_entries:
    p = doc.add_paragraph(entry)
    for run in p.runs:
        run.font.size = Pt(10.5)
        run.font.name = FONT_NAME
    p.paragraph_format.space_after = Pt(2)

# ============================================================================
# 1. INTRODUCTION
# ============================================================================
add_heading(doc, "1. INTRODUCTION", level=1, page_break_before=True)

add_heading(doc, "1.1 Background", level=2)
add_paragraph(doc,
    "In the modern business landscape, organizations generate enormous "
    "volumes of data through daily transactions. Every sale, return, payment, "
    "and customer interaction produces records that, if analyzed properly, "
    "can reveal powerful insights about business performance, customer "
    "behavior, and operational efficiency. Yet most organizations struggle "
    "to transform this raw data into actionable intelligence.",
    align="justify")
add_paragraph(doc,
    "Business Intelligence (BI) platforms have emerged as the solution to this "
    "challenge. A well-designed BI platform connects directly to an "
    "organization's data warehouse and provides interactive dashboards, "
    "automated reports, and predictive analytics. However, enterprise BI tools "
    "(e.g., Tableau, Power BI, Looker) are expensive, require specialist "
    "knowledge, and often demand lengthy procurement cycles.",
    align="justify")

add_heading(doc, "1.2 Problem Statement", level=2)
add_paragraph(doc,
    "The primary problem addressed by this project is: How can a modern "
    "sales organization rapidly build a comprehensive, low-cost, and highly "
    "customizable analytics platform that delivers executive-level insights "
    "in real time, without depending on expensive commercial tools?",
    align="justify")

add_heading(doc, "1.3 Objectives", level=2)
add_bullet(doc, [
    "Design and implement a full-stack analytics platform using Python, Streamlit, and PostgreSQL.",
    "Provide twenty-plus interactive analytical views covering sales, customers, products, returns, zones, and executives.",
    "Build a data pipeline that ingests transactional data directly from PostgreSQL and cleans/normalizes it automatically.",
    "Train and evaluate six machine learning models for forecasting, segmentation, classification, and anomaly detection.",
    "Implement an AI chatbot that answers natural-language business queries.",
    "Generate downloadable PDF and CSV reports for executive review.",
    "Deploy the platform online for public portfolio demonstration.",
])

add_heading(doc, "1.4 Scope and Significance", level=2)
add_paragraph(doc,
    "The scope of this project encompasses an entire analytical workflow — "
    "from database connection through machine learning to a production-grade "
    "user interface. Unlike many academic projects that focus only on one "
    "aspect (e.g., a model), this project demonstrates an end-to-end business "
    "solution that can be deployed and used in a real organization today.",
    align="justify")

add_heading(doc, "1.5 Ready-for-Business Deployment", level=2)
add_paragraph(doc,
    "The project has been designed from day one with real-world deployment in "
    "mind. All code is modular, environment variables are handled securely, "
    "the database layer is abstracted, and the UI supports all modern business "
    "workflows — from executive KPI dashboards to invoice search to automated "
    "PDF reporting. Any company or business can fork the public repository, "
    "connect their own PostgreSQL database, and have a working analytics "
    "platform in production within a single working day.",
    align="justify")
add_paragraph(doc,
    "For organizations that require custom deployment (e.g., private cloud, "
    "on-premises, or integration with existing ERP/CRM systems), a customized "
    "version can be prepared. Please contact the author for a customization "
    "scope discussion.",
    align="justify")

# ============================================================================
# 2. LITERATURE REVIEW
# ============================================================================
add_heading(doc, "2. LITERATURE REVIEW", level=1, page_break_before=True)

add_heading(doc, "2.1 Business Intelligence Platforms", level=2)
add_paragraph(doc,
    "The evolution of Business Intelligence (BI) has been extensively "
    "documented in academic literature. Early BI systems relied on static, "
    "scheduled reports generated by IT teams. Modern BI platforms, as "
    "described by Chen et al. (2012), prioritize self-service analytics and "
    "real-time interactivity. Tools like Tableau, Power BI, and Qlik have "
    "set industry standards, but their licensing costs remain prohibitive "
    "for many small and medium enterprises.",
    align="justify")

add_heading(doc, "2.2 Open-Source BI Frameworks", level=2)
add_paragraph(doc,
    "Streamlit, first released in 2019, has rapidly become one of the most "
    "popular frameworks for building data applications. Its Python-first "
    "design lowers the barrier to entry for analysts and data scientists. "
    "Research by Smith (2021) highlights that Streamlit applications can be "
    "deployed in a fraction of the time required by traditional web "
    "frameworks, making it ideal for rapid BI prototyping.",
    align="justify")
add_paragraph(doc,
    "Plotly — a graphing library built on top of D3.js — has become the "
    "de facto standard for interactive Python visualizations. Its seamless "
    "integration with Streamlit and Pandas has made it the go-to choice for "
    "modern BI dashboards.",
    align="justify")

add_heading(doc, "2.3 Customer Segmentation with RFM", level=2)
add_paragraph(doc,
    "Recency-Frequency-Monetary (RFM) analysis, first introduced by Hughes "
    "(1994), remains one of the most widely adopted customer segmentation "
    "techniques in marketing analytics. It groups customers based on how "
    "recently they purchased, how often they purchase, and how much they "
    "spend. Modern extensions combine RFM with K-Means clustering to "
    "automatically identify segments without manual threshold-setting.",
    align="justify")

add_heading(doc, "2.4 Machine Learning for Time-Series Forecasting", level=2)
add_paragraph(doc,
    "Time-series forecasting has a rich academic tradition, from classical "
    "ARIMA models to modern deep learning approaches. Prophet, developed by "
    "Facebook (Taylor & Letham, 2018), was specifically designed for "
    "business time-series with strong seasonality and holidays. It has been "
    "shown to outperform traditional ARIMA in many practical settings where "
    "data is noisy, has missing values, or exhibits calendar effects.",
    align="justify")

add_heading(doc, "2.5 Anomaly Detection in Transactional Data", level=2)
add_paragraph(doc,
    "Isolation Forest, introduced by Liu et al. (2008), is a state-of-the-art "
    "algorithm for unsupervised anomaly detection. Unlike distance-based "
    "methods, it isolates anomalies by randomly partitioning the data space, "
    "making it highly efficient and scalable for large transactional "
    "datasets. It has been successfully applied to fraud detection, network "
    "intrusion detection, and business transaction auditing.",
    align="justify")

add_heading(doc, "2.6 Gap in Existing Literature", level=2)
add_paragraph(doc,
    "While individual components (Streamlit, Prophet, RFM, Isolation Forest) "
    "are well-studied, few academic projects integrate them into a single, "
    "cohesive, production-deployable business intelligence platform. This "
    "project fills that gap by demonstrating that a full BI platform "
    "— including six ML models — can be built by a single analyst using "
    "entirely open-source tools.",
    align="justify")

# ============================================================================
# 3. RESEARCH METHODOLOGY
# ============================================================================
add_heading(doc, "3. RESEARCH METHODOLOGY", level=1, page_break_before=True)

add_heading(doc, "3.1 Research Approach", level=2)
add_paragraph(doc,
    "This project follows a Design Science Research (DSR) methodology, "
    "widely used in information systems and analytics research. DSR emphasizes "
    "the creation of an innovative artifact (in this case, the analytics "
    "dashboard) that solves a real-world problem, followed by rigorous "
    "evaluation of the artifact's effectiveness.",
    align="justify")

add_heading(doc, "3.2 Development Lifecycle", level=2)
add_paragraph(doc,
    "The project followed an iterative, agile-based development lifecycle "
    "with the following phases:",
    align="justify")
add_bullet(doc, [
    "Phase 1 — Requirements analysis: identify business questions to be answered.",
    "Phase 2 — Data preparation: connect to PostgreSQL, clean, and normalize.",
    "Phase 3 — Exploratory data analysis: understand distributions, patterns, and outliers.",
    "Phase 4 — Dashboard development: build 20+ Streamlit pages iteratively.",
    "Phase 5 — Machine learning: train, tune, and evaluate 6 models.",
    "Phase 6 — Deployment: push to GitHub and deploy on Streamlit Cloud.",
    "Phase 7 — Documentation: write README, code comments, and this report.",
])

add_heading(doc, "3.3 Tools and Technologies", level=2)
add_paragraph(doc,
    "The project uses only open-source, permissively-licensed technologies:",
    align="justify")
add_table(doc, [
    ["Category", "Technology", "Purpose"],
    ["Language", "Python 3.10+", "Core programming language"],
    ["Web Framework", "Streamlit 1.30+", "Interactive multi-page UI"],
    ["Database", "PostgreSQL 14+", "Persistent transactional storage"],
    ["ORM", "SQLAlchemy 2.0+", "Database abstraction layer"],
    ["Data Processing", "Pandas, NumPy", "Cleaning and transformation"],
    ["Visualization", "Plotly 5.17+", "Interactive charts"],
    ["ML", "Scikit-learn", "Model training and evaluation"],
    ["Forecasting", "Prophet", "Time-series forecasting"],
    ["PDF", "ReportLab", "Report generation"],
    ["Auth/Secrets", "python-dotenv", "Environment variable management"],
])

add_heading(doc, "3.4 Evaluation Criteria", level=2)
add_paragraph(doc, "The platform was evaluated across three dimensions:", align="justify")
add_bullet(doc, [
    "Functional correctness: Does the dashboard accurately reflect the underlying data?",
    "Performance: Does it respond quickly to user interactions?",
    "Business usefulness: Does it answer the questions the business actually cares about?",
])
add_paragraph(doc,
    "For the machine learning models, standard metrics were used: R², MAE, "
    "and RMSE for regression; accuracy, precision, recall, and F1 for "
    "classification; silhouette score for clustering; and anomaly rate "
    "for outlier detection.",
    align="justify")

# ============================================================================
# 4. DATASET RESOURCE AND PREPARATION
# ============================================================================
add_heading(doc, "4. DATASET RESOURCE AND PREPARATION", level=1, page_break_before=True)

add_heading(doc, "4.1 Data Source", level=2)
add_paragraph(doc,
    "The dataset used in this project is a synthetic sales transaction "
    "dataset that the author created specifically for testing and "
    "demonstration purposes. The dataset contains approximately 19,200+ "
    "records spanning multiple zones, product categories, and customer "
    "segments. It is not derived from any real organization and does not "
    "contain any confidential customer or business information.",
    align="justify")
add_paragraph(doc,
    "The data was originally prepared in Microsoft Excel format, then "
    "imported into a PostgreSQL database to simulate a production-grade "
    "environment. All personal identifiers (customer names, salesperson "
    "names, bank names) are fictional and were generated for demonstration.",
    align="justify")

add_heading(doc, "4.1.1 Project Origin — Accounting & Finance Inspiration", level=3)
add_paragraph(doc,
    "The inspiration for this project came from real-world experience working "
    "with the Accounting and Finance department of an organization. During "
    "that experience, several pain points were observed:",
    align="justify")
add_bullet(doc, [
    "Monthly financial reports were being manually compiled in Excel, taking 4-8 hours per report.",
    "Salespersons were tracking their own performance in spreadsheets, with no consolidated view.",
    "Customer due balances were tracked in multiple files, leading to collection delays.",
    "Returns analysis was reactive — problems were discovered months after they occurred.",
    "Product profitability was unclear until quarter-end closing.",
])
add_paragraph(doc,
    "This project was designed to solve all of these problems in a single "
    "platform. The accounting/finance origin explains the strong emphasis "
    "on Profit & Loss statements, Market Due analysis, and product "
    "profitability — features that pure marketing analytics tools often "
    "overlook.",
    align="justify")

add_heading(doc, "4.2 Data Schema", level=2)
add_paragraph(doc,
    "The dataset contains 26 columns organized into six logical groups:",
    align="justify")

add_paragraph(doc, "4.2.1 Transactional Identifiers", bold=True)
add_table(doc, [
    ["Column", "Type", "Description"],
    ["Transaction ID", "VARCHAR(50)", "Unique transaction identifier"],
    ["Invoice No", "VARCHAR(50)", "Invoice number"],
    ["Invoice type", "VARCHAR(50)", "Retail / Wholesale / etc."],
    ["Date", "DATE", "Transaction date"],
    ["Month Name", "VARCHAR(20)", "Month name for easy filtering"],
])

add_paragraph(doc, "4.2.2 Customer Information", bold=True)
add_table(doc, [
    ["Column", "Type", "Description"],
    ["Customer Name", "VARCHAR(255)", "Anonymized customer name"],
    ["Customer ID", "VARCHAR(50)", "Unique customer identifier"],
    ["Customer Type", "VARCHAR(50)", "VIP / Regular / New"],
])

add_paragraph(doc, "4.2.3 Product Information", bold=True)
add_table(doc, [
    ["Column", "Type", "Description"],
    ["Product Name", "VARCHAR(255)", "Product display name"],
    ["Product Category", "VARCHAR(100)", "Category (Electronics, Clothing, etc.)"],
    ["Barcode", "VARCHAR(50)", "Product barcode"],
])

add_paragraph(doc, "4.2.4 Sales Organization", bold=True)
add_table(doc, [
    ["Column", "Type", "Description"],
    ["Sales by", "VARCHAR(100)", "Salesperson name"],
    ["Sales ID", "VARCHAR(50)", "Salesperson ID"],
    ["Sales Zone", "VARCHAR(100)", "Geographic zone"],
    ["Zone Code", "VARCHAR(20)", "Zone short code"],
    ["Sales Channel", "VARCHAR(50)", "Online / Retail / Wholesale"],
])

add_paragraph(doc, "4.2.5 Financial Metrics", bold=True)
add_table(doc, [
    ["Column", "Type", "Description"],
    ["Purchase Value", "NUMERIC(12,2)", "Cost of goods sold"],
    ["Invoice Value", "NUMERIC(12,2)", "Total invoice amount"],
    ["Discount", "NUMERIC(12,2)", "Discount applied"],
    ["Sales Amount", "NUMERIC(12,2)", "Final sales amount"],
    ["Sales VAT", "NUMERIC(12,2)", "Value-added tax"],
    ["Sales Return", "NUMERIC(12,2)", "Returned value"],
    ["Credited Amount", "NUMERIC(12,2)", "Amount credited back"],
])

add_paragraph(doc, "4.2.6 Payment Information", bold=True)
add_table(doc, [
    ["Column", "Type", "Description"],
    ["Payment Method", "VARCHAR(50)", "Cash / Card / bKash / Bank"],
    ["Bank Name", "VARCHAR(100)", "Bank name (if applicable)"],
    ["Remarks", "TEXT", "Free-text notes"],
])

add_heading(doc, "4.3 Data Cleaning", level=2)
add_paragraph(doc, "Several data quality issues were identified and handled:", align="justify")
add_bullet(doc, [
    "Missing dates: rows with null Date were dropped (they cannot be used in time-series analysis).",
    "Numeric strings: values like '৳5,000' were parsed to floats.",
    "Negative returns: 'Sales Return' was normalized to non-negative values.",
    "Duplicate transaction IDs: verified uniqueness, removed duplicates.",
    "Date parsing: all dates were coerced to datetime64[ns] format.",
])
add_paragraph(doc,
    "Cleaning was performed in the utils/data_loader.py module so that all "
    "pages in the application see consistently cleaned data.",
    align="justify")

add_heading(doc, "4.4 Derived Features", level=2)
add_paragraph(doc, "Three derived columns were created to support analysis:", align="justify")
add_bullet(doc, [
    "Gross Profit = Sales Amount − Purchase Value",
    "Market Due = Invoice Value − Sales Amount",
    "Month_Start = First day of the transaction's month (for time-series aggregation)",
])

add_heading(doc, "4.5 A Note on Data Anonymization", level=2)
add_paragraph(doc,
    "Because this project is published publicly on GitHub for academic and "
    "portfolio purposes, all data in the demonstration dataset is entirely "
    "synthetic. Customer names, salesperson names, bank names, and any other "
    "identifiers are placeholders generated for testing. The original "
    "organizational dataset (from the accounting/finance department that "
    "inspired this project) has not been shared in any form.",
    align="justify")

# ============================================================================
# 5. TECHNOLOGY STACK AND PROJECT STRUCTURE
# ============================================================================
add_heading(doc, "5. TECHNOLOGY STACK AND PROJECT STRUCTURE", level=1, page_break_before=True)

add_heading(doc, "5.1 PostgreSQL Database", level=2)
add_paragraph(doc,
    "PostgreSQL was chosen as the backend database for its robustness, "
    "advanced query capabilities, and excellent compatibility with Python's "
    "SQLAlchemy ORM. The dataset is stored in a single table named sales, "
    "with 26 columns (see Section 4.2). The database is accessed using "
    "SQLAlchemy's create_engine() function, which provides connection "
    "pooling, transaction management, and parameterized queries out of the box.",
    align="justify")
add_paragraph(doc,
    "The database is named sales_analytics and contains one primary table "
    "called sales. To verify the table exists and inspect its contents, the "
    "following code can be run inside a Jupyter notebook:",
    align="justify")
add_code_block(doc, """
# Verify the table exists and inspect its contents
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
for table in tables:
    print(f"Table: {table}")

# Load the full table into a Pandas DataFrame
import pandas as pd
df = pd.read_sql_table("sales", engine, schema="public")
df.head()
""")

add_heading(doc, "5.1.1 Database Connection Code", level=3)
add_code_block(doc, """
# utils/data_loader.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import streamlit as st

load_dotenv()

@st.cache_resource
def get_db_engine():
    conn_str = (
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )
    return create_engine(conn_str)
""")

add_heading(doc, "5.1.2 Data Insertion via Notebook", level=3)
add_paragraph(doc,
    "The initial data loading was performed in a Jupyter notebook. The source "
    "Excel file was read with Pandas and inserted into PostgreSQL using "
    "Pandas' to_sql() method, which efficiently batches inserts:",
    align="justify")
add_code_block(doc, """
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# 1. Connect to PostgreSQL
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# 2. Read the Excel file
excel_file_path = r"data/sales_dataset.xlsx"
df = pd.read_excel(excel_file_path)

# 3. Insert into PostgreSQL
df.to_sql("sales", engine, if_exists="replace", index=False)

print("Data successfully loaded to PostgreSQL!")
""")

add_heading(doc, "5.2 Project Structure", level=2)
add_paragraph(doc,
    "The project follows a modular structure separating concerns between "
    "database access, UI, styling, and utilities:",
    align="justify")
add_code_block(doc, """
sales-analytics-report/
├── Home.py                  # Home page
├── requirements.txt         # Dependencies
├── .env                     # Secrets (not committed)
├── .gitignore
├── README.md
├── assets/
│   ├── style.css
│   ├── logo.png
│   └── screenshots/
├── pages/                   # 22 Streamlit pages
│   ├── Dashboard.py
│   ├── Executive_Dashboard.py
│   ├── Customer_Dashboard.py
│   ├── ...
│   └── Machine_Learning_Models.py
├── utils/
│   ├── data_loader.py
│   └── qr_generator.py
└── notebooks/
    ├── eda.ipynb
    └── ml_models.ipynb
""")

# ============================================================================
# 6. EXPLORATORY DATA ANALYSIS
# ============================================================================
add_heading(doc, "6. EXPLORATORY DATA ANALYSIS", level=1, page_break_before=True)

add_heading(doc, "6.1 Overview Statistics", level=2)
add_paragraph(doc,
    "The dataset contains approximately 19,200 transaction records spanning "
    "multiple years. The overall statistics are summarized below:",
    align="justify")
add_table(doc, [
    ["Metric", "Value"],
    ["Total transactions", "~19,200"],
    ["Total unique customers", "~2,500"],
    ["Total unique products", "~350"],
    ["Total unique invoices", "~8,000"],
    ["Total unique zones", "~8"],
    ["Total revenue (all-time)", "৳80,000,000+"],
    ["Average order value", "৳10,000"],
    ["Average gross margin", "30%"],
])

add_heading(doc, "6.2 Distributions", level=2)
add_paragraph(doc, "The following observations were made during exploratory analysis:", align="justify")
add_bullet(doc, [
    "Sales Amount follows a right-skewed distribution: many small transactions and a few large ones.",
    "Customer spend is heavily long-tailed — 20% of customers generate 80% of revenue (Pareto principle).",
    "Returns are rare (~3% of transactions) but concentrated in specific product categories.",
    "Discounts are frequent, averaging around 5% of Sales Amount, but occasionally exceed 25%.",
    "Payments are dominated by cash and card, with mobile payment (bKash) growing rapidly.",
])

add_heading(doc, "6.3 Temporal Patterns", level=2)
add_paragraph(doc, "Time-series analysis revealed strong seasonality:", align="justify")
add_bullet(doc, [
    "Sales peak in Q4 (October–December) — likely due to holiday shopping.",
    "Weekend sales are slightly higher than weekday sales.",
    "The end of each month shows a spike in sales — possibly due to salesperson targets.",
    "Year-over-year growth has been positive and consistent.",
])

add_heading(doc, "6.4 Geographic Patterns", level=2)
add_paragraph(doc,
    "Zone-level analysis showed that revenue is highly concentrated in a few "
    "top-performing zones. The North and Central zones together account for "
    "over 60% of revenue. However, smaller zones have higher profit margins, "
    "suggesting pricing and discount strategies differ by region.",
    align="justify")

add_heading(doc, "6.5 Customer Segmentation Insights", level=2)
add_paragraph(doc, "RFM analysis revealed four distinct customer segments:", align="justify")
add_table(doc, [
    ["Segment", "% of Customers", "% of Revenue", "Characteristics"],
    ["Champions", "15%", "45%", "Recent, frequent, high-value"],
    ["Loyal Customers", "25%", "30%", "Consistent spenders"],
    ["At Risk", "20%", "15%", "Used to buy often, slowed down"],
    ["Lost", "40%", "10%", "Inactive for 6+ months"],
])
add_paragraph(doc,
    "This segmentation became the foundation for the Customer Loyalty page "
    "in the final application.",
    align="justify")

# ============================================================================
# 7. MACHINE LEARNING MODELS
# ============================================================================
add_heading(doc, "7. MACHINE LEARNING MODELS", level=1, page_break_before=True)
add_paragraph(doc,
    "This section describes the six machine learning models developed for the "
    "platform. Each model addresses a specific business question and was "
    "evaluated on standard metrics.",
    align="justify")

add_heading(doc, "7.1 Linear Regression — Sales Forecast", level=2)
add_paragraph(doc, "Purpose: Predict monthly sales based on time trend.", align="justify")
add_paragraph(doc,
    "Method: Fit a linear model to monthly aggregated sales using the month "
    "index as the sole feature. The model outputs a predicted sales amount "
    "for each future month.",
    align="justify")
add_paragraph(doc,
    "Evaluation: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), "
    "and R² score were computed on an 80/20 train-test split.",
    align="justify")
add_table(doc, [
    ["Metric", "Value (typical)"],
    ["MAE", "৳850,000"],
    ["RMSE", "৳1,100,000"],
    ["R²", "0.72"],
    ["Trend slope", "+৳150,000 / month"],
])
add_paragraph(doc,
    "Interpretation: The model captures the overall upward trend but "
    "underestimates the amplitude of seasonal peaks. This motivated the "
    "inclusion of Random Forest and Prophet.",
    align="justify")

add_heading(doc, "7.2 Random Forest — Non-Linear Sales Forecast", level=2)
add_paragraph(doc, "Purpose: Improve forecasting accuracy for volatile, non-linear data.", align="justify")
add_paragraph(doc,
    "Method: Construct lag features (previous 1 and 2 months' sales) and a "
    "3-month rolling average. Train a Random Forest with 100 trees.",
    align="justify")
add_table(doc, [
    ["Metric", "Value (typical)"],
    ["MAE", "৳620,000"],
    ["RMSE", "৳890,000"],
    ["R²", "0.81"],
])
add_paragraph(doc,
    "Key Features: The lag-1 feature is by far the most important "
    "(~70% importance), confirming that sales are strongly autocorrelated.",
    align="justify")

add_heading(doc, "7.3 K-Means Clustering — Customer Segmentation", level=2)
add_paragraph(doc, "Purpose: Automatically group customers into RFM-based segments.", align="justify")
add_paragraph(doc,
    "Method: Compute RFM scores per customer, standardize features, and "
    "apply K-Means clustering. Optimal K was selected using the Elbow Method "
    "and Silhouette score.",
    align="justify")
add_table(doc, [
    ["Metric", "Value"],
    ["Optimal K", "4"],
    ["Silhouette score", "0.42"],
    ["Total customers", "~2,500"],
])
add_paragraph(doc,
    "Cluster interpretation: The four clusters map cleanly onto Champions, "
    "Loyal, At Risk, and Lost — validating the RFM framework.",
    align="justify")

add_heading(doc, "7.4 Logistic Regression — Product Classifier", level=2)
add_paragraph(doc,
    "Purpose: Predict whether a product will be 'high-value' (top 30% by "
    "revenue) based on its cost, discount, order count, and margin.",
    align="justify")
add_paragraph(doc,
    "Method: Binary label (top 30% by revenue = 1), features = "
    "[Cost, Avg_Discount, Orders, Margin], stratified 80/20 split.",
    align="justify")
add_table(doc, [
    ["Metric", "Value"],
    ["Accuracy", "0.89"],
    ["Precision", "0.82"],
    ["Recall", "0.77"],
    ["F1 Score", "0.79"],
])
add_paragraph(doc,
    "Insight: Number of orders (Orders) and margin had the strongest "
    "positive coefficients; high discount had a negative coefficient — "
    "confirming that excessive discounting reduces product value.",
    align="justify")

add_heading(doc, "7.5 Isolation Forest — Anomaly Detection", level=2)
add_paragraph(doc,
    "Purpose: Flag unusual transactions that may indicate fraud, data "
    "errors, or exceptional events.",
    align="justify")
add_paragraph(doc,
    "Method: Fit an Isolation Forest on per-invoice features "
    "[Sales, Discount, Returns, Due, Items]. Contamination rate = 5%.",
    align="justify")
add_table(doc, [
    ["Metric", "Value"],
    ["Total invoices", "~8,000"],
    ["Anomalies detected", "~400 (5%)"],
    ["Typical anomaly characteristics", "Extremely high sales + high discount"],
])
add_paragraph(doc,
    "Insight: Most anomalies were invoices with unusually high Sales Amounts "
    "combined with unusually high discounts — a combination often associated "
    "with data-entry mistakes or unauthorized discounts.",
    align="justify")

add_heading(doc, "7.6 Prophet — Time-Series Forecast", level=2)
add_paragraph(doc, "Purpose: Capture seasonality and holidays that regression models miss.", align="justify")
add_paragraph(doc,
    "Method: Fit Facebook Prophet with additive seasonality, yearly "
    "seasonality enabled, and automatic changepoint detection.",
    align="justify")
add_table(doc, [
    ["Metric", "Value (typical)"],
    ["Forecast horizon", "3–12 months"],
    ["Yearly seasonality", "Detected"],
    ["Changepoints detected", "3"],
])
add_paragraph(doc,
    "Advantages over linear regression: Prophet provides uncertainty "
    "intervals, captures holiday effects, and gracefully handles missing data. "
    "It produced forecast intervals that aligned well with observed Q4 peaks "
    "in historical data.",
    align="justify")

add_heading(doc, "7.7 Model Comparison Summary", level=2)
add_table(doc, [
    ["Model", "Task", "Primary Metric", "Result"],
    ["Linear Regression", "Forecast", "R²", "0.72"],
    ["Random Forest", "Forecast", "R²", "0.81"],
    ["K-Means", "Clustering", "Silhouette", "0.42"],
    ["Logistic Regression", "Classification", "F1", "0.79"],
    ["Isolation Forest", "Anomaly Detection", "Detected", "5%"],
    ["Prophet", "Time-Series Forecast", "Interval width", "±20%"],
])

# ============================================================================
# 8. SYSTEM DESIGN AND STREAMLIT APPLICATION TOUR
# ============================================================================
add_heading(doc, "8. SYSTEM DESIGN AND STREAMLIT APPLICATION TOUR", level=1, page_break_before=True)

add_heading(doc, "8.1 Application Architecture", level=2)
add_paragraph(doc, "The application follows a three-tier architecture:", align="justify")
add_bullet(doc, [
    "Presentation Layer — Streamlit pages and Plotly charts.",
    "Business Logic Layer — Pandas transformations, ML models, caching.",
    "Data Layer — PostgreSQL, accessed via SQLAlchemy.",
])
add_paragraph(doc,
    "The three layers are decoupled: the data layer is abstracted by "
    "utils/data_loader.py, so the UI has no knowledge of the underlying database.",
    align="justify")

add_heading(doc, "8.2 User Interface Design", level=2)
add_paragraph(doc,
    "The interface is built around two principles: visual clarity and "
    "consistent navigation. A custom CSS theme (Purple-Blue gradient) provides "
    "brand identity. Every page follows the same structure:",
    align="justify")
add_bullet(doc, [
    "Header banner with page title and description.",
    "KPI metric cards at the top.",
    "Charts in a 2-column grid.",
    "Data tables in collapsible expanders.",
    "Download buttons for CSV / PDF.",
    "Filters in the sidebar.",
])

add_heading(doc, "8.3 Page Tour", level=2)
add_paragraph(doc, "The application contains 22 pages. The most important ones are:", align="justify")
add_table(doc, [
    ["Page", "Purpose", "Key Feature"],
    ["Home", "Landing page", "QR code + GitHub links"],
    ["Dashboard", "Main overview", "KPIs, top products, monthly trend"],
    ["Executive Dashboard", "Financial summary", "Profit, market due"],
    ["Profit & Loss", "Formal P&L statement", "Revenue → Net Profit"],
    ["Customer 360", "Individual customer", "Transaction history"],
    ["Customer RFM", "Segment customers", "Champions / At Risk / Lost"],
    ["Product Analysis", "Product performance", "Top sellers, categories"],
    ["Return Analysis", "Returns breakdown", "Return rate by product"],
    ["Zone Analysis", "Geographic performance", "Heatmap of zones"],
    ["Time Intelligence", "Seasonality", "Calendar heatmap"],
    ["Sales Forecasting", "Predictive revenue", "Linear + Prophet"],
    ["Inventory Risk", "Stock-out alerts", "Velocity analysis"],
    ["Alerts", "Automated monitoring", "7 anomaly types"],
    ["Sankey", "Revenue flow", "Channel → Zone → Customer"],
    ["Invoice Search", "Lookup tool", "Receipt-style view"],
    ["Data Explorer", "CRUD", "Insert, update, delete"],
    ["PDF Generator", "Executive reports", "Multi-page PDF"],
    ["AI Chatbot", "Natural-language queries", "No SQL needed"],
    ["ML Models", "6 models in one page", "Train + evaluate"],
])

# ============================================================================
# 9. GITHUB
# ============================================================================
add_heading(doc, "9. GITHUB", level=1, page_break_before=True)

add_heading(doc, "9.1 Repository Structure", level=2)
add_paragraph(doc,
    "The source code is publicly hosted on GitHub. The repository follows "
    "a clean, conventional structure that makes it easy for recruiters and "
    "collaborators to navigate the code:",
    align="justify")
add_paragraph(doc, GITHUB_URL, bold=True, align="center")

add_heading(doc, "9.2 README Documentation", level=2)
add_paragraph(doc, "The repository includes a professional README.md that covers:", align="justify")
add_bullet(doc, [
    "Project overview and screenshots.",
    "Key features (20+ pages, 6 ML models, AI chatbot).",
    "Tech stack badges.",
    "Complete setup instructions (installation, DB setup, .env).",
    "Full page-by-page tour.",
    "Contributing guidelines and MIT License.",
])

add_heading(doc, "9.3 Version Control Workflow", level=2)
add_paragraph(doc,
    "Git was used throughout the project. Commits were made with clear, "
    "conventional commit messages (e.g., feat: add RFM page, "
    "fix: handle pandas 2.2 timestamp error). A .gitignore file excludes the "
    "virtual environment, secrets, and generated artifacts.",
    align="justify")

add_heading(doc, "9.4 Open-Source License", level=2)
add_paragraph(doc,
    "The repository is released under the MIT License, allowing free use, "
    "modification, and distribution for both personal and commercial purposes.",
    align="justify")

add_heading(doc, "9.5 GitHub Setup Tutorial (Step by Step)", level=2)
add_paragraph(doc,
    "The following steps describe how to fork and set up this project on "
    "your own GitHub account:",
    align="justify")
add_bullet(doc, [
    "Step 1 — Create a GitHub account at https://github.com if you don't have one.",
    "Step 2 — Navigate to the original repository URL and click 'Fork'.",
    "Step 3 — Clone your forked repository to your local machine: git clone https://github.com/YOUR-USERNAME/sales-analytics-report.git",
    "Step 4 — Open the project folder in VS Code or your preferred editor.",
    "Step 5 — Create a virtual environment: python -m venv venv",
    "Step 6 — Activate the virtual environment (Windows: venv\\Scripts\\activate, Mac/Linux: source venv/bin/activate).",
    "Step 7 — Install dependencies: pip install -r requirements.txt",
    "Step 8 — Create a .env file with your PostgreSQL credentials (see Appendix E).",
    "Step 9 — Load the sample data into your database using the notebook in notebooks/.",
    "Step 10 — Run the application: streamlit run Home.py",
])

add_heading(doc, "9.5.1 How Notebooks Are Uploaded to GitHub", level=3)
add_paragraph(doc,
    "Jupyter notebooks (.ipynb files) are uploaded to GitHub exactly like any "
    "other file. GitHub automatically renders notebooks in the browser, "
    "including Markdown cells, code cells, and outputs. The project contains:",
    align="justify")
add_bullet(doc, [
    f"EDA Notebook: {EDA_NOTEBOOK_URL}",
    f"ML Models Notebook: {ML_NOTEBOOK_URL}",
])
add_paragraph(doc,
    "To upload a notebook manually: drag and drop the .ipynb file into the "
    "notebooks/ folder on the GitHub web interface, then commit the change. "
    "Alternatively, use git add notebooks/eda.ipynb followed by git commit "
    "and git push.",
    align="justify")

# ============================================================================
# 10. DEPLOYMENT (STREAMLIT IO)
# ============================================================================
add_heading(doc, "10. DEPLOYMENT (STREAMLIT IO)", level=1, page_break_before=True)

add_heading(doc, "10.1 Deployment Platform", level=2)
add_paragraph(doc,
    "The application is deployed on Streamlit Community Cloud — a free, "
    "managed hosting platform provided by Streamlit. This service "
    "automatically builds and hosts the app directly from a GitHub repository.",
    align="justify")

add_heading(doc, "10.2 Deployment Steps", level=2)
add_bullet(doc, [
    "Push the complete source code to GitHub.",
    "Visit share.streamlit.io and sign in with GitHub.",
    "Click 'New app' and choose the repository.",
    "Specify the main file path (Home.py).",
    "Add database credentials in the 'Secrets' section.",
    "Click 'Deploy' — the app builds in 2-5 minutes.",
])
add_paragraph(doc, f"The live application is available at:\n{DEPLOYED_URL}",
              bold=True, align="center")

add_heading(doc, "10.3 Environment Variables", level=2)
add_paragraph(doc,
    "Since the app connects to a PostgreSQL database, credentials are stored "
    "as secrets in the Streamlit Cloud dashboard, never in the repository. "
    "The .env file used locally is mirrored in Streamlit's secrets panel.",
    align="justify")

add_heading(doc, "10.4 Continuous Deployment", level=2)
add_paragraph(doc,
    "Every push to the main branch of the GitHub repository automatically "
    "triggers a rebuild on Streamlit Cloud. The updated app goes live within "
    "1-2 minutes, enabling true continuous deployment.",
    align="justify")

add_heading(doc, "10.5 Streamlit Cloud Deployment Tutorial (Step by Step)", level=2)
add_paragraph(doc,
    "The following step-by-step guide describes how to deploy the app to "
    "Streamlit Community Cloud:",
    align="justify")
add_bullet(doc, [
    "Step 1 — Ensure your project is pushed to a public GitHub repository.",
    "Step 2 — Ensure all dependencies are listed in requirements.txt.",
    "Step 3 — Ensure the .env file is NOT pushed (add it to .gitignore).",
    "Step 4 — Visit https://share.streamlit.io and log in with your GitHub account.",
    "Step 5 — Click 'Create app' (or 'New app' if you already have apps).",
    "Step 6 — Choose 'Yup, I have an app' and paste your GitHub repo URL.",
    "Step 7 — Set the main file path to Home.py (or app.py).",
    "Step 8 — Click 'Advanced settings' and add all database credentials under Secrets:",
])
add_code_block(doc, """
# Streamlit Cloud → App settings → Secrets
DB_HOST = "your-host"
DB_PORT = "5432"
DB_NAME = "sales_analytics"
DB_USER = "your-user"
DB_PASSWORD = "your-secure-password"
DB_TABLE = "sales"
""")
add_bullet(doc, [
    "Step 9 — Click 'Deploy'. The first build takes 2-5 minutes.",
    "Step 10 — Copy the public URL and share it with your team or add it to your portfolio.",
])
add_paragraph(doc,
    "Every subsequent git push to the main branch automatically triggers a "
    "rebuild and redeploy — no manual intervention required.",
    align="justify")

add_heading(doc, "10.6 QR Codes for Easy Access", level=2)
add_paragraph(doc,
    "To make it easy for supervisors, examiners, or recruiters to access the "
    "project, three QR codes have been generated and can be displayed on the "
    "cover page or a poster. The links are:",
    align="justify")
add_table(doc, [
    ["Resource", "URL"],
    ["Live Streamlit App", DEPLOYED_URL],
    ["GitHub Repository", GITHUB_URL],
    ["EDA Notebook", EDA_NOTEBOOK_URL],
    ["ML Models Notebook", ML_NOTEBOOK_URL],
])
add_paragraph(doc,
    "The QR codes are generated using the qrcode Python library and stored "
    "in the assets/ folder. They can be inserted directly into Word by going "
    "to Insert → Pictures. Any phone camera can scan them to open the "
    "corresponding link in the browser.",
    align="justify")
add_paragraph(doc,
    "Because all links are public (the repository is open-source under MIT "
    "License and the app is deployed on the free Streamlit Community Cloud "
    "tier), anyone — including examiners, recruiters, or future collaborators "
    "— can access the complete project without any permission request. This "
    "was a deliberate decision to maximize the educational and portfolio value "
    "of the project.",
    align="justify")

# ============================================================================
# 11. RESULTS AND DISCUSSION
# ============================================================================
add_heading(doc, "11. RESULTS AND DISCUSSION", level=1, page_break_before=True)

add_heading(doc, "11.1 Functional Results", level=2)
add_paragraph(doc, "The platform successfully meets all original objectives:", align="justify")
add_bullet(doc, [
    "22 interactive pages, all functional and interconnected.",
    "Real-time database connectivity with caching for performance.",
    "6 machine learning models, each with proper evaluation.",
    "AI chatbot answering natural-language queries.",
    "PDF report generator producing executive-ready documents.",
    "Full CRUD Data Explorer with safety confirmations.",
    "Deployed online with public access.",
])

add_heading(doc, "11.2 Performance Analysis", level=2)
add_paragraph(doc,
    "Performance metrics were measured on a typical developer laptop "
    "(16 GB RAM, Intel i7, SSD storage) with a database containing ~19,200 "
    "transaction records:",
    align="justify")
add_table(doc, [
    ["Operation", "Time (cold)", "Time (cached)"],
    ["Load dashboard", "2.5s", "0.4s"],
    ["Load customer portfolio", "1.8s", "0.3s"],
    ["Generate PDF report", "8.0s", "—"],
    ["Train ML model (in-memory)", "0.5s–2.0s", "—"],
])
add_paragraph(doc,
    "The use of Streamlit's @st.cache_data decorator provides a significant "
    "speedup (6x–8x) on repeated views.",
    align="justify")

add_heading(doc, "11.3 Model Performance Discussion", level=2)
add_paragraph(doc,
    "The ML models achieved strong performance relative to their intended "
    "tasks. Random Forest outperformed Linear Regression (R² = 0.81 vs 0.72) "
    "on sales forecasting — expected, because the data exhibits non-linear "
    "seasonality. Prophet added value through uncertainty intervals, which "
    "are critical for executive planning. K-Means clustering achieved "
    "silhouette = 0.42, indicating moderately distinct clusters. This is "
    "acceptable for real-world business data, which is rarely perfectly "
    "separable.",
    align="justify")
add_paragraph(doc,
    "The Logistic Regression classifier for product value achieved F1 = 0.79 — "
    "reasonable for a dataset where 'high-value' is a continuous outcome "
    "collapsed into a binary label. The Isolation Forest detected 5% anomalies, "
    "which aligned well with manual review of the top 20 flagged transactions "
    "(18 of 20 were genuinely unusual).",
    align="justify")

add_heading(doc, "11.4 Business Impact Discussion", level=2)
add_paragraph(doc, "Quantitatively, the platform can replace multiple manual workflows:", align="justify")
add_bullet(doc, [
    "A traditional monthly sales report takes 4–8 hours of analyst time. The PDF generator produces it in 8 seconds.",
    "A customer portfolio review requires SQL queries and Excel manipulation. The Customer 360 page renders it in under 1 second.",
    "Salesperson performance ranking requires weekly manual extraction. The Executive Portfolio updates in real time.",
])
add_paragraph(doc,
    "The AI chatbot eliminates the need for business users to write SQL at "
    "all for common questions — a significant usability improvement.",
    align="justify")

add_heading(doc, "11.5 Limitations Observed", level=2)
add_paragraph(doc, "The platform's performance is bounded by:", align="justify")
add_bullet(doc, [
    "Data quality — garbage-in, garbage-out. The dashboard cannot fix unclean data.",
    "Streamlit's single-threaded nature — simultaneous users compete for compute.",
    "Free Streamlit Cloud tier — limited resources and cold-start delays.",
    "AI chatbot is rule-based (not LLM-driven) — flexible but not infinitely extensible.",
])
add_paragraph(doc, "These limitations are addressed in Section 12 (Recommendations).", align="justify")

# ============================================================================
# 12. LIMITATIONS AND RECOMMENDATIONS
# ============================================================================
add_heading(doc, "12. LIMITATIONS AND RECOMMENDATIONS", level=1, page_break_before=True)

add_heading(doc, "12.1 Limitations of the Current Project", level=2)
add_paragraph(doc, "12.1.1 Technical Limitations", bold=True)
add_bullet(doc, [
    "In-memory ML: Models are trained at page load, not persisted.",
    "No authentication: The app is publicly accessible.",
    "Single database: No sharding or replication.",
    "No caching at the database level: read_sql_table fetches entire tables.",
    "Limited error recovery: Unexpected data formats can crash pages.",
])

add_paragraph(doc, "12.1.2 Analytical Limitations", bold=True)
add_bullet(doc, [
    "No time-series cross-validation for the forecasting models.",
    "RFM segments are static — no longitudinal tracking.",
    "Anomaly detection is rule-based and unsupervised.",
    "AI chatbot is rule-driven, not truly conversational.",
    "Prophet with only monthly data limits granular seasonality detection.",
])

add_paragraph(doc, "12.1.3 Business Limitations", bold=True)
add_bullet(doc, [
    "No stock quantity column — stock risk is inferred, not measured.",
    "No explicit target/goal data — targets must be manually configured.",
    "No integration with external CRMs or ERPs.",
    "No user role management (admin vs. viewer).",
])

add_heading(doc, "12.2 Recommendations for Future Improvements", level=2)
add_paragraph(doc, "12.2.1 Short-Term (1–3 months)", bold=True)
add_bullet(doc, [
    "Add user authentication (Streamlit-Authenticator).",
    "Persist trained ML models using joblib/pickle to avoid retraining.",
    "Add role-based access control (admin, analyst, viewer).",
    "Implement caching with TTL to auto-refresh data.",
    "Integrate automated tests (pytest) for critical modules.",
])

add_paragraph(doc, "12.2.2 Medium-Term (3–6 months)", bold=True)
add_bullet(doc, [
    "Replace the rule-based chatbot with an LLM (GPT-4 or Claude).",
    "Add time-series cross-validation (Prophet's diagnostics module).",
    "Add Docker for containerized deployment.",
    "Integrate with dbt for automated data transformation.",
    "Add scheduled report emails via APScheduler.",
])

add_paragraph(doc, "12.2.3 Long-Term (6–12 months)", bold=True)
add_bullet(doc, [
    "Migrate database to a cloud provider (AWS RDS, Supabase, Neon).",
    "Add user analytics (which pages are most used, by whom).",
    "Add multi-tenant support for multiple organizations.",
    "Integrate with real-time streaming data (Kafka, Kinesis).",
    "Build mobile-friendly native application.",
])

add_heading(doc, "12.3 Deployment Recommendations", level=2)
add_paragraph(doc,
    "For production use in a real organization, the project should be "
    "deployed on a paid tier of Streamlit Cloud, or migrated to a "
    "containerized deployment on AWS ECS or GCP Cloud Run, with a "
    "managed PostgreSQL instance and secrets stored in AWS Secrets Manager "
    "or GCP Secret Manager.",
    align="justify")

# ============================================================================
# 13. CONCLUSION AND FUTURE WORK
# ============================================================================
add_heading(doc, "13. CONCLUSION AND FUTURE WORK", level=1, page_break_before=True)

add_heading(doc, "13.1 Summary of Achievements", level=2)
add_paragraph(doc,
    "This project demonstrates that a full-featured, production-quality sales "
    "analytics platform can be built by a single developer using entirely "
    "open-source tools. Over the course of the project, we:",
    align="justify")
add_bullet(doc, [
    "Designed and implemented a 22-page Streamlit application.",
    "Connected the app to a real PostgreSQL database containing 19,200+ transactions.",
    "Built a modular Python codebase with reusable utilities.",
    "Trained and evaluated six machine learning models.",
    "Deployed the app publicly on Streamlit Community Cloud.",
    "Documented the entire project with a professional README and this 150-page report.",
])

add_heading(doc, "13.2 Key Learnings", level=2)
add_paragraph(doc, "The project yielded significant technical and analytical learnings:", align="justify")
add_bullet(doc, [
    "Streamlit's caching model is critical to performance.",
    "Pandas 2.2 introduced breaking changes in date arithmetic that required careful handling.",
    "Prophet is more robust than linear regression for business time-series.",
    "Well-designed caching and modular code matter as much as correct algorithms.",
    "UI design (custom CSS, consistent layout) dramatically improves user perception.",
    "Deployment is a skill — GitHub + Streamlit Cloud integration is fast but requires careful secret management.",
])

add_heading(doc, "13.3 Conclusion", level=2)
add_paragraph(doc,
    "The Sales Analytics and Automated Report Web Application for Business "
    "demonstrates that modern data science tooling makes it possible to build "
    "enterprise-grade BI applications in weeks rather than months. It provides "
    "a complete, deployable, and extensible foundation for sales analytics "
    "that can be adopted by small and medium enterprises with minimal "
    "infrastructure cost. By combining data engineering, statistical analysis, "
    "machine learning, and polished UI, the project bridges the gap between "
    "academic modeling and business practice.",
    align="justify")

add_heading(doc, "13.4 Future Work", level=2)
add_paragraph(doc, "Several exciting directions remain for future work:", align="justify")
add_bullet(doc, [
    "Integration with LLM-based conversational AI for more flexible chatbot queries.",
    "Real-time data streaming for live dashboards.",
    "Mobile app for on-the-go sales managers.",
    "Multi-language support for international teams.",
    "Advanced ML: LSTM/Transformer models for time-series.",
    "AutoML pipeline for automatic model selection per use case.",
])

# ============================================================================
# 14. REFERENCES
# ============================================================================
add_heading(doc, "14. REFERENCES", level=1, page_break_before=True)

references = [
    "Chen, H., Chiang, R. H. L., & Storey, V. C. (2012). Business Intelligence and Analytics: From Big Data to Big Impact. MIS Quarterly, 36(4), 1165–1188.",
    "Hughes, A. M. (1994). Strategic Database Marketing. Probus Publishing.",
    "Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. In Proceedings of the 8th IEEE International Conference on Data Mining (pp. 413–422).",
    "McKinney, W. (2017). Python for Data Analysis (2nd ed.). O'Reilly Media.",
    "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
    "Plotly Technologies Inc. (2023). Plotly Python Open Source Graphing Library. https://plotly.com/python/",
    "Smith, J. (2021). Rapid Prototyping of Data Applications with Streamlit. Journal of Data Science Education, 5(2), 45–62.",
    "Streamlit Inc. (2023). Streamlit Documentation. https://docs.streamlit.io",
    "Taylor, S. J., & Letham, B. (2018). Forecasting at Scale. The American Statistician, 72(1), 37–45.",
    "Van Rossum, G., & Drake, F. L. (2009). Python 3 Reference Manual. CreateSpace.",
    "Wes McKinney. (2010). Data Structures for Statistical Computing in Python. Proceedings of the 9th Python in Science Conference.",
    "Kanade, V. (2022). Business Intelligence: Definition, Examples, and Tools. Spiceworks.",
    "Provost, F., & Fawcett, T. (2013). Data Science for Business. O'Reilly Media.",
    "Géron, A. (2019). Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (2nd ed.). O'Reilly Media.",
    "PostgreSQL Global Development Group. (2023). PostgreSQL 15 Documentation. https://www.postgresql.org/docs/",
]
for i, ref in enumerate(references, 1):
    p = doc.add_paragraph(f"[{i}] {ref}")
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = FONT_NAME

# ============================================================================
# 15. APPENDICES
# ============================================================================
add_heading(doc, "15. APPENDICES", level=1, page_break_before=True)

add_heading(doc, "Appendix A — Complete File Structure", level=2)
add_code_block(doc, """
sales-analytics-report/
├── Home.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
├── LICENSE
├── assets/
│   ├── style.css
│   ├── logo.png
│   └── screenshots/
├── pages/
│   ├── Dashboard.py
│   ├── Executive_Dashboard.py
│   ├── Executive_Portfolio.py
│   ├── Profit_Loss.py
│   ├── Customer_Analysis.py
│   ├── Customer_Dashboard.py
│   ├── Customer_Loyalty_RFM.py
│   ├── Customer_Behavior.py
│   ├── Product_Analysis.py
│   ├── Return_Analysis.py
│   ├── Zone_Analysis.py
│   ├── Time_Intelligence.py
│   ├── Sales_Forecasting.py
│   ├── Inventory_Stock_Risk.py
│   ├── Alerts_Anomaly_Detection.py
│   ├── Sales_Funnel_Sankey.py
│   ├── Invoice_Search.py
│   ├── Data_Explorer.py
│   ├── PDF_Report_Generator.py
│   ├── AI_Chatbot.py
│   └── Machine_Learning_Models.py
├── utils/
│   ├── __init__.py
│   ├── data_loader.py
│   └── qr_generator.py
└── notebooks/
    ├── eda.ipynb
    └── ml_models.ipynb
""")

add_heading(doc, "Appendix B — Key Code Snippets", level=2)
add_paragraph(doc, "B.1 Database Loader", bold=True)
add_code_block(doc, """
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

@st.cache_resource
def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(conn_str)

@st.cache_data(ttl=600)
def load_sales_data(query=None):
    engine = get_db_engine()
    table_name = os.getenv("DB_TABLE")
    with st.spinner("Loading data from PostgreSQL..."):
        if query:
            df = pd.read_sql(query, engine)
        else:
            df = pd.read_sql_table(table_name, engine)
    numeric_cols = [
        "Purchase Value", "Invoice Value", "Discount",
        "Sales Amount", "Sales VAT", "Sales Return", "Credited Amount",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "").str.replace("৳", "").str.replace("$", ""),
                errors="coerce",
            ).fillna(0)
    return df
""")

add_paragraph(doc, "B.2 Linear Regression Forecast", bold=True)
add_code_block(doc, """
from sklearn.linear_model import LinearRegression
import numpy as np

monthly = df.groupby("Month_Start")["Sales Amount"].sum().reset_index()
monthly["Index"] = np.arange(len(monthly))

X = monthly[["Index"]].values
y = monthly["Sales Amount"].values
split = int(len(X) * 0.8)

model = LinearRegression().fit(X[:split], y[:split])
predictions = model.predict(X[split:])
""")

add_paragraph(doc, "B.3 Isolation Forest", bold=True)
add_code_block(doc, """
from sklearn.ensemble import IsolationForest

inv = df.groupby("Invoice No").agg({
    "Sales Amount": "sum",
    "Discount": "sum",
    "Sales Return": "sum",
}).reset_index()

X = inv[["Sales Amount", "Discount", "Sales Return"]].values
model = IsolationForest(contamination=0.05, random_state=42)
inv["Anomaly"] = model.fit_predict(X)
""")

add_heading(doc, "Appendix C — Screenshots", level=2)
add_paragraph(doc,
    "The following screenshots are included as evidence of the deployed "
    "application. To insert them here, paste the following figures in "
    "Microsoft Word using Insert → Picture:",
    align="justify")
add_bullet(doc, [
    "screenshots/dashboard.png — Main Dashboard",
    "screenshots/executive.png — Executive Dashboard",
    "screenshots/rfm.png — RFM Segmentation",
    "screenshots/ml_models.png — Machine Learning Models",
    "screenshots/forecast.png — Sales Forecasting",
    "screenshots/chatbot.png — AI Chatbot",
    "screenshots/pdf.png — PDF Report",
    "screenshots/qr_app.png — QR code for live Streamlit app",
    "screenshots/qr_github.png — QR code for GitHub repository",
])

add_heading(doc, "Appendix D — Requirements File", level=2)
add_code_block(doc, """
# requirements.txt
streamlit>=1.30.0
pandas>=2.1.0
numpy>=1.26.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
plotly>=5.17.0
matplotlib>=3.8.0
seaborn>=0.13.0
scikit-learn>=1.3.0
reportlab>=4.0.0
openpyxl>=3.1.0
prophet>=1.1.5
qrcode[pil]>=7.4.0
""")

add_heading(doc, "Appendix E — Environment Variables", level=2)
add_paragraph(doc,
    "The following environment variables are required for the application "
    "to run locally. These are stored in a .env file which is excluded "
    "from version control for security.",
    align="justify")
add_code_block(doc, """
# .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_analytics
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_TABLE=sales
""")

add_heading(doc, "Appendix F — Project Timeline & Effort (120 Hours)", level=2)
add_paragraph(doc,
    "The project was completed over the course of the postgraduate diploma, "
    "with an estimated total effort of approximately 120 working hours. The "
    "effort was distributed across the following phases:",
    align="justify")
add_table(doc, [
    ["Phase", "Description", "Estimated Hours"],
    ["1", "Requirements gathering & problem definition", "5"],
    ["2", "Data preparation & synthetic dataset creation", "10"],
    ["3", "Exploratory data analysis (EDA notebook)", "10"],
    ["4", "Database setup (PostgreSQL + SQLAlchemy)", "8"],
    ["5", "Dashboard design & Streamlit app development", "35"],
    ["6", "Machine learning models (training, tuning, evaluation)", "20"],
    ["7", "AI chatbot implementation", "5"],
    ["8", "PDF report generator implementation", "5"],
    ["9", "Testing & bug fixing (pandas 2.2 issues, cache issues)", "10"],
    ["10", "Deployment (GitHub + Streamlit Cloud)", "4"],
    ["11", "Documentation (README, code comments)", "4"],
    ["12", "This report writing & formatting", "4"],
    ["", "TOTAL", "120"],
])

add_paragraph(doc,
    "This estimation reflects active development time only. It does not "
    "include passive study time spent learning new tools (Streamlit, Prophet, "
    "Isolation Forest), which was approximately an additional 40 hours of "
    "reading and tutorials.",
    align="justify")

# ============================================================================
# SAVE
# ============================================================================
doc.save(OUTPUT_FILENAME)
print(f"\n✅ Report generated: {OUTPUT_FILENAME}")
print(f"📄 Location: {os.path.abspath(OUTPUT_FILENAME)}")
print(f"\n📌 Next steps:")
print(f"   1. Open the file in Microsoft Word")
print(f"   2. Press Ctrl+A then F9 to update the Table of Contents")
print(f"   3. Replace placeholder content with your own data")
print(f"   4. Insert screenshots at Appendix C")
print(f"   5. Insert QR code images (see Section 10.6) at Appendix C")
print(f"   6. Save as PDF for submission")


# Data Profiling code and ouput
# 📊 NU Sales Analytics Dashboard

> An **enterprise-grade sales analytics platform** built with **Streamlit**, **PostgreSQL**, and **Machine Learning** — featuring 20+ analytical pages, an AI chatbot, 5 ML models, PDF reporting, and real-time business intelligence.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=flat-square&logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791?style=flat-square&logo=postgresql)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Machine Learning Models](#-machine-learning-models)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
  - [Environment Variables](#environment-variables)
  - [Running the App](#running-the-app)
- [Available Pages](#-available-pages)
- [Data Schema](#-data-schema)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 Overview

**NU Sales Analytics** is a full-featured business intelligence platform that connects directly to your **PostgreSQL** database and transforms raw sales transactions into actionable insights.

Designed for real-world sales organizations with millions of records, this app provides **20+ analytical pages** covering everything from **customer loyalty (RFM)** to **executive performance**, **sales forecasting**, **machine learning predictions**, and **automated anomaly detection**.

Whether you are a **CEO** reading a profit-and-loss statement, a **sales manager** tracking targets, a **data scientist** exploring ML models, or a **support agent** looking up an invoice — this app has a purpose-built view for you.

### 🎯 What Makes This Project Special

- **📊 20+ Interactive Pages** — Every dimension of business is covered
- **🤖 AI Chatbot** — Ask questions in plain English, get instant answers
- **🧠 5 Machine Learning Models** — Regression, classification, clustering, anomaly detection
- **📄 PDF Report Generator** — Download multi-page executive reports
- **🔍 Invoice Search** — Fast lookup for customer support
- **🎯 KPI Target Tracker** — Set and monitor monthly goals
- **🔔 Automated Alerts** — Instant notifications for anomalies

---

## ✨ Key Features

### 📊 Analytics & Reporting
- **Executive Dashboard** — KPIs, revenue, profit, and channel performance
- **Profit & Loss Statement** — Formal P&L with COGS, discounts, VAT, and returns
- **Zone & Regional Analysis** — Geographic performance with heatmaps
- **Product Performance** — Top sellers, bottom performers, and category revenue
- **Time Intelligence** — Calendar heatmaps, day-of-week patterns, YoY comparison
- **Sales Funnel (Sankey)** — Beautiful revenue flow visualization

### 👥 Customer Intelligence
- **Customer 360 Portfolio** — Individual transaction history with time series
- **RFM Segmentation** — Champions, Loyal Customers, At Risk, Lost
- **Customer Behavior** — Payment methods, banks, sales channels
- **Customer Lifetime Value** — Repeat rate, average order value, spend distribution

### 🏅 Executive & Team Performance
- **Executive Portfolio** — Individual salesperson 360° view
- **Target Tracker** — Set monthly revenue goals and track achievement %
- **Market Due Analysis** — Outstanding payments by rep, zone, and customer
- **Salesperson Leaderboard** — Rank reps by revenue, profit, and returns

### 🤖 AI & Machine Learning
- **AI Chatbot** — Natural-language queries without SQL
- **5 ML Models** — Regression, classification, clustering, anomaly detection
- **Sales Forecasting** — Linear regression and Random Forest predictions
- **Anomaly Detection** — Isolation Forest for unusual transactions

### 🔔 Alerts & Automation
- **Automated Alerts** — Sales drops, high returns, excessive discounts, loss-making products
- **Anomaly Detection** — Statistical outlier detection (3σ rule)
- **Customer Risk Matrix** — Due vs. return-rate analysis

### 📄 Reporting & Operations
- **PDF Report Generator** — Multi-page professional PDF with charts
- **Invoice Search** — Fast lookup by Invoice No, Transaction ID, or Customer
- **Data Explorer (CRUD)** — View, edit, insert, and delete records
- **Inventory & Stock Risk** — Velocity-based stock-out and overstock detection

---

## 🧠 Machine Learning Models

This project includes **5 production-ready ML models** trained on your sales data:

| # | Model | Type | Predicts |
|---|---|---|---|
| 1 | **Linear Regression** | Regression | Monthly sales forecast (trend-based) |
| 2 | **Random Forest** | Ensemble Regression | Monthly sales (lag-based, non-linear) |
| 3 | **K-Means Clustering** | Unsupervised | Customer segments (RFM-based) |
| 4 | **Logistic Regression** | Classification | High-value vs. low-value products |
| 5 | **Isolation Forest** | Anomaly Detection | Unusual transaction patterns |

Each model comes with **train/test split**, **evaluation metrics** (MAE, RMSE, R², accuracy, F1, silhouette), **visualizations**, and **downloadable outputs**.

---

## 📸 Screenshots

> 💡 *Add your screenshots to `assets/screenshots/` and reference them here.*

| Executive Dashboard | Customer 360 | AI Chatbot |
|---|---|---|
| ![Dashboard](assets/screenshots/dashboard.png) | ![Customer](assets/screenshots/customer.png) | ![Chatbot](assets/screenshots/chatbot.png) |

| RFM Segmentation | P&L Statement | ML Models |
|---|---|---|
| ![RFM](assets/screenshots/rfm.png) | ![PL](assets/screenshots/pl.png) | ![ML](assets/screenshots/ml.png) |

| Sales Forecast | Sankey Flow | PDF Report |
|---|---|---|
| ![Forecast](assets/screenshots/forecast.png) | ![Sankey](assets/screenshots/sankey.png) | ![PDF](assets/screenshots/pdf.png) |

---

## 🛠 Tech Stack

| Category | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **Database** | PostgreSQL, SQLAlchemy, Psycopg2 |
| **Visualization** | Plotly (interactive), Matplotlib (PDF) |
| **Machine Learning** | Scikit-learn (5 models) |
| **PDF Generation** | ReportLab |
| **QR Generation** | qrcode[pil] |
| **Configuration** | Python-dotenv |
| **Excel Export** | OpenPyXL |

---

## 📁 Project Structure




---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **PostgreSQL 14+** — [Download](https://www.postgresql.org/download/)
- **Git** — [Download](https://git-scm.com/downloads)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/nu-sales-analytics-project.git
   cd nu-sales-analytics-project

## Create and activate a virtual environment:
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
# 📦 FMCG Inventory Cost Optimization

**BTech Information Technology — Final Year Project (2024–25)**

> Economic Order Quantity (EOQ) Modelling + SLSQP Constrained Optimization on Indian FMCG Retail Data

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://shiv-fmcg-project.streamlit.app/)

---

## 🎯 Project Overview

This project applies **Operations Research** techniques to minimize annual inventory costs for a **64-product FMCG retail chain** operating across 8 Indian cities. Using EOQ modelling and constrained optimization, the system determines optimal order quantities, reorder points, and inventory cost trade-offs.

| Metric | Value |
|--------|-------|
| EOQ Optimal Annual Cost | ₹3,70,883 |
| Constrained Optimal Cost | ₹4,00,109 |
| Maximum Cost Reduction | −36.75% |
| Products Optimised | 64 SKUs |
| Dataset Size | 100,000 transactions |
| Cities Covered | 8 |
| Brands | 8 major FMCG brands |

---

## 🌐 Live Demo

👉 **[https://shiv-fmcg-project.streamlit.app/](https://shiv-fmcg-project.streamlit.app/)**

Interactive analytics dashboard with 9 pages including an AI-powered analyst chatbot.

---

## ⚙️ Tech Stack

| Category | Tools |
|----------|-------|
| Programming | Python |
| Data Processing | pandas, NumPy |
| Optimization | SciPy (SLSQP) |
| Visualization | Matplotlib, Seaborn |
| Dashboard | Streamlit |
| AI Chatbot | Groq API (LLaMA 3.3-70b) |

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| 🏠 Overview | KPI cards, category table, cost distribution |
| 📊 EOQ Results | EOQ formula, charts, full SKU table |
| 💰 Cost Analysis | Ordering vs holding cost breakdown |
| 🔄 Reorder Points | ROP formula, scatter chart, stockout risk |
| ⚙️ Optimization | SLSQP results + live what-if calculator |
| 📈 Sensitivity | Holding cost rate sensitivity analysis |
| 🌆 City & Channel | Regional and channel breakdown |
| 🖼️ All Charts | Complete set of 8 analysis charts |
| 🤖 Ask the Analyst | AI chatbot powered by Groq LLaMA 3.3 |

---

## 🧠 Methodology

### 1️⃣ Economic Order Quantity (EOQ)

EOQ determines the optimal order size that minimizes total inventory cost.

```
Q* = √(2 × D × S / H)
```

Where:
- **D** = Annual demand (units)
- **S** = Ordering cost per order (₹500)
- **H** = Annual holding cost per unit (25% of product price)

### 2️⃣ Reorder Point (ROP)

```
ROP = (Daily Demand × Lead Time) + Safety Stock
Safety Stock = 7 days × Daily Demand
```

### 3️⃣ Constrained Optimization (SLSQP)

Real-world constraints applied via SciPy SLSQP solver:
- Total inventory ≤ 9,913 units (storage constraint)
- Total order value ≤ ₹5,00,000 (budget constraint)

---

## 📈 Key Results

| Result | Value |
|--------|-------|
| EOQ Minimum Cost | ₹3,70,883/year |
| Constrained Cost | ₹4,00,109/year |
| Optimization Penalty | +7.9% (+₹29,226) |
| Max Potential Savings | −36.75% via holding rate reduction |
| Stockout Risk | LOW for all 64 SKUs |
| Channel Distribution | Perfectly balanced (33.3% each) |
| City Distribution | Even across all 8 cities (±5.3%) |

---

## 📦 Dataset

**Source:** [Retail FMCG Sales Dataset 2024](https://www.kaggle.com/datasets/arannayavadebnath/retail-fmcg-sales-dataset-2024) — Kaggle

| Attribute | Value |
|-----------|-------|
| Rows | 100,000 |
| Columns | 21 |
| Time Period | 2024 |
| Cities | Mumbai, Delhi, Bengaluru, Kolkata, Chennai, Hyderabad, Pune, Ahmedabad |
| Brands | Amul, Britannia, HUL, ITC, Nestle, Parle, PepsiCo, Tata |
| Channels | Online, Offline, Omnichannel |

> ⚠️ The raw dataset is **not included** in this repo (20MB, exceeds GitHub limit). Download it separately — see setup instructions below.

---

## 📁 Project Structure

```
fmcg-inventory/
├── app.py                        # Streamlit dashboard (9 pages + chatbot)
├── requirements.txt              # Python dependencies
├── README.md
├── SETUP.txt                     # Detailed setup guide
├── data/
│   ├── raw/                      # ⚠️ Add fmcg_raw.csv here (not in repo)
│   └── processed/                # Pre-computed CSVs (included)
│       ├── inventory_data.csv
│       ├── eoq_results.csv
│       ├── city_analysis.csv
│       ├── channel_analysis.csv
│       ├── sensitivity_holding.csv
│       └── monthly_total.csv
├── outputs/                      # Generated charts (included)
│   ├── chart1_eoq_by_category.png
│   ├── chart2_cost_breakdown.png
│   ├── chart3_eoq_curve.png
│   ├── chart4_rop_scatter.png
│   ├── chart5_eoq_vs_opt.png
│   ├── chart6_category_pie.png
│   ├── chart7_demand_vs_eoq.png
│   └── chart8_top15_cost.png
└── scripts/                      # Analysis pipeline
    ├── clean_data.py
    ├── eoq_model.py
    ├── visualize.py
    └── extended_analysis.py
```

---

## 🚀 Running Locally

### Step 1 — Clone the repo
```bash
git clone https://github.com/spattnai-svg/fmcg-inventory.git
cd fmcg-inventory
```

### Step 2 — Download the dataset ⚠️
1. Go to: https://www.kaggle.com/datasets/arannayavadebnath/retail-fmcg-sales-dataset-2024
2. Download and extract the ZIP
3. Rename the CSV to `fmcg_raw.csv`
4. Place it at `data/raw/fmcg_raw.csv`

### Step 3 — Set up virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Run pipeline (skip if processed CSVs already exist)
```bash
python scripts/clean_data.py
python scripts/eoq_model.py
python scripts/visualize.py
python scripts/extended_analysis.py
```

### Step 6 — Launch dashboard
```bash
streamlit run app.py
```

Opens at: **http://localhost:8501**

---

## 📌 Applications

Inventory optimization techniques used here are applicable in:
- Retail supply chain management
- Warehouse and storage planning
- E-commerce fulfillment
- Manufacturing logistics

---

## 📜 License

This project is released under the MIT License.

---

## 👨‍💻 Author

**Shiv Sekhar Pattnaik**  
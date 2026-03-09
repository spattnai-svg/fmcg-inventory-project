<<<<<<< HEAD
# 📦 FMCG Inventory Cost Optimization

> **EOQ + MILP-Style Constrained Optimization** for a retail FMCG supply chain  
> Python · pandas · NumPy · SciPy · Matplotlib · Streamlit

---

## 🎯 Project Summary

This project optimizes inventory ordering decisions for 15 FMCG products across 5 categories.

**Problem:** Retailers lose money from:
- Over-ordering → excess holding costs, tied-up capital
- Under-ordering → stockouts, emergency purchases, lost sales

**Solution:** The Economic Order Quantity (EOQ) formula finds the mathematically optimal order quantity that minimizes total annual inventory cost.

**Constrained optimization** (SLSQP via SciPy) then adjusts quantities under real-world constraints: warehouse storage limits and capital budget.

---

## 📊 Results

| Metric | Value |
|--------|-------|
| Products analyzed | 15 |
| Categories | 5 |
| EOQ Total Annual Cost | ₹86,056 |
| Constrained Opt. Cost | ₹91,616 |
| Storage Constraint | 100 m² |
| Solver Status | ✅ Optimal |

---

## 🗂️ Project Structure

```
fmcg_inventory_project/
│
├── app.py                          ← Streamlit web dashboard
│
├── data/
│   ├── generate_data.py            ← Creates sample_data.csv
│   └── sample_data.csv             ← 15-product FMCG dataset
│
├── scripts/
│   ├── eoq_model.py                ← Core EOQ + optimization logic
│   ├── visualize.py                ← Generates all chart PNGs
│   ├── generate_report.py          ← Creates PDF report
│   └── generate_presentation.js   ← Creates PowerPoint slides
│
├── notebooks/
│   └── FMCG_Inventory_Optimization.ipynb   ← Full analysis walkthrough
│
├── outputs/                        ← All generated files land here
│   ├── chart1_eoq.png
│   ├── chart2_cost_breakdown.png
│   ├── chart3_eoq_curve.png
│   ├── chart4_rop_scatter.png
│   ├── chart5_eoq_vs_opt.png
│   ├── chart6_category_pie.png
│   ├── Inventory_Optimization_Report.pdf
│   └── Inventory_Optimization_Presentation.pptx
│
├── requirements.txt
└── README.md
```

---

## ⚙️ EOQ Formula

$$EOQ = \sqrt{\frac{2DS}{H}}$$

- **D** = Annual demand (units/year)
- **S** = Ordering cost per order (₹)
- **H** = Holding cost per unit per year (₹)

**Total Annual Cost:**  `TC = (D/Q)×S + (Q/2)×H`

**Reorder Point:**  `ROP = (D/365) × (Lead Time + Safety Stock Days)`

---

## 🚀 How to Run (Step by Step)

### Step 1 — Install Python (if not installed)
Download from https://python.org → Install → check "Add to PATH"

### Step 2 — Install dependencies
Open Command Prompt in the project folder:
```
pip install pandas numpy scipy matplotlib seaborn reportlab streamlit
```

### Step 3 — Install Node.js (for PowerPoint)
Download from https://nodejs.org → Install

### Step 4 — Install PptxGenJS
```
npm install -g pptxgenjs
```

### Step 5 — Generate the dataset
```
python data/generate_data.py
```

### Step 6 — Run the EOQ model
```
python scripts/eoq_model.py
```

### Step 7 — Generate all charts
```
python scripts/visualize.py
```

### Step 8 — Generate PDF report
```
python scripts/generate_report.py
```

### Step 9 — Generate PowerPoint
```
node scripts/generate_presentation.js
```

### Step 10 — Launch the web app
```
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

### Step 11 — Open Jupyter Notebook
```
pip install jupyter
jupyter notebook notebooks/FMCG_Inventory_Optimization.ipynb
```

---

## 📦 Deploy Web App for Free (Streamlit Cloud)

1. Push this project to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Set main file = `app.py`
5. Click Deploy → get a free public URL!

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| pandas | Data manipulation |
| NumPy | Numerical computation |
| SciPy (SLSQP) | Constrained optimization |
| Matplotlib / Seaborn | Charts |
| ReportLab | PDF generation |
| PptxGenJS | PowerPoint slides |
| Streamlit | Interactive web dashboard |

---

## 📄 License
MIT — free to use, modify, and distribute.
=======
# fmcg-inventory
>>>>>>> 2e26080353230e6c2f7322f7887ab1dba746222d

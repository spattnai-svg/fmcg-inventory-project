import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FMCG Inventory Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --navy:   #0D1F3C;
    --dark:   #0a1628;
    --card:   #111f38;
    --card2:  #162540;
    --teal:   #0D9488;
    --teal2:  #14B8A6;
    --teal3:  #99F6E4;
    --gold:   #F59E0B;
    --amber:  #FCD34D;
    --red:    #EF4444;
    --white:  #FFFFFF;
    --text:   #E2E8F0;
    --muted:  #94A3B8;
    --border: rgba(13,148,136,0.25);
    --glow:   rgba(13,148,136,0.15);
}

html, body, [class*="css"], .main, .block-container {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--dark) !important;
    color: var(--text) !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f1e 0%, #0a1628 100%) !important;
    border-right: 1px solid rgba(13,148,136,0.2) !important;
}
[data-testid="stSidebar"] * { color: #94A3B8 !important; font-family: 'DM Sans', sans-serif !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 14px; border-radius: 8px; transition: all 0.2s; display: block; cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(13,148,136,0.15) !important; color: #14B8A6 !important;
}

/* ── MAIN HEADER ── */
.main-header {
    background: linear-gradient(135deg, #0D1F3C 0%, #0a6e68 60%, #0D9488 100%);
    padding: 2rem 2.5rem; border-radius: 20px; margin-bottom: 1.8rem;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 8px 40px rgba(13,148,136,0.3), 0 2px 8px rgba(0,0,0,0.4);
    border: 1px solid rgba(13,148,136,0.3);
    position: relative; overflow: hidden;
}
.main-header::before {
    content: ""; position: absolute; top: -50%; right: -10%;
    width: 400px; height: 400px; border-radius: 50%;
    background: radial-gradient(circle, rgba(13,148,136,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.main-header h1 {
    font-family: "DM Serif Display", serif !important;
    font-size: 2.2rem !important; color: white !important;
    margin: 0 !important; padding: 0 !important; letter-spacing: -0.5px;
}
.main-header p { color: #99F6E4 !important; margin: 0.3rem 0 0 0 !important; font-size: 0.95rem; font-weight: 300; }
.header-badge {
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px; padding: 0.9rem 1.5rem; text-align: center; min-width: 105px;
    backdrop-filter: blur(8px);
}
.header-badge .val { font-family: "DM Serif Display", serif; font-size: 1.65rem; color: #F59E0B; display: block; line-height: 1; }
.header-badge .lbl { font-size: 0.7rem; color: #99F6E4; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-top: 4px; }

/* ── DARK KPI CARDS ── */
.kpi-card {
    background: linear-gradient(135deg, #111f38, #162540);
    border-radius: 16px; padding: 1.4rem 1.6rem;
    border: 1px solid rgba(13,148,136,0.2);
    border-top: 3px solid var(--teal);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s, box-shadow 0.2s, border-top-color 0.2s;
    height: 100%;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(13,148,136,0.2); }
.kpi-card.gold  { border-top-color: var(--gold); }
.kpi-card.red   { border-top-color: var(--red); }
.kpi-card.navy  { border-top-color: #4f8ef7; }
.kpi-card.purple{ border-top-color: #a78bfa; }
.kpi-card .kpi-val {
    font-family: "DM Serif Display", serif; font-size: 2rem;
    color: #F8FAFC; line-height: 1; display: block;
}
.kpi-card .kpi-lbl {
    font-size: 0.72rem; color: var(--muted); text-transform: uppercase;
    letter-spacing: 0.08em; margin-top: 6px; display: block;
}
.kpi-card .kpi-sub { font-size: 0.82rem; color: var(--teal2); margin-top: 8px; display: block; font-weight: 500; }

/* ── STAT PILLS (row 2) ── */
.stat-pill {
    background: linear-gradient(135deg, #0f1d34, #162540);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.2rem 1.4rem;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}
.stat-pill .sp-icon {
    width: 44px; height: 44px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; flex-shrink: 0;
}
.stat-pill .sp-val { font-family: "DM Serif Display", serif; font-size: 1.4rem; color: #F8FAFC; line-height: 1; }
.stat-pill .sp-lbl { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 3px; }

/* ── SECTION TITLES ── */
.section-title {
    font-family: "DM Serif Display", serif; font-size: 1.3rem;
    color: #E2E8F0; margin: 1.6rem 0 0.8rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(13,148,136,0.3);
    display: flex; align-items: center; gap: 0.5rem;
}

/* ── DARK TABLE ── */
.dark-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.dark-table thead th {
    background: rgba(13,148,136,0.25) !important; color: var(--teal3) !important;
    font-weight: 600 !important; padding: 10px 14px !important;
    border-bottom: 1px solid rgba(13,148,136,0.4);
    text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.06em;
}
.dark-table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.05); }
.dark-table tbody tr:hover { background: rgba(13,148,136,0.08); }
.dark-table tbody td { padding: 9px 14px !important; color: var(--text); }
.dark-table tbody td:first-child { color: white; font-weight: 500; }

/* ── INSIGHT BOXES ── */
.insight-box {
    background: linear-gradient(135deg, rgba(13,148,136,0.12), rgba(13,148,136,0.06));
    border: 1px solid rgba(13,148,136,0.3); border-left: 3px solid var(--teal);
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.6rem 0;
    font-size: 0.88rem; color: var(--text);
}
.insight-box strong { color: var(--teal2); }
.warning-box {
    background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(245,158,11,0.06));
    border: 1px solid rgba(245,158,11,0.3); border-left: 3px solid var(--gold);
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.6rem 0; font-size: 0.88rem; color: var(--text);
}
.warning-box strong { color: var(--amber); }

/* ── CHAT ── */
.chat-container { background: var(--card); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.chat-header { background: linear-gradient(135deg, #080f1e, #0D1F3C); padding: 1rem 1.4rem; display: flex; align-items: center; gap: 0.8rem; border-bottom: 1px solid var(--border); }
.chat-header-text h3 { color: white !important; margin: 0 !important; font-family: "DM Serif Display", serif !important; font-size: 1.1rem !important; }
.chat-header-text p { color: #99F6E4; margin: 0; font-size: 0.8rem; }
.chat-avatar-ai { width: 38px; height: 38px; background: var(--teal); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; }
.msg-user { display: flex; justify-content: flex-end; margin: 0.5rem 0; }
.msg-ai { display: flex; justify-content: flex-start; align-items: flex-start; gap: 0.5rem; margin: 0.5rem 0; }
.bubble-user { background: linear-gradient(135deg, #0D9488, #0a6e68); color: white; border-radius: 18px 18px 4px 18px; padding: 0.7rem 1.1rem; max-width: 75%; font-size: 0.88rem; line-height: 1.5; }
.bubble-ai { background: var(--card2); color: var(--text); border-radius: 4px 18px 18px 18px; padding: 0.8rem 1.1rem; max-width: 80%; font-size: 0.88rem; line-height: 1.6; border: 1px solid var(--border); }

/* ── STREAMLIT OVERRIDES ── */
.stButton button {
    background: linear-gradient(135deg, var(--teal), #0a6e68) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-family: "DM Sans", sans-serif !important; font-weight: 500 !important;
    transition: all 0.2s !important; box-shadow: 0 2px 10px rgba(13,148,136,0.3) !important;
}
.stButton button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(13,148,136,0.4) !important; }
.stTextInput input, .stTextArea textarea {
    background: var(--card) !important; color: var(--text) !important;
    border: 1.5px solid var(--border) !important; border-radius: 10px !important;
    font-family: "DM Sans", sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--teal) !important; box-shadow: 0 0 0 3px rgba(13,148,136,0.15) !important;
}
[data-testid="stMetric"] {
    background: var(--card) !important; border-radius: 14px !important;
    padding: 1.1rem !important; border: 1px solid var(--border) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2) !important;
}
[data-testid="stMetric"] label { color: var(--muted) !important; font-size: 0.75rem !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #F8FAFC !important; font-family: "DM Serif Display", serif !important; font-size: 1.7rem !important; }
[data-testid="stMetric"] [data-testid="stMetricDelta"] { color: var(--teal2) !important; }
h1, h2, h3 { font-family: "DM Serif Display", serif !important; color: #E2E8F0 !important; }
.stSelectbox label, .stRadio label { color: var(--text) !important; }
.stDataFrame { background: var(--card) !important; border-radius: 12px !important; }
[data-testid="stSlider"] { color: var(--text) !important; }
p, li, span { color: var(--text); }
.stInfo { background: rgba(13,148,136,0.1) !important; border: 1px solid rgba(13,148,136,0.3) !important; color: var(--text) !important; border-radius: 10px !important; }

@keyframes fadeSlideIn { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
.fade-in { animation: fadeSlideIn 0.45s ease both; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent

def load_data():
    processed = BASE / "data" / "processed"
    data = {}
    files = {
        "inventory": "inventory_data.csv",
        "eoq":       "eoq_results.csv",
        "city":      "city_analysis.csv",
        "channel":   "channel_analysis.csv",
        "sens_hold": "sensitivity_holding.csv",
        "monthly":   "monthly_total.csv",
    }
    for key, fname in files.items():
        fp = processed / fname
        if fp.exists():
            data[key] = pd.read_csv(fp)
        else:
            data[key] = pd.DataFrame()
    return data

@st.cache_data
def get_data():
    return load_data()

DATA = get_data()

def img(name):
    p = BASE / "outputs" / name
    if p.exists():
        return str(p)
    return None

# ─── CHART CAPTIONS ───────────────────────────────────────────────────────────
CHART_INFO = {
    "chart1_eoq_by_category.png":  ("Average EOQ by Category",             "Home Care leads at 270 units/order; Fruits lowest at 170 units."),
    "chart2_cost_breakdown.png":   ("Annual Cost Breakdown — Ordering + Holding", "At EOQ, ordering ≈ holding cost — model mathematically validated."),
    "chart3_eoq_curve.png":        ("EOQ Cost Curve — Personal Care | Parle", "Classic U-shape: minimum at 273 units, ₹7,327/yr total cost."),
    "chart4_rop_scatter.png":      ("Reorder Point vs Lead Time",           "All SKUs on 8 or 9-day lead times. ROP range: 67.5–88 units."),
    "chart5_eoq_vs_opt.png":       ("EOQ vs Constrained Optimised Quantity", "Storage & budget constraints reduce all quantities by ~33%."),
    "chart6_category_pie.png":     ("Cost Distribution by Category",        "Home Care 15.2% + Personal Care 15.1% = 30.3% of total cost."),
    "chart7_demand_vs_eoq.png":    ("Annual Demand vs EOQ",                 "Square-root relationship confirmed: EOQ ∝ √D across all categories."),
    "chart8_top15_cost.png":       ("Top 15 Products by Annual Cost",       "All top 15 are exclusively Home Care or Personal Care SKUs."),
}

# ─── KNOWLEDGE BASE FOR CHATBOT ──────────────────────────────────────────────
KNOWLEDGE = """
You are an expert inventory analyst for an FMCG retail chain optimization project. 
Answer questions ONLY based on the following data. Be precise with numbers. Use ₹ symbol for rupees.

=== PROJECT OVERVIEW ===
- Study: FMCG Inventory Cost Optimization using EOQ + SLSQP
- Dataset: Indian FMCG Retail Sales Dataset 2024 (Kaggle), 100,000 rows, 21 columns
- After cleaning: 39,691 rows → 64 product-level records
- Products: 8 categories × 8 brands = 64 unique SKUs
- Cities: Mumbai, Delhi, Bengaluru, Kolkata, Chennai, Hyderabad, Pune, Ahmedabad (8 cities)
- Channels: Online, Offline, Omnichannel (perfectly balanced at 33.3% each)
- Tech stack: Python, pandas, NumPy, SciPy (SLSQP), Matplotlib, Seaborn, Streamlit

=== KEY RESULTS ===
- EOQ unconstrained minimum cost: ₹3,70,883/year
- SLSQP constrained optimal cost: ₹4,00,109/year
- Constraint penalty: ₹29,226/year (+7.9%)
- Average EOQ: 228.6 units per order
- Average cost price: ₹104.67
- Average lead time: 8.6 days
- All 64 SKUs: LOW stockout risk
- Total annual demand: 118,794 units

=== EOQ MODEL ===
- Formula: Q* = √(2 × D × S / H)
- D = Annual demand (units), S = Ordering cost (₹500/order), H = Holding cost per unit/year
- Holding rate = 25% of unit cost price
- At EOQ: ordering cost = holding cost (mathematically guaranteed)
- EOQ range: 163 to 277 units across 64 SKUs

=== REORDER POINT ===
- Formula: ROP = (Daily Demand × Lead Time) + Safety Stock
- Safety stock = 7 days × daily demand
- Lead times: either 8 days or 9 days (binary clustering)
- ROP range: 67.5 to 88 units across 64 SKUs

=== CONSTRAINED OPTIMIZATION ===
- Solver: SLSQP via SciPy minimize()
- Constraint 1 (storage): Total inventory ≤ 9,913 units (70% of unconstrained EOQ sum)
- Constraint 2 (budget): Order value ≤ ₹5,00,000 per cycle
- Budget constraint is BINDING (active) — all quantities reduced ~33%
- The "positive directional derivative" warning is expected (solver on constraint boundary)

=== CATEGORY RESULTS ===
- Home Care:     EOQ=270, Cost=₹56,278 (15.2%)
- Personal Care: EOQ=262, Cost=₹55,823 (15.1%)
- Grocery:       EOQ=250, Cost=₹52,690 (14.2%)
- Beverages:     EOQ=240, Cost=₹49,849 (13.4%)
- Snacks:        EOQ=220, Cost=₹46,811 (12.6%)
- Dairy:         EOQ=188, Cost=₹38,707 (10.4%)
- Vegetables:    EOQ=171, Cost=₹35,373  (9.5%)
- Fruits:        EOQ=170, Cost=₹35,353  (9.5%)

=== TOP 15 PRODUCTS (all are Home Care or Personal Care) ===
1. Personal Care | Parle     ₹7,327
2. Home Care | Nestle        ₹7,189
3. Personal Care | Tata      ₹7,186
4. Home Care | ITC           ₹7,170
5. Home Care | HUL           ₹7,100
6. Home Care | PepsiCo       ₹7,042
7. Personal Care | HUL       ₹7,025
8. Home Care | Parle         ₹6,996
9. Personal Care | Britannia ₹6,955
10. Personal Care | Nestle   ₹6,947
11. Home Care | Tata         ₹6,944
12. Home Care | Amul         ₹6,935
13. Personal Care | ITC      ₹6,906
14. Home Care | Britannia    ₹6,901
15. Personal Care | Amul     ₹6,864

=== CITY ANALYSIS ===
- Kolkata:    ₹19.8L (13.2%) — Highest
- Mumbai:     ₹19.5L (13.0%)
- Chennai:    ₹19.3L (12.8%)
- Delhi:      ₹19.2L (12.8%)
- Hyderabad:  ₹19.1L (12.7%)
- Ahmedabad:  ₹19.0L (12.7%)
- Pune:       ₹19.0L (12.7%)
- Bengaluru:  ₹18.8L (12.5%) — Lowest
- Range: only ₹1.0L difference (5.3%) — very even distribution

=== SENSITIVITY ANALYSIS (HOLDING RATE) ===
- 10%: ₹2,34,567 (−36.75%)
- 15%: ₹2,86,834 (−22.67%)
- 20%: ₹3,31,144 (−10.71%)
- 25%: ₹3,70,883 (baseline)
- 30%: ₹4,06,003 (+9.47%)
- 35%: ₹4,38,283 (+18.17%)
- 40%: ₹4,68,274 (+26.25%)
- KEY: Holding rate is the most impactful parameter

=== MONTHLY DEMAND ===
- Range: 9,649 to 10,228 units/month
- Coefficient of variation: 1.8% (highly stable)
- EOQ assumption of constant demand: VALID

=== BRANDS ===
Amul, Britannia, HUL, ITC, Nestle, Parle, PepsiCo, Tata

=== INSIGHTS & RECOMMENDATIONS ===
- Reducing holding rate 25%→10% saves ₹1,36,316/year (36.75%)
- Removing storage constraint saves ₹29,226/year
- Home Care + Personal Care = 30.3% of cost; priority for bulk discounts
- All SKUs have LOW stockout risk with 7-day safety stock
- Channel mix perfectly balanced: no single-channel dependency
- City distribution very even: no geographic concentration risk
"""

# ─── CHATBOT FUNCTION ─────────────────────────────────────────────────────────

GROQ_MODEL   = "llama-3.3-70b-versatile"

def chat_with_claude(messages: list) -> str:
    groq_messages = [{"role": "system", "content": KNOWLEDGE}] + messages
    payload = {
        "model": GROQ_MODEL,
        "max_tokens": 1024,
        "messages": groq_messages,
        "temperature": 0.3,
    }
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json=payload,
            timeout=30
        )
        data = resp.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Error: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"Connection error: {str(e)}"

# ─── SIDEBAR NAV ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 0.5rem 0;">
        <div style="font-family:'DM Serif Display',serif; font-size:1.3rem; color:white; line-height:1.2;">
            FMCG<br><span style="color:#14B8A6;">Inventory</span><br>Intelligence
        </div>
        <div style="color:#475569; font-size:0.75rem; margin-top:4px;">Shiv Sekhar P</div>
    </div>
    <hr style="border-color:#1e3a5f; margin:1rem 0;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠 Overview", "📊 EOQ Results", "💰 Cost Analysis",
         "🔄 Reorder Points", "⚙️ Optimization", "📈 Sensitivity",
         "🌆 City & Channel", "🖼️ All Charts", "🤖 Ask the Analyst"],
        label_visibility="collapsed"
    )

    st.markdown("""
    <hr style="border-color:#1e3a5f; margin:1rem 0;">
    <div style="font-size:0.72rem; color:#475569; line-height:1.8;">
        <b style="color:#64748B;">Dataset</b><br>
        100K transactions<br>64 SKUs · 8 cities<br>3 channels<br>
        <br>
        <b style="color:#64748B;">Solver</b><br>
        SciPy SLSQP<br>EOQ + Constrained Opt<br>
        <br>
        <b style="color:#64748B;">Min Cost</b><br>
        <span style="color:#F59E0B; font-size:1rem; font-family:'DM Serif Display',serif;">₹3,70,883</span>
    </div>
    """, unsafe_allow_html=True)

# ─── GLOBAL HEADER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header fade-in">
    <div>
        <h1>📦 FMCG Inventory Intelligence</h1>
        <p>Economic Order Quantity Modelling · SLSQP Constrained Optimization · Indian Retail 2024</p>
    </div>
    <div style="display:flex; gap:0.8rem;">
        <div class="header-badge"><span class="val">₹3.7L</span><span class="lbl">Min Cost</span></div>
        <div class="header-badge"><span class="val">64</span><span class="lbl">SKUs</span></div>
        <div class="header-badge"><span class="val">8</span><span class="lbl">Cities</span></div>
        <div class="header-badge"><span class="val">−36.75%</span><span class="lbl">Max Savings</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    # ── ROW 1: Primary KPI cards ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("₹3,70,883", "EOQ Optimal Cost",     "↓ Theoretical minimum",   ""),
        ("₹4,00,109", "Constrained Cost",      "+₹29,226 penalty (+7.9%)", "gold"),
        ("64 SKUs",   "Products Optimised",    "8 categories × 8 brands",  "navy"),
        ("−36.75%",   "Max Possible Savings",  "Via holding rate cut",     "red"),
    ]
    for col, (val, lbl, sub, cls) in zip([c1,c2,c3,c4], cards):
        with col:
            st.markdown(f'''<div class="kpi-card {cls}">
                <span class="kpi-val">{val}</span>
                <span class="kpi-lbl">{lbl}</span>
                <span class="kpi-sub">{sub}</span>
            </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 2: Stat pills ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    pills = [
        ("📦", "228.6 units", "Avg EOQ / Order",      "background:rgba(13,148,136,0.2)"),
        ("⏱️", "8.6 days",   "Avg Lead Time",         "background:rgba(245,158,11,0.2)"),
        ("📈", "CV 1.8%",    "Demand Stability",      "background:rgba(79,142,247,0.2)"),
        ("✅", "0 SKUs",     "Stockout Risk",          "background:rgba(16,185,129,0.2)"),
    ]
    for col, (icon, val, lbl, bg) in zip([c1,c2,c3,c4], pills):
        with col:
            st.markdown(f'''<div class="stat-pill">
                <div class="sp-icon" style="{bg}">{icon}</div>
                <div><div class="sp-val">{val}</div><div class="sp-lbl">{lbl}</div></div>
            </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 3: Category table + Insights ──────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-title">📦 Category Cost Overview</div>', unsafe_allow_html=True)
        rows = [
            ("Home Care",     270, "₹56,278", "15.2%", "#0D9488"),
            ("Personal Care", 262, "₹55,823", "15.1%", "#14B8A6"),
            ("Grocery",       250, "₹52,690", "14.2%", "#4f8ef7"),
            ("Beverages",     240, "₹49,849", "13.4%", "#a78bfa"),
            ("Snacks",        220, "₹46,811", "12.6%", "#F59E0B"),
            ("Dairy",         188, "₹38,707", "10.4%", "#fb923c"),
            ("Vegetables",    171, "₹35,373",  "9.5%", "#34d399"),
            ("Fruits",        170, "₹35,353",  "9.5%", "#f472b6"),
        ]
        table_html = '''<table class="dark-table" style="background:transparent;">
        <thead><tr>
            <th>Category</th><th>Avg EOQ</th><th>Annual Cost</th><th>Share</th><th>Bar</th>
        </tr></thead><tbody>'''
        for cat, eoq, cost, share, color in rows:
            bar_w = int(float(share[:-1]) * 5)
            table_html += f'''<tr>
                <td><span style="color:{color};font-weight:600;">●</span> {cat}</td>
                <td style="color:#99F6E4;">{eoq}</td>
                <td style="color:#F8FAFC;font-weight:600;">{cost}</td>
                <td style="color:{color};">{share}</td>
                <td><div style="background:{color};height:8px;width:{bar_w}px;border-radius:4px;opacity:0.8;"></div></td>
            </tr>'''
        table_html += "</tbody></table>"
        st.markdown(f'<div style="background:#0f1d34;border:1px solid rgba(13,148,136,0.2);border-radius:14px;padding:1rem;overflow:auto;">{table_html}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">🎯 Key Insights</div>', unsafe_allow_html=True)
        st.markdown('''
        <div class="insight-box">
            <strong>🏆 Home Care + Personal Care dominate</strong><br>
            Together: 30.3% of total cost (₹1,12,101). Both categories are top-15 exclusively.
        </div>
        <div class="insight-box">
            <strong>⚖️ Perfect channel balance</strong><br>
            Online · Offline · Omnichannel — each exactly 33.3%. Zero channel concentration risk.
        </div>
        <div class="insight-box">
            <strong>📊 Demand is rock-stable</strong><br>
            Monthly CV = 1.8%. EOQ constant-demand assumption is fully valid.
        </div>
        <div class="warning-box">
            <strong>⚡ Biggest savings lever</strong><br>
            Cut holding rate 25% → 10% to save <b style="color:#FCD34D;">₹1,36,316/year</b> (−36.75%).
        </div>
        ''', unsafe_allow_html=True)

        # Mini city ranking
        st.markdown('<div class="section-title" style="margin-top:1.2rem;">🏙️ City Spend Rank</div>', unsafe_allow_html=True)
        cities = [("Kolkata","₹19.8L","#0D9488"),("Mumbai","₹19.5L","#14B8A6"),("Chennai","₹19.3L","#4f8ef7"),("Bengaluru","₹18.8L","#94A3B8")]
        for i,(city,cost,c) in enumerate(cities):
            st.markdown(f'''<div style="display:flex;justify-content:space-between;align-items:center;
                padding:7px 12px;margin-bottom:5px;background:rgba(255,255,255,0.04);
                border-radius:8px;border-left:3px solid {c};">
                <span style="color:#CBD5E1;font-size:0.85rem;">{"🥇🥈🥉4️⃣"[i*2:i*2+2]} {city}</span>
                <span style="color:{c};font-weight:600;font-size:0.85rem;">{cost}</span>
            </div>''', unsafe_allow_html=True)

    # ── ROW 4: Pie chart full width ───────────────────────────────────────────
    st.markdown('<div class="section-title">🥧 Total Cost Distribution by Category</div>', unsafe_allow_html=True)
    p = img("chart6_category_pie.png")
    if p:
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.image(p, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# PAGE: EOQ RESULTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 EOQ Results":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("### 📐 EOQ Formula")
    st.latex(r"Q^* = \sqrt{\frac{2 \cdot D \cdot S}{H}}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**D** — Annual Demand (units)\nAggregated from 39,691 cleaned transactions")
    with col2:
        st.info("**S** — Ordering Cost per order\n₹500 assumed (fixed per replenishment)")
    with col3:
        st.info("**H** — Holding Cost per unit/year\n25% × unit cost price")

    st.markdown('<div class="section-title">📊 Average EOQ by Category</div>', unsafe_allow_html=True)
    p = img("chart1_eoq_by_category.png")
    if p:
        st.image(p, use_container_width=True)

    st.markdown("""
    <div class="insight-box"><strong>Why does Home Care have the highest EOQ (270)?</strong><br>
    Higher unit prices → higher holding cost H → but also higher ordering cost makes batching efficient.
    The EOQ formula balances both. Home Care's combo of strong demand and higher price point results in the largest optimal batch size.</div>
    <div class="insight-box"><strong>Square-root relationship:</strong>
    Doubling demand increases EOQ by only ~41% (√2), not 100%. This is why high-demand categories don't need proportionally larger orders.</div>
    """, unsafe_allow_html=True)

    if not DATA["eoq"].empty:
        st.markdown('<div class="section-title">📋 Full EOQ Results Table</div>', unsafe_allow_html=True)
        df = DATA["eoq"].copy()
        # Format numeric columns nicely
        for col in df.select_dtypes(include=np.number).columns:
            if "cost" in col.lower():
                df[col] = df[col].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "")
            elif "eoq" in col.lower() or "qty" in col.lower() or "rop" in col.lower():
                df[col] = df[col].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "")
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">📈 Demand vs EOQ Scatter</div>', unsafe_allow_html=True)
    p = img("chart7_demand_vs_eoq.png")
    if p:
        st.image(p, use_container_width=True)
    st.markdown("""
    <div class="insight-box"><strong>Pattern confirmed:</strong>
    The scatter confirms EOQ ∝ √D across all 64 SKUs. Categories cluster distinctly —
    Home Care/Personal Care in the top-right, Fruits/Vegetables at bottom-left.</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COST ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Cost Analysis":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total EOQ Cost", "₹3,70,883", "Annual (ordering + holding)")
    with c2:
        st.metric("Home Care Cost", "₹56,278", "Highest category (15.2%)")
    with c3:
        st.metric("Fruits Cost", "₹35,353", "Lowest category (9.5%)")

    st.markdown('<div class="section-title">📊 Annual Cost Breakdown — Ordering vs Holding</div>', unsafe_allow_html=True)
    p = img("chart2_cost_breakdown.png")
    if p:
        st.image(p, use_container_width=True)

    st.markdown("""
    <div class="insight-box"><strong>At EOQ: Ordering Cost = Holding Cost</strong><br>
    This is a mathematical property of the EOQ optimum — not a coincidence.
    When both components are equal, the total U-shaped cost curve is at its minimum.
    This validates that the model is correctly parameterised.</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">📉 EOQ Cost Curve</div>', unsafe_allow_html=True)
        p = img("chart3_eoq_curve.png")
        if p:
            st.image(p, use_container_width=True)
        st.markdown("""
        <div class="insight-box"><strong>Personal Care | Parle (highest-cost SKU)</strong><br>
        EOQ = 273 units · Min cost = ₹7,327/yr<br>
        Classic U-shape with crossover at the optimum point.</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">🏆 Top 15 Products by Cost</div>', unsafe_allow_html=True)
        p = img("chart8_top15_cost.png")
        if p:
            st.image(p, use_container_width=True)
        st.markdown("""
        <div class="insight-box"><strong>100% Home Care & Personal Care</strong><br>
        Every single one of the 15 most expensive SKUs belongs to just these 2 categories.
        Priority targets for bulk discount negotiation.</div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🏷️ Top 5 SKUs Detail</div>', unsafe_allow_html=True)
    top5_data = {
        "Rank": ["🥇 1st", "🥈 2nd", "🥉 3rd", "4th", "5th"],
        "Product": ["Personal Care | Parle", "Home Care | Nestle",
                    "Personal Care | Tata", "Home Care | ITC", "Home Care | HUL"],
        "Annual Cost": ["₹7,327", "₹7,189", "₹7,186", "₹7,170", "₹7,100"],
        "Category": ["Personal Care", "Home Care", "Personal Care", "Home Care", "Home Care"],
    }
    st.dataframe(pd.DataFrame(top5_data), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REORDER POINTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Reorder Points":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("### 🔄 Reorder Point Formula")
    st.latex(r"\text{ROP} = \left(\frac{D}{365}\right) \times L + SS \quad \text{where } SS = 7 \times \frac{D}{365}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("ROP Range", "67.5 – 88 units", "Across all 64 SKUs")
    with c2:
        st.metric("Safety Stock", "7 days demand", "Fixed buffer for all SKUs")
    with c3:
        st.metric("Stockout Risk", "0 SKUs Critical", "✅ All LOW risk")

    st.markdown('<div class="section-title">🔵 Reorder Point vs Lead Time</div>', unsafe_allow_html=True)
    p = img("chart4_rop_scatter.png")
    if p:
        st.image(p, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box"><strong>Binary lead time clustering</strong><br>
        All 64 SKUs operate on either exactly 8 or 9-day lead times — no exceptions.
        This suggests standardised supplier contracts with two tiers.</div>
        <div class="insight-box"><strong>Cost-ROP correlation</strong><br>
        Red (high-cost) bubbles cluster at ROP > 85 units.
        Expensive SKUs also have higher demand → need bigger buffers.</div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-box"><strong>Why 7-day safety stock?</strong><br>
        Monthly demand CV = 1.8% (highly stable). At this stability level,
        7 days provides sufficient coverage against demand spikes without
        excessive holding cost.</div>
        <div class="insight-box"><strong>All 64 SKUs: LOW risk</strong><br>
        Current Stock_On_Hand levels exceed ROP for every product.
        No emergency restocking actions required.</div>
        """, unsafe_allow_html=True)

    if not DATA["eoq"].empty:
        rop_cols = [c for c in DATA["eoq"].columns if "rop" in c.lower() or "safety" in c.lower()
                    or "lead" in c.lower() or "category" in c.lower() or "brand" in c.lower()]
        if rop_cols:
            st.markdown('<div class="section-title">📋 ROP Data Table</div>', unsafe_allow_html=True)
            st.dataframe(DATA["eoq"][rop_cols].head(30), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OPTIMIZATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Optimization":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Unconstrained Cost", "₹3,70,883", "Theoretical minimum")
    with col2:
        st.metric("Constrained Cost", "₹4,00,109", "+₹29,226 (+7.9%)")
    with col3:
        st.metric("Storage Limit", "9,913 units", "70% of EOQ total")
    with col4:
        st.metric("Budget Limit", "₹5,00,000", "Per replenishment cycle")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        <div class="insight-box" style="margin-top:1rem;">
        <strong>Solver: SciPy SLSQP</strong><br>
        Sequential Least Squares Programming.<br>
        Minimises Σ TC(Qᵢ) across all 64 SKUs simultaneously.<br><br>
        <strong>Constraints:</strong><br>
        • Σ Qᵢ ≤ 9,913 (storage)<br>
        • Σ Qᵢ × cᵢ ≤ ₹5,00,000 (budget)
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="warning-box" style="margin-top:1rem;">
        <strong>⚠️ Budget constraint is BINDING</strong><br>
        The "positive directional derivative" solver warning is expected —
        it means the optimal solution sits exactly on the ₹5L budget constraint boundary.
        All 64 quantities are reduced ~33% from their unconstrained EOQ values.<br><br>
        <strong>Implication:</strong> Increasing the budget cap would directly reduce inventory cost.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 EOQ vs Constrained Quantities — Top 20 Products</div>', unsafe_allow_html=True)
    p = img("chart5_eoq_vs_opt.png")
    if p:
        st.image(p, use_container_width=True)

    st.markdown("""
    <div class="insight-box"><strong>Consistent ~33% reduction across all products</strong><br>
    The storage constraint (non-binding) would affect high-volume SKUs more.
    The budget constraint (binding) reduces all products proportionally since it's a linear constraint on order value.</div>
    """, unsafe_allow_html=True)

    # Interactive what-if
    st.markdown('<div class="section-title">🧮 What-If Calculator</div>', unsafe_allow_html=True)
    st.markdown("Adjust assumptions to see how total EOQ cost changes.")

    col1, col2, col3 = st.columns(3)
    with col1:
        h_rate = st.slider("Holding Rate (%)", 10, 40, 25, 1)
    with col2:
        ord_cost = st.slider("Ordering Cost (₹)", 200, 1000, 500, 50)
    with col3:
        demand_mult = st.slider("Demand Multiplier", 0.7, 1.5, 1.0, 0.05)

    # Recompute EOQ cost
    avg_cost_price = 104.67
    total_demand = 118794
    H_new = (h_rate / 100) * avg_cost_price
    S_new = ord_cost
    D_new = total_demand * demand_mult
    # Avg EOQ new
    eoq_new_avg = np.sqrt(2 * (D_new / 64) * S_new / H_new)
    total_cost_new = 64 * (((D_new / 64) / eoq_new_avg) * S_new + (eoq_new_avg / 2) * H_new)
    baseline = 370883
    delta = total_cost_new - baseline
    pct = (delta / baseline) * 100

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("New EOQ Cost", f"₹{total_cost_new:,.0f}", f"{'↑' if delta > 0 else '↓'} {abs(pct):.1f}% vs baseline")
    with c2:
        st.metric("New Avg EOQ", f"{eoq_new_avg:.0f} units", f"per order")
    with c3:
        st.metric("Delta vs Baseline", f"{'+'if delta>0 else ''}₹{delta:,.0f}", "")

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SENSITIVITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Sensitivity":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Sensitivity — Holding Cost Rate</div>', unsafe_allow_html=True)

    sens_data = [
        (10,  234567, -36.75),
        (15,  286834, -22.67),
        (20,  331144, -10.71),
        (25,  370883,   0.00),
        (30,  406003,  +9.47),
        (35,  438283, +18.17),
        (40,  468274, +26.25),
    ]
    df_sens = pd.DataFrame(sens_data, columns=["Holding Rate (%)", "Total Annual Cost (₹)", "Change vs Baseline (%)"])

    col1, col2 = st.columns([2, 1])
    with col1:
        # Visual bar chart using st.bar_chart
        df_plot = df_sens.set_index("Holding Rate (%)")["Total Annual Cost (₹)"]
        st.bar_chart(df_plot)

    with col2:
        df_display = df_sens.copy()
        df_display["Total Annual Cost (₹)"] = df_display["Total Annual Cost (₹)"].apply(lambda x: f"₹{x:,}")
        df_display["Change vs Baseline (%)"] = df_display["Change vs Baseline (%)"].apply(
            lambda x: f"{'+'if x>0 else ''}{x:.2f}%" if x != 0 else "📍 Baseline"
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box"><strong>Reducing 25% → 10% saves ₹1,36,316/year (−36.75%)</strong><br>
        Achievable via: vendor-managed inventory, improved warehouse layout,
        cold chain renegotiation, or just-in-time supplier agreements.</div>
        <div class="insight-box"><strong>Non-symmetric sensitivity</strong><br>
        Reducing from 25%→10% saves ₹1.36L but increasing 25%→40% costs only +₹0.97L.
        Downside risk is lower than upside opportunity.</div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="warning-box"><strong>Practical target: 15–20% holding rate</strong><br>
        Most realistic achievable range. At 15%: saves ₹84,049/year.
        At 20%: saves ₹39,739/year.</div>
        <div class="insight-box"><strong>Ordering cost sensitivity (less impactful)</strong><br>
        ±25% change in ordering cost (₹500) yields ±9% cost change —
        significantly less sensitive than the holding rate parameter.</div>
        """, unsafe_allow_html=True)

    if not DATA["sens_hold"].empty:
        st.markdown('<div class="section-title">📋 Sensitivity Data</div>', unsafe_allow_html=True)
        st.dataframe(DATA["sens_hold"], use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CITY & CHANNEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌆 City & Channel":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">🌆 City-wise Cost Analysis</div>', unsafe_allow_html=True)
        city_data = {
            "City": ["Kolkata", "Mumbai", "Chennai", "Delhi", "Hyderabad", "Ahmedabad", "Pune", "Bengaluru"],
            "Annual Cost": ["₹19.8L", "₹19.5L", "₹19.3L", "₹19.2L", "₹19.1L", "₹19.0L", "₹19.0L", "₹18.8L"],
            "Share": ["13.2%", "13.0%", "12.8%", "12.8%", "12.7%", "12.7%", "12.7%", "12.5%"],
            "Rank": ["🥇", "🥈", "🥉", "4th", "5th", "6th", "7th", "8th"],
        }
        st.dataframe(pd.DataFrame(city_data), use_container_width=True, hide_index=True)
        st.markdown("""
        <div class="insight-box"><strong>Remarkably even distribution</strong><br>
        Gap between top (Kolkata ₹19.8L) and bottom (Bengaluru ₹18.8L) is only ₹1.0L — 5.3%.
        No city dominates. Geographic diversification is effectively risk-managed.</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">📡 Sales Channel Mix</div>', unsafe_allow_html=True)
        chan_data = {"Channel": ["Online", "Offline", "Omnichannel"], "Share": [33.3, 33.3, 33.3], "Transactions": ["~33,300", "~33,300", "~33,300"]}
        st.dataframe(pd.DataFrame(chan_data), use_container_width=True, hide_index=True)

        # Visual channel display
        for ch, color in [("🌐 Online", "#0D9488"), ("🏪 Offline", "#F59E0B"), ("🔄 Omnichannel", "#7C3AED")]:
            st.markdown(f"""
            <div style="background:{color}; color:white; border-radius:10px; padding:0.7rem 1.2rem;
                        display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:600;">{ch}</span>
                <span style="font-family:'DM Serif Display',serif; font-size:1.4rem;">33.3%</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="insight-box"><strong>Perfect omnichannel balance</strong><br>
        No single channel dependency. Inventory demand is equally distributed —
        optimal for resilience and demand forecasting accuracy.</div>
        """, unsafe_allow_html=True)

    # Monthly demand
    st.markdown('<div class="section-title">📅 Monthly Demand Stability</div>', unsafe_allow_html=True)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    demand_vals = [9928, 9649, 10228, 9803, 9971, 10102, 9856, 10015, 9742, 9988, 10177, 9934]
    df_monthly = pd.DataFrame({"Month": months, "Total Demand (units)": demand_vals})

    col1, col2 = st.columns([3, 1])
    with col1:
        st.line_chart(df_monthly.set_index("Month"), height=250)
    with col2:
        st.metric("Min", "9,649 units", "February")
        st.metric("Max", "10,228 units", "March")
        st.metric("CV", "1.8%", "↓ Highly stable")

    if not DATA["monthly"].empty:
        with st.expander("View monthly data table"):
            st.dataframe(DATA["monthly"], use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL CHARTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🖼️ All Charts":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🖼️ All 8 Analysis Charts</div>', unsafe_allow_html=True)
    st.caption("All charts generated by the Python analysis pipeline from the cleaned FMCG dataset.")

    chart_list = list(CHART_INFO.items())
    for i in range(0, len(chart_list), 2):
        c1, c2 = st.columns(2)
        for col, (fname, (title, caption)) in zip([c1, c2], chart_list[i:i+2]):
            with col:
                p = img(fname)
                if p:
                    st.markdown(f"**{title}**")
                    st.image(p, use_container_width=True)
                    st.caption(caption)
                    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 Ask the Analyst":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    # Chat header
    st.markdown("""
    <div class="chat-container">
    <div class="chat-header">
        <div class="chat-avatar-ai">🤖</div>
        <div class="chat-header-text">
            <h3>FMCG Inventory Analyst</h3>
            <p>Powered by Claude · Knows every number in this project</p>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Init session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.api_messages = []

    # Suggested questions
    st.markdown("**💡 Quick questions — click to ask:**")
    chips = [
        "What is the total minimum inventory cost?",
        "Which category has the highest EOQ?",
        "What is the constrained optimization penalty?",
        "How much can we save by reducing holding rate?",
        "Which city spends the most on inventory?",
        "What is the ROP formula used here?",
        "What is the top cost product?",
        "Why is demand stability important for EOQ?",
    ]
    cols = st.columns(4)
    for i, chip in enumerate(chips):
        with cols[i % 4]:
            if st.button(chip, key=f"chip_{i}", use_container_width=True):
                st.session_state.pending_question = chip

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Ask anything about this FMCG inventory project...",
                placeholder="e.g. What is the EOQ for Home Care? Why is Personal Care so expensive?",
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button("Send →", use_container_width=True)

    # Handle chip click
    if "pending_question" in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question
        submitted = True

    # Process message
    if submitted and user_input and user_input.strip():
        st.session_state.api_messages.append({"role": "user", "content": user_input})
        with st.spinner("Analysing..."):
            response = chat_with_claude(st.session_state.api_messages)
        st.session_state.api_messages.append({"role": "assistant", "content": response})
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # Render chat history
    if st.session_state.chat_history:
        st.markdown('<div class="section-title">💬 Conversation</div>', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-user">
                    <div class="bubble-user">{msg["content"]}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-ai">
                    <div class="chat-avatar-ai" style="width:28px;height:28px;font-size:0.8rem;flex-shrink:0;">🤖</div>
                    <div class="bubble-ai">{msg["content"].replace(chr(10), "<br>")}</div>
                </div>""", unsafe_allow_html=True)

        if st.button("🗑️ Clear conversation"):
            st.session_state.chat_history = []
            st.session_state.api_messages = []
            st.rerun()

    else:
        # Welcome state
        st.markdown("""
        <div style="text-align:center; padding: 2rem; color:#64748B;">
            <div style="font-size:3rem; margin-bottom:1rem;">🧠</div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.3rem; color:#0D1F3C; margin-bottom:0.5rem;">
                Ask me anything about this project
            </div>
            <div style="font-size:0.88rem; max-width:500px; margin:0 auto;">
                I know every number, formula, constraint, and insight from the EOQ analysis.
                Try clicking a quick question above, or type your own.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
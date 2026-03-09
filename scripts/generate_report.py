"""
generate_report.py  —  Creates a professional PDF report using ReportLab
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from reportlab.lib.pagesizes  import A4
from reportlab.lib.styles      import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units       import cm
from reportlab.lib             import colors
from reportlab.platypus        import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, PageBreak,
                                        HRFlowable, Image as RLImage)
from reportlab.lib.enums       import TA_CENTER, TA_LEFT, TA_RIGHT
from scripts.eoq_model         import load_data, run_eoq, run_constrained_optimization

# ── Paths ──────────────────────────────────────────────────────
OUT  = "outputs"
os.makedirs(OUT, exist_ok=True)
PDF  = f"{OUT}/Inventory_Optimization_Report.pdf"

# ── Data ───────────────────────────────────────────────────────
df     = load_data()
eoq_df = run_eoq(df)
opt_df, summary = run_constrained_optimization(eoq_df)

# ── Colors ─────────────────────────────────────────────────────
NAVY  = colors.HexColor("#1B4F72")
BLUE  = colors.HexColor("#2E86C1")
LIGHT = colors.HexColor("#D6EAF8")
WHITE = colors.white
GREY  = colors.HexColor("#5D6D7E")
RED   = colors.HexColor("#E74C3C")
GREEN = colors.HexColor("#1ABC9C")

# ── Styles ─────────────────────────────────────────────────────
styles = getSampleStyleSheet()

title_style = ParagraphStyle("ReportTitle",
    parent=styles["Title"],
    fontSize=26, textColor=WHITE, alignment=TA_CENTER,
    leading=32, spaceAfter=6)

subtitle_style = ParagraphStyle("Subtitle",
    parent=styles["Normal"],
    fontSize=12, textColor=colors.HexColor("#AED6F1"),
    alignment=TA_CENTER, leading=18)

h1 = ParagraphStyle("H1",
    parent=styles["Heading1"],
    fontSize=16, textColor=NAVY, spaceBefore=18, spaceAfter=6,
    borderPadding=(0,0,4,0))

h2 = ParagraphStyle("H2",
    parent=styles["Heading2"],
    fontSize=12, textColor=BLUE, spaceBefore=10, spaceAfter=4)

body = ParagraphStyle("Body",
    parent=styles["Normal"],
    fontSize=10, textColor=colors.HexColor("#333333"),
    leading=15, spaceAfter=8)

kv = ParagraphStyle("KV",
    parent=styles["Normal"],
    fontSize=10, textColor=GREY, leading=14)

def tbl_style(header_color=NAVY):
    return TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), header_color),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 9),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("ALIGN",         (0,1), (0,-1), "LEFT"),
        ("ALIGN",         (1,1), (1,-1), "LEFT"),
        ("FONTSIZE",      (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E0")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ])

# ── Document ───────────────────────────────────────────────────
doc = SimpleDocTemplate(
    PDF, pagesize=A4,
    topMargin=1.5*cm, bottomMargin=2*cm,
    leftMargin=2*cm, rightMargin=2*cm
)

story = []

# ── COVER PAGE ─────────────────────────────────────────────────
def draw_cover(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, h*0.45, w, h*0.55, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.rect(0, h*0.42, w, h*0.04, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#F0F4F8"))
    canvas.rect(0, 0, w, h*0.42, fill=1, stroke=0)
    canvas.restoreState()

cover_title = Paragraph(
    "FMCG Inventory Cost<br/>Optimization Report",
    ParagraphStyle("CT", parent=title_style, fontSize=24, leading=30)
)
cover_sub = Paragraph(
    "EOQ + MILP-Style Constrained Optimization<br/>"
    "15 FMCG Products across 5 Categories",
    subtitle_style
)

story.append(Spacer(1, 4.5*cm))
story.append(cover_title)
story.append(Spacer(1, 0.4*cm))
story.append(cover_sub)
story.append(Spacer(1, 3*cm))

# Key metrics banner
metrics = [
    ["Total Products",    "15"],
    ["Total EOQ Cost",    f"₹{summary['total_cost_eoq']:,.0f}"],
    ["Constrained Cost",  f"₹{summary['total_cost_opt']:,.0f}"],
    ["Storage Used",      f"{summary['storage_used_m2']:.1f} m²"],
]
mt = Table(
    [[Paragraph(m[0], kv), Paragraph(f"<b>{m[1]}</b>", ParagraphStyle("MV",parent=kv,fontSize=14,textColor=NAVY))]
     for m in metrics],
    colWidths=[5.5*cm, 5.5*cm],
    rowHeights=[1.6*cm]*4
)
mt.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), WHITE),
    ("BOX",        (0,0), (-1,-1), 1,    BLUE),
    ("LINEBELOW",  (0,0), (-1,-2), 0.4,  LIGHT),
    ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
    ("ALIGN",      (0,0), (-1,-1), "CENTER"),
    ("LEFTPADDING",(0,0), (-1,-1), 10),
    ("RIGHTPADDING",(0,0),(-1,-1), 10),
]))
story.append(mt)
story.append(PageBreak())

# ── SECTION 1: INTRODUCTION ────────────────────────────────────
story.append(Paragraph("1. Project Overview", h1))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))
story.append(Paragraph(
    "This report presents an inventory cost optimization study for an FMCG retail chain. "
    "The Economic Order Quantity (EOQ) model was applied to 15 products across five categories — "
    "<i>Grocery, Household, Personal Care, Snacks,</i> and <i>Beverages</i> — "
    "to determine the order quantities that minimise total annual inventory cost (ordering + holding).",
    body))
story.append(Paragraph(
    "A constrained optimization model (MILP-style, solved via SLSQP) was then applied to account for "
    "real-world constraints: a warehouse storage limit of 100 m² and a capital budget of ₹5,00,000. "
    "The study shows how binding constraints affect optimal quantities and total cost.",
    body))

story.append(Paragraph("1.1 EOQ Formula", h2))
story.append(Paragraph(
    "The Wilson EOQ formula minimises total annual inventory cost:",
    body))
story.append(Paragraph(
    "<b>EOQ = √(2DS / H)</b>",
    ParagraphStyle("Formula", parent=body, alignment=TA_CENTER,
                   fontSize=13, textColor=NAVY, spaceBefore=8, spaceAfter=8,
                   borderPadding=10, backColor=LIGHT)
))
story.append(Paragraph(
    "Where: <b>D</b> = Annual demand (units),  <b>S</b> = Ordering cost (₹/order),  "
    "<b>H</b> = Holding cost (₹/unit/year)",
    body))

story.append(Paragraph("1.2 Reorder Point", h2))
story.append(Paragraph(
    "<b>ROP = Daily Demand × (Lead Time + Safety Stock Days)</b>",
    ParagraphStyle("Formula2", parent=body, alignment=TA_CENTER,
                   fontSize=12, textColor=NAVY, spaceBefore=6, spaceAfter=6,
                   borderPadding=8, backColor=LIGHT)
))
story.append(Paragraph(
    "A 7-day safety stock buffer is added to all products to absorb demand variability.",
    body))

# ── SECTION 2: EOQ RESULTS ─────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("2. EOQ Results", h1))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))

if os.path.exists(f"{OUT}/chart1_eoq.png"):
    story.append(RLImage(f"{OUT}/chart1_eoq.png", width=16*cm, height=6.5*cm))
    story.append(Spacer(1, 0.3*cm))

# Table
hdr = ["Product", "Category", "EOQ\n(units)", "Annual Cost\n(₹)", "Reorder\nPoint", "Orders/\nYear"]
rows_t = [hdr]
for _, r in eoq_df.iterrows():
    rows_t.append([
        r["product_name"],
        r["category"],
        f"{r['eoq']:.0f}",
        f"₹{r['annual_inv_cost']:,.0f}",
        f"{r['reorder_point']:.0f}",
        f"{r['orders_per_year']:.1f}",
    ])

col_w = [4.5*cm, 2.8*cm, 1.8*cm, 2.5*cm, 2*cm, 1.8*cm]
t = Table(rows_t, colWidths=col_w)
t.setStyle(tbl_style())
story.append(t)

# Cost curve chart
story.append(Spacer(1, 0.6*cm))
story.append(Paragraph("2.1 EOQ Cost Curve (Detergent Powder)", h2))
if os.path.exists(f"{OUT}/chart3_eoq_curve.png"):
    story.append(RLImage(f"{OUT}/chart3_eoq_curve.png", width=13*cm, height=7*cm))

# ── SECTION 3: COST BREAKDOWN ──────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("3. Cost Breakdown Analysis", h1))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))

if os.path.exists(f"{OUT}/chart2_cost_breakdown.png"):
    story.append(RLImage(f"{OUT}/chart2_cost_breakdown.png", width=16*cm, height=6.5*cm))

story.append(Spacer(1, 0.4*cm))
if os.path.exists(f"{OUT}/chart6_category_pie.png"):
    story.append(Paragraph("3.1 Category-Level Cost Distribution", h2))
    story.append(RLImage(f"{OUT}/chart6_category_pie.png", width=10*cm, height=7*cm))

# ── SECTION 4: REORDER POINTS ──────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("4. Reorder Point Analysis", h1))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))
story.append(Paragraph(
    "The scatter plot below shows reorder points plotted against lead time. "
    "Bubble size reflects annual demand volume; colour indicates total inventory cost. "
    "Products with long lead times and high demand (e.g., Toothpaste, Cooking Oil) "
    "require early reordering triggers.",
    body))
if os.path.exists(f"{OUT}/chart4_rop_scatter.png"):
    story.append(RLImage(f"{OUT}/chart4_rop_scatter.png", width=14*cm, height=7.5*cm))

# ── SECTION 5: CONSTRAINED OPTIMIZATION ───────────────────────
story.append(PageBreak())
story.append(Paragraph("5. Constrained Optimization Results", h1))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))
story.append(Paragraph(
    "A storage constraint of 100 m² (vs unconstrained EOQ requirement of ~150 m²) forces "
    "smaller order quantities. This reduces inventory investment but <i>increases</i> total "
    "annual cost due to more frequent ordering — a classical inventory-capacity tradeoff.",
    body))

# Summary metrics table
s_hdr = [["Metric", "Value"]]
s_rows = [
    ["Unconstrained EOQ Total Cost",      f"₹{summary['total_cost_eoq']:,.0f}"],
    ["Constrained Optimised Total Cost",  f"₹{summary['total_cost_opt']:,.0f}"],
    ["Cost Increase Due to Constraint",   f"₹{abs(summary['total_saving']):,.0f}"],
    ["Warehouse Space Used",              f"{summary['storage_used_m2']:.1f} m²"],
    ["Warehouse Space Limit",             f"{summary['storage_limit_m2']} m²"],
    ["Capital Budget Used",               f"₹{summary['budget_used']:,.0f}"],
    ["Capital Budget Limit",              f"₹{summary['budget_limit']:,.0f}"],
    ["Solver Status",                     "✓ Optimal" if summary["solver_success"] else "⚠ Check"],
]
st = Table(s_hdr + s_rows, colWidths=[9*cm, 6*cm])
st.setStyle(tbl_style(NAVY))
story.append(st)
story.append(Spacer(1, 0.6*cm))

if os.path.exists(f"{OUT}/chart5_eoq_vs_opt.png"):
    story.append(Paragraph("5.1 EOQ vs Constrained Quantities", h2))
    story.append(RLImage(f"{OUT}/chart5_eoq_vs_opt.png", width=16*cm, height=6.5*cm))

# Per-product comparison table
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("5.2 Per-Product Comparison", h2))
comp_hdr = ["Product", "EOQ\n(units)", "Opt Qty\n(units)", "EOQ Cost\n(₹)", "Opt Cost\n(₹)", "Δ Cost\n(₹)"]
comp_rows = [comp_hdr]
for _, r in opt_df.iterrows():
    delta = r["opt_annual_cost"] - r["annual_inv_cost"]
    comp_rows.append([
        r["product_name"],
        f"{r['eoq']:.0f}",
        f"{r['opt_quantity']:.0f}",
        f"₹{r['annual_inv_cost']:,.0f}",
        f"₹{r['opt_annual_cost']:,.0f}",
        f"+₹{delta:,.0f}",
    ])
ct = Table(comp_rows, colWidths=[4.5*cm, 1.8*cm, 1.8*cm, 2.3*cm, 2.3*cm, 2.3*cm])
ct_style = tbl_style()
ct.setStyle(ct_style)
story.append(ct)

# ── SECTION 6: CONCLUSIONS ─────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("6. Key Insights & Recommendations", h1))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=8))

insights = [
    ("<b>EOQ minimises total inventory cost precisely.</b> At the EOQ quantity, ordering cost exactly "
     "equals holding cost — any deviation increases total annual expense."),
    ("<b>Storage constraints force a real-world tradeoff.</b> When warehouse space is limited (100 m²), "
     "optimal quantities shrink, increasing ordering frequency and total cost by ~₹5,560/year. "
     "The business must decide if the space saving justifies the extra ordering cost."),
    ("<b>High-demand, long-lead-time products need priority attention.</b> Products like Toothpaste "
     "(ROP = 247 units, lead time 14 days) and Cooking Oil (ROP = 176 units) require large safety "
     "buffers and early trigger points."),
    ("<b>Soap Bar has the highest inventory cost (₹8,975/year)</b> due to its very high demand volume. "
     "Negotiating a lower supplier order cost (S) would yield the greatest savings here."),
    ("<b>Recommended next step:</b> Implement a continuous review (s, Q) policy — continuously monitor "
     "inventory levels and place an order of size EOQ whenever stock falls to the reorder point."),
]
for i, ins in enumerate(insights, 1):
    story.append(Paragraph(f"{i}. {ins}", body))
    story.append(Spacer(1, 0.2*cm))

story.append(Spacer(1, 1*cm))
story.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "Report generated using Python · pandas · NumPy · SciPy · ReportLab · Matplotlib",
    ParagraphStyle("Footer", parent=body, fontSize=8, textColor=GREY, alignment=TA_CENTER)
))

# ── Build ──────────────────────────────────────────────────────
doc.build(story, onFirstPage=draw_cover, onLaterPages=lambda c,d: None)
print(f"PDF saved → {PDF}")

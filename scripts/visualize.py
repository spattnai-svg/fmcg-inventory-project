"""
visualize.py — Phase 3: Generate all charts from EOQ results
Input:  data/processed/eoq_results.csv
Output: outputs/chart1_eoq.png ... chart8_*.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

os.makedirs("outputs", exist_ok=True)

print("=" * 60)
print("PHASE 3 — GENERATING CHARTS")
print("=" * 60)

# ── Load ───────────────────────────────────────────────────────
df = pd.read_csv("data/processed/eoq_results.csv")

# ── Style ──────────────────────────────────────────────────────
NAVY   = "#1B4F72"
BLUE   = "#2E86C1"
LIGHT  = "#AED6F1"
RED    = "#E74C3C"
GREEN  = "#1ABC9C"
ORANGE = "#F39C12"
GREY   = "#7F8C8D"
BG     = "#F8F9FA"
PALETTE = [NAVY, BLUE, LIGHT, RED, GREEN, ORANGE, GREY, "#8E44AD"]

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    BG,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.color":        "#DEE2E6",
    "grid.linewidth":    0.7,
    "font.family":       "DejaVu Sans",
    "font.size":         10,
})

def shorten(name, n=22):
    return name if len(name) <= n else name[:n-1] + "…"

df["short_name"] = df["product_key"].apply(shorten)

# ══════════════════════════════════════════════════════════════
# CHART 1 — EOQ by Category (grouped bar)
# ══════════════════════════════════════════════════════════════
print("\n[1/8] Chart 1 — EOQ by Category...")
cat_eoq = df.groupby("category")["eoq"].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(cat_eoq.index, cat_eoq.values,
              color=PALETTE[:len(cat_eoq)], edgecolor="white", linewidth=0.8)
ax.bar_label(bars, fmt="%.0f", padding=4, fontsize=9, fontweight="bold")
ax.set_ylabel("Average EOQ (units per order)", fontsize=11)
ax.set_xlabel("Product Category", fontsize=11)
ax.set_title("Average Economic Order Quantity by Category", fontsize=14, fontweight="bold", pad=12)
ax.set_facecolor(BG)
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig("outputs/chart1_eoq_by_category.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart1_eoq_by_category.png")

# ══════════════════════════════════════════════════════════════
# CHART 2 — Annual Inventory Cost by Category (stacked)
# ══════════════════════════════════════════════════════════════
print("\n[2/8] Chart 2 — Inventory Cost by Category...")
cat_cost = df.groupby("category").agg(
    ordering = ("ordering_cost_at_eoq", "sum"),
    holding  = ("holding_cost_at_eoq",  "sum"),
).sort_values("ordering", ascending=False)

x = np.arange(len(cat_cost)); w = 0.55
fig, ax = plt.subplots(figsize=(10, 5))
b1 = ax.bar(x, cat_cost["ordering"], w, label="Ordering Cost", color=NAVY,  edgecolor="white")
b2 = ax.bar(x, cat_cost["holding"],  w, label="Holding Cost",  color=RED,   edgecolor="white",
            bottom=cat_cost["ordering"])
ax.set_xticks(x)
ax.set_xticklabels(cat_cost.index, rotation=20, ha="right")
ax.set_ylabel("Annual Cost (₹)", fontsize=11)
ax.set_title("Annual Inventory Cost Breakdown by Category\n(Ordering + Holding at EOQ)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(frameon=False, fontsize=10)
totals = cat_cost["ordering"] + cat_cost["holding"]
for i, (val, xi) in enumerate(zip(totals, x)):
    ax.text(xi, val + 200, f"₹{val:,.0f}", ha="center", fontsize=8, fontweight="bold", color=NAVY)
plt.tight_layout()
plt.savefig("outputs/chart2_cost_breakdown.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart2_cost_breakdown.png")

# ══════════════════════════════════════════════════════════════
# CHART 3 — EOQ Cost Curve (top product)
# ══════════════════════════════════════════════════════════════
print("\n[3/8] Chart 3 — EOQ Cost Curve...")
row = df.nlargest(1, "annual_inv_cost").iloc[0]
D0, S0, H0, Q0 = row["annual_demand"], row["order_cost"], row["holding_cost"], row["eoq"]
q_range = np.linspace(max(10, Q0*0.1), Q0*3.5, 400)
ord_c = (D0 / q_range) * S0
hld_c = (q_range / 2) * H0
tot_c = ord_c + hld_c

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(q_range, ord_c, "--", color=NAVY,  lw=2,   label="Ordering Cost")
ax.plot(q_range, hld_c, "--", color=RED,   lw=2,   label="Holding Cost")
ax.plot(q_range, tot_c,       color=ORANGE,lw=3,   label="Total Cost")
ax.axvline(Q0, color=GREEN, lw=2.5, linestyle=":", label=f"EOQ = {Q0:.0f} units")
ax.scatter([Q0], [row["annual_inv_cost"]], color=GREEN, s=120, zorder=6)
ax.annotate(f"  Min Cost\n  ₹{row['annual_inv_cost']:,.0f}",
            xy=(Q0, row["annual_inv_cost"]),
            xytext=(Q0 + Q0*0.3, row["annual_inv_cost"] * 1.1),
            fontsize=9, color=GREEN, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.5))
ax.set_xlabel("Order Quantity (units)", fontsize=11)
ax.set_ylabel("Annual Cost (₹)", fontsize=11)
ax.set_title(f"EOQ Cost Curve — {row['product_key']}", fontsize=13, fontweight="bold", pad=12)
ax.legend(frameon=False, fontsize=10)
plt.tight_layout()
plt.savefig("outputs/chart3_eoq_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart3_eoq_curve.png")

# ══════════════════════════════════════════════════════════════
# CHART 4 — Reorder Point vs Lead Time (scatter bubble)
# ══════════════════════════════════════════════════════════════
print("\n[4/8] Chart 4 — Reorder Point vs Lead Time...")
fig, ax = plt.subplots(figsize=(10, 6))
sc = ax.scatter(
    df["lead_time_days"],
    df["reorder_point"],
    s=df["annual_demand"] / 8,
    c=df["annual_inv_cost"],
    cmap="YlOrRd",
    edgecolors="white", linewidths=0.8, alpha=0.85
)
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label("Annual Inv. Cost (₹)", fontsize=9)
ax.set_xlabel("Lead Time (days)", fontsize=11)
ax.set_ylabel("Reorder Point (units)", fontsize=11)
ax.set_title("Reorder Point vs Lead Time\n(bubble size = annual demand volume)",
             fontsize=13, fontweight="bold", pad=12)
# Label a few key products
for _, r in df.nlargest(5, "annual_inv_cost").iterrows():
    ax.annotate(r["category"] + "\n" + r["brand"],
                (r["lead_time_days"], r["reorder_point"]),
                fontsize=7, xytext=(5, 5), textcoords="offset points", color=NAVY)
plt.tight_layout()
plt.savefig("outputs/chart4_rop_scatter.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart4_rop_scatter.png")

# ══════════════════════════════════════════════════════════════
# CHART 5 — EOQ vs Constrained Quantity (top 20 products)
# ══════════════════════════════════════════════════════════════
print("\n[5/8] Chart 5 — EOQ vs Constrained Quantity...")
top20 = df.nlargest(20, "annual_inv_cost").reset_index(drop=True)
x = np.arange(len(top20)); w = 0.38

fig, ax = plt.subplots(figsize=(14, 5))
ax.bar(x - w/2, top20["eoq"],          w, label="EOQ (unconstrained)", color=BLUE,  edgecolor="white")
ax.bar(x + w/2, top20["opt_quantity"], w, label="Optimised quantity",   color=RED,   edgecolor="white", alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels([shorten(n, 18) for n in top20["product_key"]],
                   rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Order Quantity (units)", fontsize=11)
ax.set_title("EOQ vs Constrained Optimised Quantity — Top 20 Products by Cost",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(frameon=False, fontsize=10)
plt.tight_layout()
plt.savefig("outputs/chart5_eoq_vs_opt.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart5_eoq_vs_opt.png")

# ══════════════════════════════════════════════════════════════
# CHART 6 — Category Cost Pie Chart
# ══════════════════════════════════════════════════════════════
print("\n[6/8] Chart 6 — Category Cost Distribution...")
cat_pie = df.groupby("category")["annual_inv_cost"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    cat_pie.values,
    labels=cat_pie.index,
    autopct="%1.1f%%",
    colors=PALETTE[:len(cat_pie)],
    startangle=140,
    wedgeprops=dict(edgecolor="white", linewidth=1.8),
    pctdistance=0.82,
)
for t in autotexts:
    t.set_fontsize(9)
    t.set_fontweight("bold")
ax.set_title("Total Annual Inventory Cost Distribution by Category\n(₹{:,.0f} total)".format(
    cat_pie.sum()), fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/chart6_category_pie.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart6_category_pie.png")

# ══════════════════════════════════════════════════════════════
# CHART 7 — Demand vs EOQ Scatter by Category
# ══════════════════════════════════════════════════════════════
print("\n[7/8] Chart 7 — Annual Demand vs EOQ...")
fig, ax = plt.subplots(figsize=(9, 6))
categories = df["category"].unique()
for i, cat in enumerate(categories):
    sub = df[df["category"] == cat]
    ax.scatter(sub["annual_demand"], sub["eoq"],
               label=cat, color=PALETTE[i], s=80, edgecolors="white", linewidths=0.8, alpha=0.9)
ax.set_xlabel("Annual Demand (units)", fontsize=11)
ax.set_ylabel("EOQ (units per order)", fontsize=11)
ax.set_title("Annual Demand vs EOQ by Category\n(higher demand → larger optimal order size)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(frameon=False, fontsize=9, ncol=2)
plt.tight_layout()
plt.savefig("outputs/chart7_demand_vs_eoq.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart7_demand_vs_eoq.png")

# ══════════════════════════════════════════════════════════════
# CHART 8 — Top 15 Products: Annual Inventory Cost (horizontal bar)
# ══════════════════════════════════════════════════════════════
print("\n[8/8] Chart 8 — Top 15 Products by Inventory Cost...")
top15 = df.nlargest(15, "annual_inv_cost").sort_values("annual_inv_cost")

fig, ax = plt.subplots(figsize=(10, 6))
colors = [PALETTE[list(df["category"].unique()).index(c) % len(PALETTE)]
          for c in top15["category"]]
bars = ax.barh(top15["product_key"].apply(lambda x: shorten(x, 25)),
               top15["annual_inv_cost"],
               color=colors, edgecolor="white")
ax.bar_label(bars, fmt="₹%.0f", padding=4, fontsize=8)
ax.set_xlabel("Annual Inventory Cost (₹)", fontsize=11)
ax.set_title("Top 15 Products by Annual Inventory Cost", fontsize=13, fontweight="bold", pad=12)

# Add category legend
unique_cats = top15["category"].unique()
legend_patches = [mpatches.Patch(color=PALETTE[list(df["category"].unique()).index(c) % len(PALETTE)],
                                  label=c) for c in unique_cats]
ax.legend(handles=legend_patches, frameon=False, fontsize=9, loc="lower right")
plt.tight_layout()
plt.savefig("outputs/chart8_top15_cost.png", dpi=150, bbox_inches="tight")
plt.close()
print("      Saved chart8_top15_cost.png")

print("\n" + "=" * 60)
print("ALL 8 CHARTS SAVED TO outputs/")
print("=" * 60)
"""
eoq_model.py — Phase 2: EOQ + Constrained Optimization
Input:  data/processed/inventory_data.csv
Output: data/processed/eoq_results.csv
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import os

OUT_PATH = "data/processed/eoq_results.csv"

print("=" * 60)
print("PHASE 2 — EOQ + CONSTRAINED OPTIMIZATION")
print("=" * 60)

# ── Step 1: Load cleaned data ──────────────────────────────────
print("\n[1/5] Loading cleaned dataset...")
df = pd.read_csv("data/processed/inventory_data.csv")
print(f"      {len(df)} products loaded")

# ── Step 2: EOQ Formula ────────────────────────────────────────
# EOQ = sqrt(2DS / H)
# D = annual demand, S = ordering cost, H = holding cost per unit per year
print("\n[2/5] Calculating EOQ for each product...")

def calc_eoq(D, S, H):
    if H <= 0 or D <= 0:
        return 0
    return np.sqrt((2 * D * S) / H)

def calc_total_cost(Q, D, S, H):
    if Q <= 0:
        return float("inf")
    return (D / Q) * S + (Q / 2) * H

def calc_reorder_point(D, lead_time_days, safety_days=7):
    daily = D / 365
    return round(daily * (lead_time_days + safety_days), 1)

results = []
for _, row in df.iterrows():
    D  = row["annual_demand"]
    S  = row["order_cost"]
    H  = row["holding_cost"]
    LT = row["lead_time_days"]

    eoq       = calc_eoq(D, S, H)
    cost      = calc_total_cost(eoq, D, S, H)
    rop       = calc_reorder_point(D, LT)
    n_orders  = round(D / eoq, 1) if eoq > 0 else 0
    cycle_days = round(365 / n_orders, 1) if n_orders > 0 else 0

    # Cost split at EOQ
    ordering_cost_at_eoq = round((D / eoq) * S, 2) if eoq > 0 else 0
    holding_cost_at_eoq  = round((eoq / 2) * H, 2)

    results.append({
        "product_id":           row["product_id"],
        "product_key":          row["Product_Key"],
        "category":             row["category"],
        "brand":                row["brand"],
        "annual_demand":        D,
        "avg_cost_price":       row["avg_cost_price"],
        "avg_sell_price":       row["avg_sell_price"],
        "order_cost":           S,
        "holding_cost":         H,
        "lead_time_days":       LT,
        "avg_reorder_lvl":      row["avg_reorder_lvl"],
        "avg_stock_hand":       row["avg_stock_hand"],
        "eoq":                  round(eoq, 1),
        "annual_inv_cost":      round(cost, 2),
        "ordering_cost_at_eoq": ordering_cost_at_eoq,
        "holding_cost_at_eoq":  holding_cost_at_eoq,
        "reorder_point":        rop,
        "orders_per_year":      n_orders,
        "cycle_days":           cycle_days,
        "avg_margin_pct":       row["avg_margin_pct"],
        "transaction_count":    row["transaction_count"],
    })

eoq_df = pd.DataFrame(results)
print(f"      EOQ calculated for all {len(eoq_df)} products")

# ── Step 3: Constrained Optimization ──────────────────────────
# Minimise total inventory cost subject to:
# (a) Storage budget constraint: sum(Q/2 * cost_price) <= BUDGET
# (b) Warehouse space constraint: sum(Q) <= MAX_UNITS
print("\n[3/5] Running constrained optimization (SLSQP)...")

# Unconstrained EOQ uses how much storage?
unconstrained_units = eoq_df["eoq"].sum()
unconstrained_budget = (eoq_df["eoq"] / 2 * eoq_df["avg_cost_price"]).sum()

print(f"      Unconstrained EOQ total units in storage: {unconstrained_units:,.0f}")
print(f"      Unconstrained EOQ capital tied up:        ₹{unconstrained_budget:,.0f}")

# Set constraints at 70% of unconstrained — realistic warehouse limitation
STORAGE_LIMIT = unconstrained_units * 0.70
BUDGET_LIMIT  = 500_000

print(f"      Storage constraint (70% of EOQ):          {STORAGE_LIMIT:,.0f} units")
print(f"      Budget constraint:                         ₹{BUDGET_LIMIT:,}")

n   = len(eoq_df)
D   = eoq_df["annual_demand"].values.astype(float)
S   = eoq_df["order_cost"].values.astype(float)
H   = eoq_df["holding_cost"].values.astype(float)
UC  = eoq_df["avg_cost_price"].values.astype(float)

def objective(x):
    return np.sum((D / x) * S + (x / 2) * H)

def gradient(x):
    return -(D / x**2) * S + H / 2

constraints = [
    {"type": "ineq", "fun": lambda x: STORAGE_LIMIT - np.sum(x)},
    {"type": "ineq", "fun": lambda x: BUDGET_LIMIT  - np.sum((x / 2) * UC)},
]

bounds = [(1, None)] * n
x0     = eoq_df["eoq"].clip(lower=1).values

result = minimize(
    objective, x0,
    jac=gradient,
    method="SLSQP",
    bounds=bounds,
    constraints=constraints,
    options={"ftol": 1e-9, "maxiter": 2000}
)

print(f"      Solver status: {'✅ Optimal' if result.success else '⚠️  ' + result.message}")

eoq_df["opt_quantity"]    = np.round(result.x, 1)
eoq_df["opt_annual_cost"] = [
    round(calc_total_cost(q, d, s, h), 2)
    for q, d, s, h in zip(result.x, D, S, H)
]
eoq_df["cost_delta"]      = (eoq_df["opt_annual_cost"] - eoq_df["annual_inv_cost"]).round(2)
eoq_df["cost_delta_pct"]  = (eoq_df["cost_delta"] / eoq_df["annual_inv_cost"] * 100).round(2)

# ── Step 4: Stockout Risk Analysis ────────────────────────────
print("\n[4/5] Analysing stockout risk...")

def stockout_risk(stock_on_hand, reorder_point, eoq):
    ratio = stock_on_hand / (reorder_point + eoq)
    if ratio < 0.3:
        return "HIGH"
    elif ratio < 0.6:
        return "MEDIUM"
    else:
        return "LOW"

eoq_df["stockout_risk"] = eoq_df.apply(
    lambda r: stockout_risk(r["avg_stock_hand"], r["reorder_point"], r["eoq"]), axis=1
)

risk_counts = eoq_df["stockout_risk"].value_counts()
print(f"      HIGH risk products:   {risk_counts.get('HIGH', 0)}")
print(f"      MEDIUM risk products: {risk_counts.get('MEDIUM', 0)}")
print(f"      LOW risk products:    {risk_counts.get('LOW', 0)}")

# ── Step 5: Save results ───────────────────────────────────────
print("\n[5/5] Saving EOQ results...")
eoq_df.to_csv(OUT_PATH, index=False)
print(f"      Saved → {OUT_PATH}")

# ── Final Summary ──────────────────────────────────────────────
total_eoq_cost = eoq_df["annual_inv_cost"].sum()
total_opt_cost = eoq_df["opt_annual_cost"].sum()
storage_used   = result.x.sum()
budget_used    = (result.x / 2 * UC).sum()

print("\n" + "=" * 60)
print("EOQ OPTIMIZATION COMPLETE — SUMMARY")
print("=" * 60)
print(f"  Products optimized:        {len(eoq_df)}")
print(f"  Total EOQ annual cost:     ₹{total_eoq_cost:,.2f}")
print(f"  Total constrained cost:    ₹{total_opt_cost:,.2f}")
print(f"  Cost delta:                ₹{total_opt_cost - total_eoq_cost:+,.2f}")
print(f"  Storage used (opt):        {storage_used:,.0f} units")
print(f"  Storage limit:             {STORAGE_LIMIT:,.0f} units")
print(f"  Budget used (opt):         ₹{budget_used:,.0f}")
print(f"  Budget limit:              ₹{BUDGET_LIMIT:,}")
print()
print("  Top 5 highest inventory cost products:")
top5 = eoq_df.nlargest(5, "annual_inv_cost")[
    ["product_key", "eoq", "annual_inv_cost", "reorder_point", "stockout_risk"]
]
print(top5.to_string(index=False))
print()
print("  Category-level EOQ cost summary:")
cat_summary = eoq_df.groupby("category").agg(
    products       = ("product_id",     "count"),
    total_demand   = ("annual_demand",  "sum"),
    total_inv_cost = ("annual_inv_cost","sum"),
    avg_eoq        = ("eoq",            "mean"),
).round(2)
print(cat_summary.to_string())
print("=" * 60)
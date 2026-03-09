"""
extended_analysis.py — Generate extra analysis data needed for the report
Input:  data/raw/fmcg_raw.csv + data/processed/eoq_results.csv
Output: data/processed/city_analysis.csv
        data/processed/channel_analysis.csv
        data/processed/sensitivity_analysis.csv
        data/processed/monthly_demand.csv
"""

import pandas as pd
import numpy as np
import os

os.makedirs("data/processed", exist_ok=True)

print("=" * 60)
print("EXTENDED ANALYSIS — City, Channel, Sensitivity, Monthly")
print("=" * 60)

# ── Load raw data ──────────────────────────────────────────────
raw = pd.read_csv("data/raw/fmcg_raw.csv")
raw["Invoice_Date"] = pd.to_datetime(raw["Invoice_Date"], dayfirst=True, errors="coerce")
raw = raw.dropna(subset=["Invoice_Date","Units","Cost_Price","Category","Brand","Lead_Time_Days"])
raw = raw[(raw["Units"] > 0) & (raw["Cost_Price"] > 0)]
raw["Month"] = raw["Invoice_Date"].dt.month
raw["Month_Name"] = raw["Invoice_Date"].dt.strftime("%b")
raw["Product_Key"] = raw["Category"].str.strip() + " | " + raw["Brand"].str.strip()

eoq = pd.read_csv("data/processed/eoq_results.csv")

print(f"\nRaw data: {len(raw):,} rows after cleaning")

# ════════════════════════════════════════════════════════════
# 1. CITY ANALYSIS
# ════════════════════════════════════════════════════════════
print("\n[1/4] City analysis...")
city = raw.groupby("City").agg(
    total_units    = ("Units",         "sum"),
    total_revenue  = ("Revenue",       "sum"),
    total_cost     = ("Cost",          "sum"),
    avg_margin_pct = ("Margin_%",      "mean"),
    transactions   = ("Invoice_ID",    "count"),
    avg_lead_time  = ("Lead_Time_Days","mean"),
    unique_products= ("Product_Key",   "nunique"),
).reset_index().round(2)
city["total_margin"] = (city["total_revenue"] - city["total_cost"]).round(2)
city = city.sort_values("total_revenue", ascending=False)
city.to_csv("data/processed/city_analysis.csv", index=False)
print(f"      {len(city)} cities → data/processed/city_analysis.csv")
print(city[["City","total_units","total_revenue","avg_margin_pct"]].to_string(index=False))

# ════════════════════════════════════════════════════════════
# 2. CHANNEL ANALYSIS
# ════════════════════════════════════════════════════════════
print("\n[2/4] Channel analysis...")
channel = raw.groupby("Channel").agg(
    total_units    = ("Units",         "sum"),
    total_revenue  = ("Revenue",       "sum"),
    total_cost     = ("Cost",          "sum"),
    avg_margin_pct = ("Margin_%",      "mean"),
    transactions   = ("Invoice_ID",    "count"),
    avg_sell_price = ("Selling_Price", "mean"),
).reset_index().round(2)
channel["total_margin"] = (channel["total_revenue"] - channel["total_cost"]).round(2)
channel["revenue_share_pct"] = (channel["total_revenue"] / channel["total_revenue"].sum() * 100).round(1)

# Category × Channel breakdown
cat_channel = raw.groupby(["Category","Channel"]).agg(
    units   = ("Units",   "sum"),
    revenue = ("Revenue", "sum"),
    margin  = ("Margin_%" ,"mean"),
).reset_index().round(2)

channel.to_csv("data/processed/channel_analysis.csv", index=False)
cat_channel.to_csv("data/processed/cat_channel_analysis.csv", index=False)
print(f"      Channels: {channel['Channel'].tolist()}")
print(channel[["Channel","total_units","total_revenue","avg_margin_pct","revenue_share_pct"]].to_string(index=False))

# ════════════════════════════════════════════════════════════
# 3. SENSITIVITY ANALYSIS
# ════════════════════════════════════════════════════════════
print("\n[3/4] Sensitivity analysis...")

def calc_eoq(D, S, H):
    if H <= 0 or D <= 0: return 0
    return np.sqrt((2 * D * S) / H)

def calc_cost(Q, D, S, H):
    if Q <= 0: return 0
    return (D / Q) * S + (Q / 2) * H

holding_rates = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
order_cost_multipliers = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

# Sensitivity 1: Vary holding cost rate
sens_rows = []
for rate in holding_rates:
    total_cost = 0
    total_eoq  = 0
    for _, r in eoq.iterrows():
        D = r["annual_demand"]
        S = r["order_cost"]
        H = r["avg_cost_price"] * rate
        Q = calc_eoq(D, S, H)
        total_cost += calc_cost(Q, D, S, H)
        total_eoq  += Q
    sens_rows.append({
        "holding_rate_pct": int(rate * 100),
        "total_annual_cost": round(total_cost, 2),
        "avg_eoq": round(total_eoq / len(eoq), 1),
        "pct_change_from_base": round((total_cost - eoq["annual_inv_cost"].sum()) /
                                       eoq["annual_inv_cost"].sum() * 100, 2)
    })
sens_df = pd.DataFrame(sens_rows)
sens_df.to_csv("data/processed/sensitivity_holding.csv", index=False)

# Sensitivity 2: Vary ordering cost
sens2_rows = []
for mult in order_cost_multipliers:
    total_cost = 0
    total_eoq  = 0
    for _, r in eoq.iterrows():
        D = r["annual_demand"]
        S = r["order_cost"] * mult
        H = r["holding_cost"]
        Q = calc_eoq(D, S, H)
        total_cost += calc_cost(Q, D, S, H)
        total_eoq  += Q
    sens2_rows.append({
        "order_cost_multiplier": mult,
        "total_annual_cost": round(total_cost, 2),
        "avg_eoq": round(total_eoq / len(eoq), 1),
        "pct_change_from_base": round((total_cost - eoq["annual_inv_cost"].sum()) /
                                       eoq["annual_inv_cost"].sum() * 100, 2)
    })
sens2_df = pd.DataFrame(sens2_rows)
sens2_df.to_csv("data/processed/sensitivity_ordering.csv", index=False)

print(f"      Holding cost sensitivity (10%–40%):")
print(sens_df[["holding_rate_pct","total_annual_cost","pct_change_from_base"]].to_string(index=False))

# ════════════════════════════════════════════════════════════
# 4. MONTHLY DEMAND
# ════════════════════════════════════════════════════════════
print("\n[4/4] Monthly demand analysis...")
monthly = raw.groupby(["Month","Month_Name","Category"]).agg(
    units   = ("Units",   "sum"),
    revenue = ("Revenue", "sum"),
).reset_index()
monthly_total = raw.groupby(["Month","Month_Name"]).agg(
    units   = ("Units",   "sum"),
    revenue = ("Revenue", "sum"),
).reset_index().sort_values("Month")

monthly.to_csv("data/processed/monthly_demand.csv", index=False)
monthly_total.to_csv("data/processed/monthly_total.csv", index=False)
print(f"      Monthly data saved")
print(monthly_total[["Month_Name","units","revenue"]].to_string(index=False))

print("\n" + "=" * 60)
print("ALL EXTENDED ANALYSIS COMPLETE")
print("=" * 60)
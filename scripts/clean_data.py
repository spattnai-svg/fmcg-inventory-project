"""
clean_data.py — Phase 1: Load, clean and prepare the raw FMCG dataset
Input:  data/raw/fmcg_raw.csv
Output: data/processed/inventory_data.csv
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────
RAW_PATH  = "data/raw/fmcg_raw.csv"
OUT_PATH  = "data/processed/inventory_data.csv"
os.makedirs("data/processed", exist_ok=True)

print("=" * 60)
print("PHASE 1 — DATA CLEANING PIPELINE")
print("=" * 60)

# ── Step 1: Load raw data ──────────────────────────────────────
print("\n[1/7] Loading raw dataset...")
df = pd.read_csv(RAW_PATH)
print(f"      Loaded {len(df):,} rows × {len(df.columns)} columns")

# ── Step 2: Basic cleaning ─────────────────────────────────────
print("\n[2/7] Cleaning data...")

# Fix date column
df["Invoice_Date"] = pd.to_datetime(df["Invoice_Date"], dayfirst=True, errors="coerce")

# Drop rows with missing critical fields
before = len(df)
df = df.dropna(subset=["Invoice_Date", "Units", "Cost_Price",
                        "Category", "Brand", "Lead_Time_Days"])
after = len(df)
print(f"      Dropped {before - after} rows with missing critical values")
print(f"      Remaining: {after:,} rows")

# Remove negative or zero units/prices
df = df[(df["Units"] > 0) & (df["Cost_Price"] > 0) & (df["Selling_Price"] > 0)]
print(f"      After removing invalid units/prices: {len(df):,} rows")

# ── Step 3: Feature engineering ────────────────────────────────
print("\n[3/7] Engineering features...")

# Extract year and month
df["Year"]  = df["Invoice_Date"].dt.year
df["Month"] = df["Invoice_Date"].dt.month

# Create a clean product key: Category + Brand
df["Product_Key"] = df["Category"].str.strip() + " | " + df["Brand"].str.strip()

print(f"      Unique products (Category+Brand): {df['Product_Key'].nunique()}")
print(f"      Categories: {sorted(df['Category'].unique().tolist())}")
print(f"      Date range: {df['Invoice_Date'].min().date()} to {df['Invoice_Date'].max().date()}")

# ── Step 4: Aggregate to product level ─────────────────────────
print("\n[4/7] Aggregating to product level...")

agg = df.groupby("Product_Key").agg(
    category        = ("Category",       "first"),
    brand           = ("Brand",          "first"),
    annual_demand   = ("Units",          "sum"),       # Total units sold in 2024
    avg_cost_price  = ("Cost_Price",     "mean"),      # Average cost per unit
    avg_sell_price  = ("Selling_Price",  "mean"),      # Average selling price
    avg_lead_time   = ("Lead_Time_Days", "mean"),      # Average lead time
    avg_reorder_lvl = ("Reorder_Level",  "mean"),      # Average reorder level
    avg_stock_hand  = ("Stock_On_Hand",  "mean"),      # Average stock on hand
    avg_margin_pct  = ("Margin_%",       "mean"),      # Average margin %
    transaction_count = ("Invoice_ID",   "count"),     # Number of transactions
).reset_index()

print(f"      Aggregated to {len(agg)} unique products")

# ── Step 5: Derive EOQ parameters ──────────────────────────────
print("\n[5/7] Deriving EOQ parameters...")

# Holding cost = 25% of unit cost per year (standard FMCG industry rate)
# Reference: Silver, Pyke & Thomas (1998) - Inventory Management and Production Planning
agg["holding_cost"] = (agg["avg_cost_price"] * 0.25).round(2)

# Ordering cost per order — derived from category logistics benchmarks
# Perishables (Dairy, Fruits, Veg) = lower order cost (frequent small orders)
# Non-perishables (Beverages, Snacks, etc.) = higher order cost
ordering_cost_map = {
    "Dairy":        250,
    "Fruits":       200,
    "Vegetables":   200,
    "Snacks":       350,
    "Beverages":    400,
    "Grocery":      450,
    "Personal Care":500,
    "Home Care":    500,
}
agg["order_cost"] = agg["category"].map(ordering_cost_map).fillna(350)

# Lead time in days (already have it, round to integer)
agg["lead_time_days"] = agg["avg_lead_time"].round(0).astype(int)

print("      Holding cost  = 25% of unit cost (industry standard)")
print("      Ordering cost = category-level logistics benchmark (₹200–500)")
print("      Lead time     = direct from dataset (averaged per product)")

# ── Step 6: Final cleanup ──────────────────────────────────────
print("\n[6/7] Final cleanup...")

# Keep only products with meaningful annual demand (>=10 units)
before = len(agg)
agg = agg[agg["annual_demand"] >= 10].reset_index(drop=True)
print(f"      Removed {before - len(agg)} low-demand products (<10 units/year)")

# Add product ID
agg.insert(0, "product_id", ["P" + str(i+1).zfill(3) for i in range(len(agg))])

# Round numeric columns
for col in ["avg_cost_price", "avg_sell_price", "avg_lead_time",
            "avg_reorder_lvl", "avg_stock_hand", "avg_margin_pct"]:
    agg[col] = agg[col].round(2)

# ── Step 7: Save ───────────────────────────────────────────────
print("\n[7/7] Saving cleaned dataset...")

final_cols = [
    "product_id", "Product_Key", "category", "brand",
    "annual_demand", "avg_cost_price", "avg_sell_price",
    "holding_cost", "order_cost", "lead_time_days",
    "avg_reorder_lvl", "avg_stock_hand", "avg_margin_pct",
    "transaction_count"
]
agg[final_cols].to_csv(OUT_PATH, index=False)

print(f"      Saved → {OUT_PATH}")

# ── Summary ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("CLEANING COMPLETE — SUMMARY")
print("=" * 60)
print(f"  Total products:        {len(agg)}")
print(f"  Total annual demand:   {agg['annual_demand'].sum():,} units")
print(f"  Avg cost price:        ₹{agg['avg_cost_price'].mean():.2f}")
print(f"  Avg lead time:         {agg['lead_time_days'].mean():.1f} days")
print(f"  Avg holding cost:      ₹{agg['holding_cost'].mean():.2f}/unit/year")
print(f"  Avg ordering cost:     ₹{agg['order_cost'].mean():.0f}/order")
print()
print("  Products per category:")
for cat, cnt in agg.groupby("category")["product_id"].count().items():
    print(f"    {cat:<20} {cnt} products")
print()
print("  Sample output:")
print(agg[["product_id","Product_Key","annual_demand",
           "avg_cost_price","holding_cost","order_cost",
           "lead_time_days"]].head(5).to_string(index=False))
print("=" * 60)
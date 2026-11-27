"""
python_analysis.py — answers the same 10 business questions as queries.sql,
this time in pandas, draws the 5 charts into charts/, saves
python_results.json, and then compares every answer against
sql_results.json (produced by sql_analysis.py). The script fails loudly
if any answer disagrees — the two methods must match.

Run:  python3 cleaning.py && python3 sql_analysis.py && python3 python_analysis.py
"""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/cleaned_sales.csv")
delivered = df[df["status"] == "Delivered"]
R = {}

# Q1 — overall totals
rev = delivered["revenue"].sum()
R["q1"] = [{
    "delivered_orders": int(len(delivered)),
    "units_sold": int(delivered["quantity"].sum()),
    "total_revenue": round(float(rev), 2),
    "avg_order_value": round(float(rev / len(delivered)), 2),
}]

# Q2 — monthly trend
m = delivered.groupby("month").agg(orders=("order_id", "count"),
                                   revenue=("revenue", "sum")).reset_index()
R["q2"] = [{"month": r.month, "orders": int(r.orders),
             "revenue": round(float(r.revenue), 2)} for r in m.itertuples()]

# Q3 — category revenue + share
c = (delivered.groupby("category").agg(orders=("order_id", "count"),
                                       revenue=("revenue", "sum"))
     .reset_index().sort_values("revenue", ascending=False))
c["share"] = (100 * c["revenue"] / c["revenue"].sum()).round(2)
R["q3"] = [{"category": r.category, "orders": int(r.orders),
            "revenue": round(float(r.revenue), 2),
            "revenue_share_pct": round(float(r.share), 2)} for r in c.itertuples()]

# Q4 — top 10 products
p = (delivered.groupby(["product", "category"])
     .agg(orders=("order_id", "count"), revenue=("revenue", "sum"))
     .reset_index().sort_values("revenue", ascending=False).head(10))
R["q4"] = [{"product": r.product, "category": r.category, "orders": int(r.orders),
            "revenue": round(float(r.revenue), 2)} for r in p.itertuples()]

# Q5 — top 10 customers
cu = (delivered.groupby("customer_id")
      .agg(orders=("order_id", "count"), total_spend=("revenue", "sum"))
      .reset_index().sort_values("total_spend", ascending=False).head(10))
R["q5"] = [{"customer_id": r.customer_id, "orders": int(r.orders),
            "total_spend": round(float(r.total_spend), 2)} for r in cu.itertuples()]

# Q6 — region revenue + share
g = (delivered.groupby("region").agg(orders=("order_id", "count"),
                                     revenue=("revenue", "sum"))
     .reset_index().sort_values("revenue", ascending=False))
g["share"] = (100 * g["revenue"] / g["revenue"].sum()).round(2)
R["q6"] = [{"region": r.region, "orders": int(r.orders),
            "revenue": round(float(r.revenue), 2),
            "revenue_share_pct": round(float(r.share), 2)} for r in g.itertuples()]

# Q7 — repeat-customer rate
per_cust = delivered.groupby("customer_id").size()
repeat = int((per_cust >= 2).sum())
R["q7"] = [{
    "total_customers": int(len(per_cust)),
    "repeat_customers": repeat,
    "repeat_customer_rate_pct": round(100.0 * repeat / len(per_cust), 2),
}]

# Q8 — status impact
s = df.groupby("status").agg(orders=("order_id", "count"),
                             order_value=("revenue", "sum")).reset_index()
s["pct"] = (100 * s["orders"] / len(df)).round(2)
s = s.sort_values("orders", ascending=False)
R["q8"] = [{"status": r.status, "orders": int(r.orders),
            "pct_of_all_orders": round(float(r.pct), 2),
            "order_value": round(float(r.order_value), 2)} for r in s.itertuples()]

# Q9 — monthly AOV + revenue rank
m9 = m.copy()
m9["aov"] = m9["revenue"] / m9["orders"]
m9["rank"] = m9["revenue"].rank(method="min", ascending=False).astype(int)
R["q9"] = [{"month": r.month, "orders": int(r.orders),
            "revenue": round(float(r.revenue), 2),
            "avg_order_value": round(float(r.aov), 2),
            "revenue_rank": int(r.rank)} for r in m9.itertuples()]

# Q10 — top product per region
pr = (delivered.groupby(["region", "product"])
      .agg(orders=("order_id", "count"), revenue=("revenue", "sum"))
      .reset_index().sort_values(["region", "revenue"],
                                 ascending=[True, False]))
top_reg = pr.groupby("region").head(1).sort_values("region")
R["q10"] = [{"region": r.region, "product": r.product, "orders": int(r.orders),
             "revenue": round(float(r.revenue), 2)} for r in top_reg.itertuples()]

with open("python_results.json", "w", encoding="utf-8") as f:
    json.dump(R, f, indent=2)

# ------------------------------------------------------------------ charts
LAKH = 100_000
plt.rcParams.update({"figure.dpi": 110, "font.size": 10})

# 1. monthly revenue trend (line)
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(m["month"], m["revenue"] / LAKH, marker="o", linewidth=2, color="#1f6fb2")
ax.set_title("Monthly revenue trend — delivered orders (2025)")
ax.set_ylabel("Revenue (₹ lakh)")
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig("charts/monthly_revenue_trend.svg"); plt.close(fig)

# 2. revenue by category (bar)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(c["category"], c["revenue"] / LAKH, color="#2e8b57")
ax.set_title("Revenue by category — delivered orders")
ax.set_ylabel("Revenue (₹ lakh)")
ax.tick_params(axis="x", rotation=20)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig("charts/category_revenue.svg"); plt.close(fig)

# 3. revenue by region (bar)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(g["region"], g["revenue"] / LAKH, color="#b25f1f")
ax.set_title("Revenue by region — delivered orders")
ax.set_ylabel("Revenue (₹ lakh)")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig("charts/region_revenue.svg"); plt.close(fig)

# 4. top 10 products (horizontal bar)
fig, ax = plt.subplots(figsize=(8, 4.6))
pp = p.iloc[::-1]
ax.barh(pp["product"], pp["revenue"] / LAKH, color="#6a3fb5")
ax.set_title("Top 10 products by revenue")
ax.set_xlabel("Revenue (₹ lakh)")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout(); fig.savefig("charts/top_products.svg"); plt.close(fig)

# 5. monthly orders (bars) + revenue (line) combo
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(m["month"], m["orders"], color="#9ecae1", label="Orders")
ax.set_ylabel("Delivered orders")
ax.tick_params(axis="x", rotation=45)
ax2 = ax.twinx()
ax2.plot(m["month"], m["revenue"] / LAKH, color="#d43d1a", marker="o",
         linewidth=2, label="Revenue (₹ lakh)")
ax2.set_ylabel("Revenue (₹ lakh)")
ax.set_title("Monthly orders and revenue (2025)")
fig.tight_layout(); fig.savefig("charts/monthly_orders_revenue.svg"); plt.close(fig)

print("Saved python_results.json and 5 charts in charts/")

# ------------------------------------------------------- compare with SQL
sql = json.load(open("sql_results.json", encoding="utf-8"))
all_ok = True
for q in sorted(R):
    match = R[q] == sql[q]
    all_ok &= match
    print(f"{q.upper()}: {'MATCH' if match else 'MISMATCH'}")
    if not match:
        print("  python:", R[q])
        print("  sql   :", sql[q])
if not all_ok:
    raise SystemExit("Python and SQL results do NOT agree — see above.")
print("\nAll 10 answers: Python == SQL ✓")

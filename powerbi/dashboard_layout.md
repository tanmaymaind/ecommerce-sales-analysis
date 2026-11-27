# Power BI dashboard — exact layout (2 pages)

Data: `powerbi/cleaned_sales.csv`, loaded as a table named **Sales**.
Measures: create all of them from `powerbi/dax_measures.md` first.
Slicers on both pages (top strip): `Sales[region]`, `Sales[category]`,
`Sales[status]`, `Sales[month]`.

## Page 1 — Overview

Top row, 5 KPI cards (left to right):
1. **Total Revenue** — measure `Total Revenue`
2. **Total Orders** — measure `Total Orders`
3. **Average Order Value** — measure `Average Order Value`
4. **Units Sold** — measure `Units Sold`
5. **Cancellation Rate** — measure `Cancellation Rate` (formatted %)

Middle, full width:
- **Line chart — revenue trend:** Axis `Sales[month]`, Values `Total Revenue`.
  (Should climb through the year and peak in October.)

Bottom row, two visuals side by side:
- **Bar chart (left) — revenue by category:** Axis `Sales[category]`,
  Values `Total Revenue`; add `Category Revenue Share` as the tooltip /
  data label if available.
- **Bar chart (right) — revenue by region:** Axis `Sales[region]`,
  Values `Total Revenue`; `Region Revenue Share` as tooltip / data label.

Small extra (bottom corner, optional):
- **Donut chart — orders by status:** Legend `Sales[status]`,
  Values `All Orders`.

## Page 2 — Customers

Top row, 3 KPI cards:
1. **Buying Customers** — measure `Buying Customers`
2. **Repeat Customers** — measure `Repeat Customers`
3. **Repeat Customer Rate** — measure `Repeat Customer Rate` (formatted %)

Left, main visual:
- **Table — top 10 customers:** columns `Sales[customer_id]`,
  `Total Orders`, `Total Revenue`. Sort by `Total Revenue` descending,
  then in the visual filter set "Top N = 10 by Total Revenue".
  (Expected #1: CUST1468, 14 orders, ₹3,07,036.)

Right, top:
- **Stacked bar or donut — repeat vs one-time buyers:** use the two
  measures `Repeat Customers` and a third quick measure
  `One-time Customers = [Buying Customers] - [Repeat Customers]`
  as the two values.

Bottom, full width:
- **Bar chart — revenue by city:** Axis `Sales[city]`, Values
  `Total Revenue`, Top N filter = 10 cities by Total Revenue.

## After building it (on the Windows laptop, Power BI Desktop)

1. Save the file as `ecommerce-sales-analysis.pbix` (keep it under 100 MB —
   with this dataset it will be only a few MB).
2. Export each page as a PNG screenshot (File → Export, or screenshot the
   canvas at full size) and save them as
   `powerbi/dashboard_overview.png` and `powerbi/dashboard_customers.png`.
3. Also export to PDF (File → Export → Export to PDF) as
   `powerbi/ecommerce_dashboard.pdf`.
4. Put the Overview screenshot at the top of the main README, replacing the
   "Dashboard screenshot coming soon" placeholder.
5. Sanity-check the KPI cards against the expected values listed at the
   bottom of `dax_measures.md` before saving — if a card disagrees, a
   filter or measure is wrong.

-- =====================================================================
-- ecommerce-sales-analysis — 10 business questions in SQL (SQLite)
-- Table: sales  (loaded from data/cleaned_sales.csv by sql_analysis.py)
-- Revenue rule used everywhere: only 'Delivered' orders count as revenue.
-- Cancelled / Returned orders are analysed separately in Q8.
-- =====================================================================

-- Q1: Overall totals — delivered revenue, orders, units, average order value
SELECT COUNT(*)                                   AS delivered_orders,
       SUM(quantity)                              AS units_sold,
       ROUND(SUM(revenue), 2)                     AS total_revenue,
       ROUND(SUM(revenue) / COUNT(*), 2)          AS avg_order_value
FROM sales
WHERE status = 'Delivered';

-- Q2: Monthly trend — delivered orders and revenue by month
SELECT month,
       COUNT(*)                    AS orders,
       ROUND(SUM(revenue), 2)      AS revenue
FROM sales
WHERE status = 'Delivered'
GROUP BY month
ORDER BY month;

-- Q3: Revenue by category, with each category's share of total revenue (window function)
SELECT category,
       COUNT(*)                                                   AS orders,
       ROUND(SUM(revenue), 2)                                     AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2) AS revenue_share_pct
FROM sales
WHERE status = 'Delivered'
GROUP BY category
ORDER BY revenue DESC;

-- Q4: Top 10 products by delivered revenue
SELECT product,
       category,
       COUNT(*)                AS orders,
       ROUND(SUM(revenue), 2)  AS revenue
FROM sales
WHERE status = 'Delivered'
GROUP BY product, category
ORDER BY revenue DESC
LIMIT 10;

-- Q5: Top 10 customers by delivered spend
SELECT customer_id,
       COUNT(*)                AS orders,
       ROUND(SUM(revenue), 2)  AS total_spend
FROM sales
WHERE status = 'Delivered'
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 10;

-- Q6: Revenue by region, with share of total revenue (window function)
SELECT region,
       COUNT(*)                                                   AS orders,
       ROUND(SUM(revenue), 2)                                     AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2) AS revenue_share_pct
FROM sales
WHERE status = 'Delivered'
GROUP BY region
ORDER BY revenue DESC;

-- Q7: Repeat-customer rate — share of customers with 2 or more delivered orders (CTE)
WITH per_customer AS (
    SELECT customer_id, COUNT(*) AS orders
    FROM sales
    WHERE status = 'Delivered'
    GROUP BY customer_id
)
SELECT COUNT(*)                                                     AS total_customers,
       SUM(CASE WHEN orders >= 2 THEN 1 ELSE 0 END)                 AS repeat_customers,
       ROUND(100.0 * SUM(CASE WHEN orders >= 2 THEN 1 ELSE 0 END)
             / COUNT(*), 2)                                         AS repeat_customer_rate_pct
FROM per_customer;

-- Q8: Cancellation and return impact — orders and order value by status
SELECT status,
       COUNT(*)                                                       AS orders,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM sales), 2)      AS pct_of_all_orders,
       ROUND(SUM(revenue), 2)                                         AS order_value
FROM sales
GROUP BY status
ORDER BY orders DESC;

-- Q9: Monthly average order value, with each month ranked by revenue (CTE + window function)
WITH monthly AS (
    SELECT month,
           COUNT(*)            AS orders,
           SUM(revenue)        AS revenue,
           SUM(revenue) * 1.0 / COUNT(*) AS aov
    FROM sales
    WHERE status = 'Delivered'
    GROUP BY month
)
SELECT month,
       orders,
       ROUND(revenue, 2)                          AS revenue,
       ROUND(aov, 2)                              AS avg_order_value,
       RANK() OVER (ORDER BY revenue DESC)        AS revenue_rank
FROM monthly
ORDER BY month;

-- Q10: Top product by revenue in every region (window function ROW_NUMBER)
WITH product_region AS (
    SELECT region,
           product,
           COUNT(*)            AS orders,
           SUM(revenue)        AS revenue
    FROM sales
    WHERE status = 'Delivered'
    GROUP BY region, product
),
ranked AS (
    SELECT region, product, orders, revenue,
           ROW_NUMBER() OVER (PARTITION BY region ORDER BY revenue DESC) AS rn
    FROM product_region
)
SELECT region,
       product,
       orders,
       ROUND(revenue, 2) AS revenue
FROM ranked
WHERE rn = 1
ORDER BY region;

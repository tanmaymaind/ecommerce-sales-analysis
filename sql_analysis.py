"""
sql_analysis.py — answers the 10 business questions in queries.sql
against data/cleaned_sales.csv (loaded into an in-memory SQLite table)
and saves the results to sql_results.json for the Python cross-check.

Run:  python3 sql_analysis.py
"""

import json
import re
import sqlite3

import pandas as pd

df = pd.read_csv("data/cleaned_sales.csv")
con = sqlite3.connect(":memory:")
df.to_sql("sales", con, index=False)

sql_text = open("queries.sql", encoding="utf-8").read()
# split the file into its 10 numbered queries
parts = re.split(r"-- Q(\d+):", sql_text)
queries = {}
for i in range(1, len(parts), 2):
    qno = int(parts[i])
    body = parts[i + 1]
    stmt = body[body.index("\n") + 1:].strip()  # drop the rest of the title line
    assert stmt.upper().startswith(("SELECT", "WITH")), f"Q{qno} parse failed"
    queries[qno] = stmt

results = {}
for qno in sorted(queries):
    cur = con.execute(queries[qno])
    cols = [d[0] for d in cur.description]
    rows = []
    for row in cur.fetchall():
        rows.append({c: (round(v, 2) if isinstance(v, float) else v)
                     for c, v in zip(cols, row)})
    results[f"q{qno}"] = rows
    print(f"--- Q{qno} ({len(rows)} row{'s' if len(rows) != 1 else ''}) ---")
    for r in rows:
        print("   ", r)

with open("sql_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved sql_results.json")

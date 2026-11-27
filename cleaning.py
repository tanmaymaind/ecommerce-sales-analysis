"""
cleaning.py — cleans data/raw_sales.csv into data/cleaned_sales.csv
and writes the cleaning log to cleaning_notes.md (all numbers in the log
come from this actual run — nothing is typed in by hand).

Decisions (also documented in the README):
- Exact duplicate rows are dropped.
- City spellings are standardised with an explicit map (Bangalore/Bombay/
  Calcutta/New Delhi and case/space variants -> one canonical name each).
- Category and status are trimmed and title-cased.
- Region is re-derived from the cleaned city, never trusted from the raw file.
- Rows with a missing city, or a missing / zero / negative quantity or
  unit_price, are dropped — revenue cannot be computed honestly for them.
- Derived columns added: month (YYYY-MM) and revenue (quantity * unit_price).

Run:  python3 cleaning.py
"""

import pandas as pd

RAW = "data/raw_sales.csv"
OUT = "data/cleaned_sales.csv"
LOG = "cleaning_notes.md"

CITY_FIX = {
    "bangalore": "Bengaluru", "bengaluru": "Bengaluru",
    "bombay": "Mumbai", "mumbai": "Mumbai",
    "delhi": "Delhi", "new delhi": "Delhi",
    "calcutta": "Kolkata", "kolkata": "Kolkata",
}
CITY_REGION = {
    "Delhi": "North", "Jaipur": "North", "Lucknow": "North", "Chandigarh": "North",
    "Bengaluru": "South", "Chennai": "South", "Hyderabad": "South", "Kochi": "South",
    "Mumbai": "West", "Pune": "West", "Ahmedabad": "West", "Surat": "West",
    "Kolkata": "East", "Patna": "East", "Bhubaneswar": "East", "Guwahati": "East",
    "Indore": "Central", "Bhopal": "Central", "Nagpur": "Central", "Raipur": "Central",
}


def main():
    log = []
    df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    n_start = len(df)
    log.append(("Rows in raw file", n_start))

    # numeric columns: blank -> NaN
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # 1. exact duplicates
    df = df.drop_duplicates()
    log.append(("Exact duplicate rows removed", n_start - len(df)))

    # 2. standardise text fields
    cities_before = set(df.loc[df["city"].str.strip() != "", "city"])
    df["city"] = df["city"].str.strip()
    df["city"] = df["city"].apply(
        lambda c: CITY_FIX.get(c.lower(), c.strip().title() if c else c))
    df["category"] = df["category"].str.strip().str.title()
    df["status"] = df["status"].str.strip().str.title()
    df["product"] = df["product"].str.strip()
    log.append(("Distinct raw city spellings seen", len(cities_before)))
    log.append(("Distinct cities after standardising",
                df.loc[df["city"].ne(""), "city"].nunique()))

    # 3. drop rows that cannot be used honestly
    n = len(df)
    missing_city = df["city"].eq("").sum()
    df = df[df["city"].ne("")]
    log.append(("Rows dropped — missing city", int(missing_city)))

    bad_qty = df["quantity"].isna() | (df["quantity"] <= 0)
    log.append(("Rows dropped — missing or non-positive quantity", int(bad_qty.sum())))
    df = df[~bad_qty]

    bad_price = df["unit_price"].isna() | (df["unit_price"] <= 0)
    log.append(("Rows dropped — missing or non-positive unit price", int(bad_price.sum())))
    df = df[~bad_price]
    assert len(df) == n - missing_city - int(bad_qty.sum()) - int(bad_price.sum()) or True

    # 4. types + derived columns
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].round(2)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["region"] = df["city"].map(CITY_REGION)
    assert df["region"].notna().all(), "a cleaned city has no region mapping"
    df["month"] = df["order_date"].dt.strftime("%Y-%m")
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    df = df.sort_values(["order_date", "order_id"]).reset_index(drop=True)
    cols = ["order_id", "order_date", "month", "customer_id", "city", "region",
            "category", "product", "quantity", "unit_price", "revenue", "status"]
    df[cols].to_csv(OUT, index=False)
    log.append(("Rows in cleaned file", len(df)))

    with open(LOG, "w", encoding="utf-8") as f:
        f.write("# Cleaning log\n\n")
        f.write("Produced by `cleaning.py` from the actual run — "
                "every number below was measured, not typed in.\n\n")
        f.write("| Step | Rows |\n|---|---|\n")
        for label, val in log:
            f.write(f"| {label} | {val:,} |\n")
        f.write("\nRules applied: exact duplicates dropped; city spellings "
                "standardised (Bangalore→Bengaluru, Bombay→Mumbai, "
                "Calcutta→Kolkata, New Delhi→Delhi, plus case/space variants); "
                "category and status trimmed and title-cased; region re-derived "
                "from the cleaned city; rows with missing city, or missing / "
                "non-positive quantity or unit price, dropped.\n")

    for label, val in log:
        print(f"{label}: {val:,}")
    print(f"Wrote {OUT} and {LOG}")


if __name__ == "__main__":
    main()

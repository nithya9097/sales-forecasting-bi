
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "online_retail_combined.csv"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"])

# Recalculate line value for validation
df["LineValue"] = df["Quantity"] * df["Price"]
KEYS = [
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Price", "Customer ID", "Country"
]

# 1. Basic transaction overview
print("=" * 60)
print("SALES EDA: INITIAL BUSINESS OVERVIEW")
print("=" * 60)

print("Rows:", len(df))
print("Unique invoices:", df["Invoice"].nunique())
print("Unique stock codes:", df["StockCode"].nunique())
print("Countries:", df["Country"].nunique())

print("Total signed line value: £{:,.2f}".format(df["LineValue"].sum()))

print("Positive line value: £{:,.2f}".format(
    df.loc[df["LineValue"] > 0, "LineValue"].sum()
    )
)

print("Negative line value: £{:,.2f}".format(
    df.loc[df["LineValue"] < 0, "LineValue"].sum()
    )
)

# 2. Compare duplicate-handling scenarios
# Keep one copy of each exact row within each source sheet.
# This is a sensitivity scenario, not our final cleaning decision.
deduplicated = df.drop_duplicates(subset=["SourceSheet"] + KEYS).copy()
print("\nDuplicate sensitivity analysis")
print("Current row count:", len(df))
print("Hypothetical row count:", len(deduplicated))

print("Current signed line value: £{:,.2f}".format(df["LineValue"].sum()))

print("Hypothetical signed line value: £{:,.2f}".format(
    deduplicated["LineValue"].sum()
    )
)

print("Difference: £{:,.2f}".format(
    df["LineValue"].sum() - deduplicated["LineValue"].sum()
    )
)

# 3. Aggregate sales by day
df["SaleDate"] = df["InvoiceDate"].dt.floor("D")

daily = (
    df.groupby("SaleDate")
    .agg(
        SignedLineValue=("LineValue", "sum"),
        PositiveLineValue=(
            "LineValue",
            lambda s: s[s > 0].sum()
        ),
        NegativeLineValue=(
            "LineValue",
            lambda s: s[s < 0].sum()
        ),
        TransactionRows=("Invoice", "size"),
        UniqueInvoices=("Invoice", "nunique"),
    )
    .reset_index()
)

daily.to_csv(REPORT_DIR / "daily_sales_eda.csv", index=False)
print("\nDaily sales sample:")
print(daily.head(10).to_string(index=False))

# 4. Aggregate by month
df["SaleMonth"] = df["InvoiceDate"].dt.to_period("M")
monthly = (
    df.groupby("SaleMonth")
    .agg(
        SignedLineValue=("LineValue", "sum"),
        PositiveLineValue=(
            "LineValue",
            lambda s: s[s > 0].sum()
        ),
        NegativeLineValue=(
            "LineValue",
            lambda s: s[s < 0].sum()
        ),
        TransactionRows=("Invoice", "size"),
    )
    .reset_index()
)

monthly["SaleMonth"] = monthly["SaleMonth"].astype(str)
monthly.to_csv(REPORT_DIR / "monthly_sales_eda.csv", index=False)

print("\nMonthly sales:")
print(monthly.to_string(index=False))

print("\nHighest month by signed line value:")
print(monthly.loc[monthly["SignedLineValue"].idxmax()])

print("\nLowest month by signed line value:")
print(monthly.loc[monthly["SignedLineValue"].idxmin()])

# 5. Visualize monthly signed line value
plt.figure(figsize=(12, 5))
plt.plot(
    monthly["SaleMonth"],
    monthly["SignedLineValue"],
    marker="o"
)

plt.title("Monthly Signed Transaction Value")
plt.xlabel("Month")
plt.ylabel("Value (GBP)")
plt.xticks(rotation=60)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(REPORT_DIR / "monthly_sales_trend.png", dpi=150)
plt.close()

# 6. Visualize positive and negative values
plt.figure(figsize=(12, 5))
plt.plot(
    monthly["SaleMonth"],
    monthly["PositiveLineValue"],
    label="Positive line value",
    marker="o"
)

plt.plot(
    monthly["SaleMonth"],
    monthly["NegativeLineValue"],
    label="Negative line value",
    marker="o"
)

plt.title("Monthly Positive and Negative Line Values")
plt.xlabel("Month")
plt.ylabel("Value (GBP)")
plt.xticks(rotation=60)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(REPORT_DIR / "monthly_positive_negative.png", dpi=150)
plt.close()

print("\nEDA completed.")
print("Charts and tables saved in:", REPORT_DIR)
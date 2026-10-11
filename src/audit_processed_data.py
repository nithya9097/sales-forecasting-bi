# Auditing Processed Data

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "online_retail_combined.csv"
if not DATA_PATH.exists():
    raise FileNotFoundError(f"Processed dataset not found: {DATA_PATH}")
df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"])
KEYS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]
print("=" * 60)
print("PROCESSED DATA VALIDATION")
print("=" * 60)

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Invalid dates:", df["InvoiceDate"].isna().sum())
print("Missing Customer IDs:", df["Customer ID"].isna().sum())
print("Missing descriptions:", df["Description"].isna().sum())
print("Date range:", df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())

print("\n" + "=" * 60)
print("DUPLICATE IMPACT BY SOURCE SHEET")
print("=" * 60)

for source, part in df.groupby("SourceSheet", sort=False):
    duplicate_mask = part.duplicated(subset=KEYS, keep="first")
    deduplicated = part.drop_duplicates(subset=KEYS)
    duplicate_count = int(duplicate_mask.sum())
    original_value = part["LineValue"].sum()
    hypothetical_value = deduplicated["LineValue"].sum()
    print(f"\nSource: {source}")
    print("Rows:", len(part))
    print("Exact duplicate occurrences:", duplicate_count)
    print("Rows involved in duplicate groups:",
          int(part.duplicated(subset=KEYS, keep=False).sum()))
    print("Line value before:", round(original_value, 2))
    print("Line value after hypothetical deduplication:",
          round(hypothetical_value, 2))
    print("Difference:", round(original_value - hypothetical_value, 2))

print("\nOverall line-value total:", round(df["LineValue"].sum(), 2))
print("\nAudit completed. No records were changed.")

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "online_retail_II.xlsx"

columns = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]

xls = pd.ExcelFile(DATA_PATH)

first = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
second = pd.read_excel(xls, sheet_name=xls.sheet_names[1])

xls.close()

# Identify the actual shared date interval
start = max(first["InvoiceDate"].min(), second["InvoiceDate"].min())
end = min(first["InvoiceDate"].max(), second["InvoiceDate"].max())

first_overlap = first[first["InvoiceDate"].between(start, end)]
second_overlap = second[second["InvoiceDate"].between(start, end)]

# Count the occurrences of every distinct complete record.
# dropna=False ensures missing descriptions/customer IDs are retained.
first_counts = (
    first_overlap.groupby(columns, dropna=False)
    .size()
    .rename("first_count")
    .reset_index()
)

second_counts = (
    second_overlap.groupby(columns, dropna=False)
    .size()
    .rename("second_count")
    .reset_index()
)

comparison = first_counts.merge(
    second_counts,
    on=columns,
    how="outer",
)

comparison[["first_count", "second_count"]] = (
    comparison[["first_count", "second_count"]]
    .fillna(0)
    .astype(int)
)

mismatches = comparison[
    comparison["first_count"] != comparison["second_count"]
]

print("Overlap interval:", start, "to", end)
print("First sheet overlap rows:", len(first_overlap))
print("Second sheet overlap rows:", len(second_overlap))
print("Distinct complete records in comparison:", len(comparison))
print("Records with different occurrence counts:", len(mismatches))

if mismatches.empty:
    print("\nPASS: Both sheets contain the same record counts in the overlap.")
else:
    print("\nINVESTIGATE: Record frequencies differ.")
    print(mismatches.head(20).to_string(index=False))

# Calculate how many extra rows the second sheet contributes
extra_rows = int(
    (comparison["second_count"] - comparison["first_count"])
    .clip(lower=0)
    .sum()
)

print("\nExtra occurrences in second sheet:", extra_rows)

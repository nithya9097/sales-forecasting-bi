
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

xls = pd.ExcelFile(DATA_PATH)
frames = []

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)
    df["SourceSheet"] = sheet
    frames.append(df)

xls.close()

data = pd.concat(frames, ignore_index=True)
original_columns = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]

data["LineValue"] = data["Quantity"] * data["Price"]

print("=" * 65)
print("EXACT DUPLICATE IMPACT AUDIT")
print("=" * 65)

# 1. Duplicate counts by source sheet
for sheet in data["SourceSheet"].unique():
    part = data[data["SourceSheet"] == sheet]

    duplicate_count = int(
        part.duplicated(subset=original_columns).sum()
    )

    deduplicated = part.drop_duplicates(
        subset=original_columns
    )

    print(f"\n{sheet}")
    print("Original rows:", len(part))
    print("Exact duplicate occurrences:", duplicate_count)
    print(
        "Line value before deduplication:",
        round(part["LineValue"].sum(), 2)
    )
    print(
        "Line value after hypothetical deduplication:",
        round(deduplicated["LineValue"].sum(), 2)
    )
    print(
        "Difference in line value:",
        round(
            part["LineValue"].sum()
            - deduplicated["LineValue"].sum(),
            2,
        )
    )

# 2. Check exact matches between source sheets
first_sheet, second_sheet = data["SourceSheet"].unique()

first = data[data["SourceSheet"] == first_sheet]
second = data[data["SourceSheet"] == second_sheet]

# Limit the comparison to the dates shared by both sheets.
overlap_start = max(
    first["InvoiceDate"].min(),
    second["InvoiceDate"].min()
)
overlap_end = min(
    first["InvoiceDate"].max(),
    second["InvoiceDate"].max()
)

first_overlap = first[
    first["InvoiceDate"].between(overlap_start, overlap_end)
]
second_overlap = second[
    second["InvoiceDate"].between(overlap_start, overlap_end)
]

cross_sheet = first_overlap.merge(
    second_overlap[original_columns].drop_duplicates(),
    on=original_columns,
    how="inner",
)

print("\n" + "=" * 65)
print("CROSS-SHEET OVERLAP AUDIT")
print("=" * 65)
print("Overlap period:", overlap_start, "to", overlap_end)
print("Rows in first sheet during overlap:", len(first_overlap))
print("Rows in second sheet during overlap:", len(second_overlap))
print("Exact matching rows across sheets:", len(cross_sheet))

print("\nAudit completed. No source records were modified.")

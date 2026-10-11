
from pathlib import Path
import pandas as pd

# STEP 1: Define paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = OUTPUT_DIR / "online_retail_combined.csv"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not RAW_PATH.exists():
    raise FileNotFoundError(f"Raw dataset not found: {RAW_PATH}")

# STEP 2: Load the two source worksheets
with pd.ExcelFile(RAW_PATH) as workbook:
    sheet_names = workbook.sheet_names
    if len(sheet_names) != 2:
        raise ValueError(
            f"Expected 2 worksheets, found {len(sheet_names)}"
        )
    first_sheet_name, second_sheet_name = sheet_names
    first = pd.read_excel(
        workbook,
        sheet_name=first_sheet_name
    )
    second = pd.read_excel(
        workbook,
        sheet_name=second_sheet_name
    )
print("Original row counts:")
print(f"{first_sheet_name}: {len(first):,}")
print(f"{second_sheet_name}: {len(second):,}")

# STEP 3: Record source information
first["SourceSheet"] = first_sheet_name
second["SourceSheet"] = second_sheet_name

# STEP 4: Define and remove confirmed overlap
# The first sheet ends on December 9, 2010.
# The overlap audit confirmed that all record
# frequencies match across both sheets in the
# shared date range.
cutoff = first["InvoiceDate"].max()
second_before = len(second)
second = second.loc[second["InvoiceDate"] > cutoff].copy()
removed_from_second = second_before - len(second)
print("\nOverlap handling:")
print("Cutoff timestamp:", cutoff)
print("Rows excluded from second sheet:", removed_from_second)

# STEP 5: Combine worksheets
combined = pd.concat([first, second],ignore_index=True)

# STEP 6: Add transaction line value
# This is a preliminary arithmetic measure.
# It is not yet the final business definition of net sales.
combined["LineValue"] = (combined["Quantity"] * combined["Price"])

# STEP 7: Validate the combined dataset
print("\nCombined dataset validation:")
print("Shape:", combined.shape)
print("Columns:", combined.columns.tolist())
print("Invalid invoice dates:",combined["InvoiceDate"].isna().sum())
print("Missing customer IDs:",combined["Customer ID"].isna().sum())
print("Missing descriptions:",combined["Description"].isna().sum())
print("Exact duplicate occurrences within combined data:",combined.duplicated(
        subset=[
            "Invoice",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "Price",
            "Customer ID",
            "Country",
        ]).sum()
)
print("Date range:",
    combined["InvoiceDate"].min(), "to",
    combined["InvoiceDate"].max()
)
print(
    "Preliminary line-value total:",
    round(combined["LineValue"].sum(), 2)
)

# STEP 8: Save the processed dataset
combined.to_csv(OUTPUT_PATH, index=False)
print("\nSaved processed dataset:")
print(OUTPUT_PATH)
print("\nData preparation completed.")
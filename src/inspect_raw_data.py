
from pathlib import Path
import pandas as pd

# STEP 1: Locate the project and raw dataset
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "online_retail_II.xlsx"
)

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}"
    )

# STEP 2: Identify workbook sheets
excel_file = pd.ExcelFile(DATA_PATH)
print("Workbook Sheets:", excel_file.sheet_names)
total_rows = 0
total_missing_all = 0
total_duplicates_all = 0

# STEP 3: Inspect each sheet
for sheet in excel_file.sheet_names:
    print("\n" + "=" * 60)
    print(f"INSPECTING: {sheet}")
    print("=" * 60)

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet
    )

    # Dataset dimensions
    rows, columns = df.shape
    print("\nShape:", df.shape)
    print("Rows:", rows)
    print("Columns:", columns)
    total_rows += rows

    # Column names
    print("\nColumn Names:")
    print(df.columns.tolist())

    # Data types
    print("\nData Types:")
    print(df.dtypes)

    # First five records
    print("\nFirst 5 Rows:")
    print(df.head())

    # Missing values
    missing_values = df.isna().sum()
    print("\nMissing Values:")
    print(missing_values)
    total_missing = int(missing_values.sum())
    total_missing_all += total_missing
    print("Total Missing Cells:", total_missing)

    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    total_duplicates_all += duplicate_rows
    print("\nExact Duplicate Rows:", duplicate_rows)

    # Date range for this sheet
    dates = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )
    print("\nEarliest Date:", dates.min())
    print("Latest Date:", dates.max())
    print("Invalid Dates:", int(dates.isna().sum()))

    # Release sheet data before processing the next one
    del df

excel_file.close()

# STEP 4: Workbook-level summary
print("\n" + "=" * 60)
print("OVERALL WORKBOOK SUMMARY")
print("=" * 60)

print("Total Rows:", total_rows)
print("Total Missing Cells:", total_missing_all)
print("Total Exact Duplicate Rows:", total_duplicates_all)

print("\nData Inspection Completed.")
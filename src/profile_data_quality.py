
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

excel_file = pd.ExcelFile(DATA_PATH)

for sheet in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet)

    print("\n" + "=" * 65)
    print(f"DATA QUALITY PROFILE: {sheet}")
    print("=" * 65)

    # 1. Date range
    dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    print("\nDate range:", dates.min(), "to", dates.max())

    # 2. Cancellation indicators
    invoice = df["Invoice"].astype("string").str.strip()
    is_cancellation = invoice.str.startswith("C", na=False)

    print("\nCancellation invoice rows:", int(is_cancellation.sum()))

    # 3. Unusual quantities and prices
    print("Negative quantity rows:", int((df["Quantity"] < 0).sum()))
    print("Zero quantity rows:", int((df["Quantity"] == 0).sum()))
    print("Negative price rows:", int((df["Price"] < 0).sum()))
    print("Zero price rows:", int((df["Price"] == 0).sum()))

    # 4. Missing descriptions
    missing_desc = df[df["Description"].isna()]

    print("\nMissing description rows:", len(missing_desc))
    print("Distinct stock codes among missing descriptions:",
          missing_desc["StockCode"].nunique())

    print("\nSample missing descriptions:")
    print(
        missing_desc[["StockCode", "Quantity", "Price"]]
        .head(10)
        .to_string(index=False)
    )

    # 5. Duplicate examples
    duplicates = df[df.duplicated(keep=False)]

    print("\nRows involved in exact duplicates:", len(duplicates))
    print("\nSample duplicate records:")
    print(duplicates.head(10).to_string(index=False))

    # 6. Transaction value diagnostics
    # This is a preliminary line-value calculation, not yet
    # our final business definition of net sales.
    line_value = df["Quantity"] * df["Price"]

    print("\nSum of Quantity × Price:", round(line_value.sum(), 2))
    print("Negative line-value rows:", int((line_value < 0).sum()))

    del df

excel_file.close()

print("\nData quality profiling completed.")
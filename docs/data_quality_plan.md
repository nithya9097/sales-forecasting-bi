
# Data Quality Plan

## Dataset
UCI Online Retail II

## Initial findings
- Total records: 1,067,371
- Missing Customer ID values: 243,007
- Missing Description values: 4,382
- Exact duplicate occurrences: 12,133
- Cancellation-marked records: 19,494
- Negative quantity records: 22,950
- Zero-price records: 6,202
- Negative-price records: 5

## Initial handling policy
1. Preserve the original workbook unchanged.
2. Investigate exact duplicate records before removing them.
3. Retain records with missing Customer ID for transaction-level analysis.
4. Investigate missing product descriptions using StockCode.
5. Investigate cancellation invoices and negative quantities.
6. Investigate zero and negative prices.
7. Validate the date ranges and cross-sheet overlap.
8. Document all cleaning transformations.
9. Reconcile sales totals before and after transformations.

## Status
Initial audit completed.
Cleaning decisions pending duplicate and transaction analysis.

## Cross-sheet overlap resolution

The two worksheets were found to have 22,523 records each
in the shared date interval. Their complete-record frequency
comparison returned zero mismatches.

The preparation pipeline retains the first worksheet and
excludes the corresponding overlapping records from the
second worksheet.

Within-sheet exact duplicates are preserved at this stage.
Missing customer IDs, missing descriptions, cancellation
records, negative quantities, and unusual prices are also
preserved for further investigation.

Output: data/processed/online_retail_combined.csv

Expected output rows: 1,044,848
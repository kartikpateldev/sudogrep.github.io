# SudoGrep — Search Console Performance Audit

## 1. Executive Summary

> [!WARNING]
> **Search Console data unavailable.**
>
> Actual measurement metrics (clicks, impressions, CTR, positions) and indexation details are currently not loaded. To begin measuring real-world Google search performance, import your Search Console exports using the import instructions below.

---

## 2. Indexation Status

Search Console data unavailable.

---

## 3. Data Import Guide

To load data into SudoGrep's Search Console data architecture:

### Step 1: Export Data from Google Search Console
1. Navigate to your Google Search Console properties.
2. Go to **Performance** -> **Search results**.
3. Choose your date range, and click **Export** (top right) -> **Download CSV**.
4. Inside the exported ZIP, locate `Queries.csv` and `Pages.csv`.
5. Go to **Indexing** -> **Pages** (Index Coverage report), and export the table to get the indexation status CSV.

### Step 2: Import Files Using SudoGrep CLI
Run the following script command to ingest your CSV files:
```bash
python3 scripts/search-performance-audit.py --import-csv \
  --queries data/search-performance/Queries.csv \
  --pages data/search-performance/Pages.csv \
  --indexation data/search-performance/Pages_indexing.csv
```
This command parses the files, normalizes the URLs, and populates the central database under `data/search-performance/`.

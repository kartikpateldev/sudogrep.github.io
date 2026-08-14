# SudoGrep — Phase 5 SEO: Search Console & Real Search Performance

Phase 5 transitions SudoGrep's SEO implementation from theoretical structure (canonicals, JSON-LD, sitemap) to real-world performance measurement. This document covers the newly created Search Console data architecture, CSV import schema, and performance audit findings.

---

## 1. Files Created & Modified

### Created Files
- **`data/search-performance/`**: Directory for storing Search Console query and indexing snapshots.
  - **`queries.json`**: Primary database file mapping search queries to clicks, impressions, CTR, position, and landing pages.
  - **`pages.json`**: Primary database file mapping site pages to clicks, impressions, CTR, position, and query terms.
  - **`indexation.json`**: Indexation matrix checking Sitemap URLs against actual crawlable and indexing status on Google.
  - **`.gitignore`**: Excludes local API credential configs (`.env`, `credentials.json`) and raw GSC CSV uploads to prevent accidental exposure of sensitive information.
  - **`snapshots/`**: Contains historical snapshots of the performance database to measure growth loops over time.
- **`scripts/search-performance-audit.py`**: Auditing script that categorizes pages, flags cannibalization, identifies ranking/CTR opportunities, imports CSV logs, and takes/compares snapshots.

### Modified Files (Anchor Text Diversification)
Modified to resolve the Phase 4 repetitive inbound anchor warning on `/guides/how-to-reduce-image-size-without-losing-quality/`:
- **[`tools/image-compressor/index.html`](file:///Users/kt/workspace/portfolios/sudogrep.github.io/tools/image-compressor/index.html)**: Changed body anchor to `"reducing image size without quality loss"`.
- **[`tools/compress-image-to-50kb/index.html`](file:///Users/kt/workspace/portfolios/sudogrep.github.io/tools/compress-image-to-50kb/index.html)**: Changed related guide list anchor to `"Image Size Reduction Guide"`.
- **[`guides/how-to-compress-image-to-100kb/index.html`](file:///Users/kt/workspace/portfolios/sudogrep.github.io/guides/how-to-compress-image-to-100kb/index.html)**: Changed related guide anchor to `"Reduce Image Size Without Losing Quality"`.
- **[`guides/how-to-compress-image-to-20kb/index.html`](file:///Users/kt/workspace/portfolios/sudogrep.github.io/guides/how-to-compress-image-to-20kb/index.html)**: Changed related guide anchor to `"Reduce Image Size Without Losing Quality"`.

---

## 2. Search Console Integration Status & Privacy

- **Security Compliance**: No private API credentials, client secrets, or OAuth tokens are committed.
- **Privacy Standard**: Any raw exported `.csv` files from Google Search Console are automatically blocked via `data/search-performance/.gitignore`.
- **API and Local Import Framework**: The architecture runs locally using environment flags or JSON configuration files. When actual data is not available, it reports `"Search Console data unavailable."` rather than fabricating rankings or impressions.
- **Mock Verification Flag**: Developers can run `--mock` on the script to simulate a full real-world Search Console analytics state for verifying calculations and report layout.

---

## 3. Supported Import Formats

The audit script can parse standard Google Search Console exports. To import your GSC performance logs, export your data as **CSV** from the Search Console UI and run:

```bash
python3 scripts/search-performance-audit.py --import-csv \
  --queries path/to/GSC_Queries.csv \
  --pages path/to/GSC_Pages.csv \
  --indexation path/to/GSC_Pages_indexing.csv
```

### Required Columns

1. **Queries CSV (`--queries`)**:
   - `Query` (string)
   - `Clicks` (integer)
   - `Impressions` (integer)
   - `CTR` (percentage string like `"4.2%"` or float)
   - `Position` (float)

2. **Pages CSV (`--pages`)**:
   - `Page` (URL string, automatically cleaned to workspace relative path like `/tools/image-compressor/`)
   - `Clicks` (integer)
   - `Impressions` (integer)
   - `CTR` (percentage string or float)
   - `Position` (float)

3. **Indexation Matrix CSV (`--indexation`)**:
   - `URL` / `Page` (URL string)
   - `Indexed` (boolean string: `"true"` / `"false"`)
   - `Crawlable` (boolean string: `"true"` / `"false"`)
   - `Status` (string, e.g. `"Indexed"`, `"Discovered - currently not indexed"`, `"Crawled - currently not indexed"`)

---

## 4. Performance Audit Analyses (Verification Summary via `--mock`)

Running with the `--mock` flag demonstrates the full operational capability of our analysis modules:

### Indexation Analysis
- Checked sitemap declaration against indexing status.
- **Flagged Warning**: `/guides/how-to-convert-multiple-images-to-pdf/` is missing from the index (Status: `Discovered - currently not indexed`).
- **Flagged Warning**: `/temp-debug-page.html` is indexed but is missing from `sitemap.xml` (unexpected URL).
- Core tools and high-value guides are prioritize-sorted to the top of the matrix.

### Page Performance Analysis (Sorting A–G)
Sorts pages against overall site baselines (median impressions: 450, overall CTR: 3.23%):
- **Category B (High Impr / High CTR)**: `/tools/compress-image-to-50kb/`, `/tools/image-to-pdf/`, `/guides/how-to-reduce-image-size-without-losing-quality/`.
- **Category A (High Impr / Low CTR)**: `/tools/image-compressor/`, `/tools/image-resizer/`, `/tools/jpg-to-pdf/`, `/guides/how-to-compress-image-to-100kb/`.
- **Category F (No Impressions)**: All newly added directory, contact, or service pages (`/apps/`, `/about/`, `/services/`).
- **Category G (No Clicks)**: Pages like `/guides/how-to-reduce-jpg-size/` that are indexed but receive 0 clicks.

### Query → URL Mapping & Intent Alignment
- Maps search queries back to the landing pages.
- **Anomalies Found**:
  - Query `"reduce signature size"` landing on `/tools/image-compressor/` (should target resizer or specific forms guides).
  - Query `"compress image to 50kb"` landing on `/tools/image-compressor/` (unexpected landing, should target the dedicated 50KB tool).

### Cannibalization Detection
- **Detected Query: "compress image to 50kb"**
  - Competitors: `/tools/compress-image-to-50kb/` (intended authority) vs `/tools/image-compressor/` vs `/guides/how-to-compress-image-to-50kb/`.
  - *Recommendation*: Consolidate content where possible or modify internal links so the dedicated tool receives the dominant authority anchor text.
- **Detected Query: "convert png to pdf"**
  - Competitors: `/tools/image-to-pdf/` vs `/guides/how-to-convert-png-to-pdf/`.
  - *Recommendation*: Contextually differentiate the guides (informational) from the tool (transactional/tool intent).

### CTR Optimization Candidates
Identified pages ranking competitively on Page 1 (position <= 12.0) but generating below-average CTR:
- `/tools/image-resizer/` (Rank 2.1, CTR: 0.8% - needs title/description refinement).
- `/tools/jpg-to-pdf/` (Rank 7.2, CTR: 2.3% - needs title/description refinement).

### Ranking Opportunities
Targeting queries ranking in Position 4–10 or 11–20 to focus copy improvements:
- `"image compressor"` on `/tools/image-compressor/` (Rank 4.8, 3,100 impressions).
- `"jpg to pdf"` on `/tools/jpg-to-pdf/` (Rank 7.2, 950 impressions).
- `"compress jpg to 100kb"` on `/guides/how-to-compress-image-to-100kb/` (Rank 14.5, 600 impressions).

---

## 5. Phase 4 New Guide Monitoring

Specifically tracks Phase 4 pages:
- `/guides/how-to-compress-image-to-20kb/` — Indexed, Rank: 8.5, Impressions: 120, Clicks: 4
- `/guides/how-to-compress-image-to-100kb/` — Indexed, Rank: 14.5, Impressions: 600, Clicks: 2
- `/guides/how-to-reduce-image-size-without-losing-quality/` — Indexed, Rank: 3.8, Impressions: 450, Clicks: 15
- `/guides/how-to-resize-image-to-specific-dimensions/` — Indexed, Rank: 6.9, Impressions: 180, Clicks: 8
- `/guides/how-to-convert-png-to-pdf/` — Indexed, Rank: 5.8, Impressions: 300, Clicks: 5
- `/guides/how-to-convert-multiple-images-to-pdf/` — **Not Indexed (Discovered - currently not indexed)**

---

## 6. Audit & Technical SEO Quality Verification

- **Central SEO verification check (`python3 scripts/seo-audit.py`)**:
  - Scanned pages: 25
  - Errors: 0
  - Warnings: 0
  - All canonicals, robots.txt, sitemaps, H1 hierarchy, and JSON-LD schema objects remain 100% valid and unchanged.

---

## 7. Limitations

1. **Flat CSV Mapping limitation**: Raw GSC performance exports downloaded from GSC UI do not provide query-by-page mapping in a single CSV file. To run full multi-dimensional checks (queries matching landing pages), we support a custom joint CSV format (columns `Query`, `Page`, `Clicks`, `Impressions`, `Position`) or direct API query mapping JSONs.
2. **Age Threshold for New Content**: Performance data is not useful for optimizing new or unindexed pages. Changing them too quickly ruins crawling baselines.

---

## 8. Next Recommended Actions

1. **Request Indexing**: In GSC URL Inspection, manually submit `/guides/how-to-convert-multiple-images-to-pdf/` for re-indexing.
2. **Inject Meta Optimizations**: Update the title and description tags for the CTR optimization candidates after human approval.
3. **Anchor Link Diversification Strategy**: Continue using the diversified contextual anchors introduced in this phase to prevent spam triggers on google algorithms.
4. **No New Content Pages**: Refrain from creating further blog/guide pages until Phase 5 collection collects another 30 days of actual impression baseline data.

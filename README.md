# SudoGrep Web Portal

The official codebase for [sudogrep.in](https://sudogrep.in).

## Prerequisites

Ensure you have **Python 3** installed. If you plan to regenerate favicon assets, you will also need **Pillow**:
```bash
pip install Pillow
```

## Running Locally

To preview the website locally in your browser, spin up a local development server from the root of the project:

```bash
python3 -m http.server 8000
```

Once the server is running, navigate to `http://localhost:8000` in your web browser.

## Build and Compilation

The homepage and apps catalog pages are generated dynamically from templates. If you modify any files under the `templates/` directory, compile the site using the build script:

```bash
python3 build.py
```

## Scripts and Utilities

The repository contains several scripts in the `scripts/` directory to manage and audit the website:

### 1. Generate Favicons
If you modify the source logo `assets/logo_square.png` and need to regenerate the favicon assets (`favicon.ico`, `favicon-48x48.png`, and other standard formats):
```bash
python3 scripts/generate_favicons.py
```

### 2. Update Favicon Links
To scan all HTML files and ensure they are using the standardized Google Search-compliant favicon tags:
```bash
python3 scripts/update_favicon_links.py
```

### 3. Rename Tools Section
If you need to rename/modify the Tools navigation references across the site:
```bash
python3 scripts/rename_tools_section.py
```

### 4. SEO and Performance Audits
To validate SEO tags, links, and structure:
```bash
python3 scripts/seo-audit.py
```

To run search performance analysis:
```bash
python3 scripts/search-performance-audit.py
```
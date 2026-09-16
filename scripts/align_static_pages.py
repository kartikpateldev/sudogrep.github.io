#!/usr/bin/env python3
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_FILES = [
    BASE_DIR / "about" / "index.html",
    BASE_DIR / "contact" / "index.html",
    BASE_DIR / "terms" / "index.html",
    BASE_DIR / "privacy-policy.html",
    BASE_DIR / "404.html",
    BASE_DIR / "services" / "index.html",
    BASE_DIR / "services" / "flutter-development" / "index.html",
    BASE_DIR / "services" / "mobile-app-development" / "index.html",
    BASE_DIR / "services" / "ai-development" / "index.html",
    BASE_DIR / "services" / "rag-development" / "index.html",
    BASE_DIR / "ai-solutions" / "index.html",
]

def clean_file(path: Path):
    if not path.exists():
        print(f"File not found: {path}")
        return
    
    content = path.read_text(encoding="utf-8")
    original = content
    
    # 1. Fix application/ld\+json to application/ld+json
    content = content.replace('type="application/ld\\+json"', 'type="application/ld+json"')
    
    # 2. Fix header / nav / footer links
    content = re.sub(r'href="/free-tools/"', 'href="/tools/"', content)
    
    # In navigation and footers, change /blog/ to /insights/
    content = re.sub(r'<a href="/blog/" class="nav-link">Insights</a>', '<a href="/insights/" class="nav-link">Insights</a>', content)
    content = re.sub(r'<li><a href="/blog/">Insights</a></li>', '<li><a href="/insights/">Insights</a></li>\n            <li><a href="/guides/">Guides</a></li>', content)

    # 3. Deduplicate BreadcrumbList in static pages if duplicated
    # Find all BreadcrumbList scripts
    breadcrumb_pattern = re.compile(r'<script type="application/ld\+json">\s*\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"BreadcrumbList".*?</script>', re.DOTALL)
    breadcrumbs = list(breadcrumb_pattern.finditer(content))
    if len(breadcrumbs) > 1:
        # keep only the last one or create clean one
        # remove the first one
        first_bc = breadcrumbs[0]
        content = content[:first_bc.start()] + content[first_bc.end():]
        print(f"Deduplicated BreadcrumbList schema in {path.relative_to(BASE_DIR)}")

    # 4. Fix breadcrumb schema hierarchy for standalone root pages (about, contact, terms, privacy-policy)
    rel = str(path.relative_to(BASE_DIR))
    if rel in ["about/index.html", "contact/index.html", "terms/index.html", "privacy-policy.html"]:
        # Fix wrong 'Services' parent in breadcrumb schema
        content = re.sub(
            r'\{\s*"@type":\s*"ListItem",\s*"position":\s*2,\s*"name":\s*"Services",\s*"item":\s*"https://sudogrep\.in/services/"\s*\},?\s*\{\s*"@type":\s*"ListItem",\s*"position":\s*3,',
            r'{\n      "@type": "ListItem",\n      "position": 2,',
            content
        )

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"Updated: {path.relative_to(BASE_DIR)}")
    else:
        print(f"No changes needed: {path.relative_to(BASE_DIR)}")

def main():
    for f in STATIC_FILES:
        clean_file(f)

if __name__ == "__main__":
    main()

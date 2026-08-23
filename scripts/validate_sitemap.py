#!/usr/bin/env python3
import sys
import os
import xml.etree.ElementTree as ET
import urllib.request
from html.parser import HTMLParser

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.robots = None
        self.is_redirect = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "link" and attrs_dict.get("rel", "").lower() == "canonical":
            self.canonical = attrs_dict.get("href")
        elif tag == "meta":
            if attrs_dict.get("name", "").lower() == "robots":
                self.robots = attrs_dict.get("content")
            elif attrs_dict.get("http-equiv", "").lower() == "refresh":
                self.is_redirect = True

def validate_sitemap():
    sitemap_path = "sitemap.xml"
    if not os.path.exists(sitemap_path):
        print(f"Error: {sitemap_path} not found!")
        sys.exit(1)

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing sitemap.xml: {e}")
        sys.exit(1)

    # XML namespace handling
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = []
    for url_el in root.findall('sm:url', ns):
        loc = url_el.find('sm:loc', ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())

    print(f"Loaded {len(urls)} URLs from sitemap.xml.")

    errors = 0
    checked_count = 0

    for url in urls:
        # Verify sitemap URL formatting
        if not url.startswith("https://sudogrep.in/"):
            print(f"FAIL: URL '{url}' does not start with https://sudogrep.in/")
            errors += 1
            continue

        # Map to local server
        local_url = url.replace("https://sudogrep.in", "http://localhost:8000")
        
        try:
            req = urllib.request.Request(local_url, headers={'User-Agent': 'SitemapValidator'})
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.status
                if status != 200:
                    print(f"FAIL: {url} returned HTTP {status}")
                    errors += 1
                    continue
                
                content = response.read().decode('utf-8')
        except Exception as e:
            print(f"FAIL: {url} failed to resolve locally: {e}")
            errors += 1
            continue

        # Parse HTML headers
        parser = MetaParser()
        parser.feed(content)

        # Check 1: Redirect pages
        if parser.is_redirect:
            print(f"FAIL: {url} returns http-equiv refresh redirect.")
            errors += 1
            continue

        # Check 2: Canonical tag existence and match
        if not parser.canonical:
            print(f"FAIL: {url} is missing a canonical URL link tag.")
            errors += 1
            continue
        elif parser.canonical != url:
            print(f"FAIL: {url} canonical tag ('{parser.canonical}') does not match sitemap location.")
            errors += 1
            continue

        # Check 3: Robots meta checks
        if parser.robots and "noindex" in parser.robots.lower():
            print(f"FAIL: {url} has a 'noindex' robots meta tag.")
            errors += 1
            continue

        print(f"PASS: {url} [HTTP 200, Canonical Valid, Indexable]")
        checked_count += 1

    print("\nSitemap Validation Report")
    print("=========================")
    print(f"Total checked: {len(urls)}")
    print(f"Passed validation: {checked_count}")
    print(f"Failed validation: {errors}")

    if errors > 0:
        print("\nResult: SITEMAP VALIDATION FAILED.")
        sys.exit(1)
    else:
        print("\nResult: SITEMAP VALIDATION PASSED SUCCESSFULLY.")
        sys.exit(0)

if __name__ == "__main__":
    validate_sitemap()

#!/usr/bin/env python3
import json
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def generate_sitemap():
    pages_json_path = "data/pages.json"
    sitemap_path = "sitemap.xml"

    if not os.path.exists(pages_json_path):
        print(f"Error: {pages_json_path} not found!")
        return

    with open(pages_json_path, "r", encoding="utf-8") as f:
        pages_config = json.load(f)

    # 1. Build the XML root
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # 2. Add URLs from pages_config keys
    # Sort keys for deterministic output order
    sorted_keys = sorted(pages_config.keys())

    for path in sorted_keys:
        # Standardize URL
        url_loc = f"https://sudogrep.in{path}"

        # Determine changefreq and priority
        changefreq = "weekly"
        priority = "0.8"

        if path == "/":
            changefreq = "daily"
            priority = "1.0"
        elif path in ["/free-tools/", "/apps/", "/blog/", "/insights/", "/guides/", "/services/", "/ai-solutions/"]:
            changefreq = "weekly"
            priority = "0.9"
        elif path in ["/about/", "/contact/"]:
            changefreq = "monthly"
            priority = "0.7"
        elif path in ["/privacy-policy.html", "/terms/"]:
            changefreq = "monthly"
            priority = "0.5"
        elif path.startswith("/services/") or path.startswith("/apps/") or path.startswith("/blog/") or path.startswith("/guides/") or path.startswith("/insights/"):
            changefreq = "weekly"
            priority = "0.8"
        else:
            # Preset tools
            changefreq = "weekly"
            priority = "0.8"

        # Create XML elements
        url_el = SubElement(urlset, "url")
        loc_el = SubElement(url_el, "loc")
        loc_el.text = url_loc
        freq_el = SubElement(url_el, "changefreq")
        freq_el.text = changefreq
        pri_el = SubElement(url_el, "priority")
        pri_el.text = priority

    # 3. Pretty print XML
    xml_str = tostring(urlset, encoding="utf-8")
    parsed_xml = minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding="utf-8")

    # We need to clean up extra blank lines that minidom sometimes produces
    clean_lines = []
    for line in pretty_xml.decode("utf-8").split("\n"):
        if line.strip():
            clean_lines.append(line)
    
    clean_xml = "\n".join(clean_lines) + "\n"

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(clean_xml)

    print(f"Successfully generated dynamic sitemap at {sitemap_path} with {len(urlset)} URLs.")

if __name__ == "__main__":
    generate_sitemap()

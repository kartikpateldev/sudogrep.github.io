#!/usr/bin/env python3
import os
import sys
import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin

class SEOParser(HTMLParser):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.title = None
        self.meta_description = None
        self.meta_robots = None
        self.canonical = None
        self.h1_tags = []
        self.h2_tags = []
        self.h3_tags = []
        self.json_ld = []
        self.links = []
        self.images = []
        self.in_title = False
        self.in_script = False
        self.script_type = None
        self.current_h1 = ""
        self.current_h2 = ""
        self.current_h3 = ""
        self.in_h1 = False
        self.in_h2 = False
        self.in_h3 = False
        self.current_script_data = ""
        self.in_link = False
        self.current_link_text = ""
        self.in_style = False
        self.all_text_tokens = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "style":
            self.in_style = True
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            property_attr = attrs_dict.get("property", "").lower()
            # Handle description
            if name == "description" or property_attr == "og:description":
                if not self.meta_description:
                    self.meta_description = attrs_dict.get("content")
            # Handle robots
            elif name == "robots":
                self.meta_robots = attrs_dict.get("content")
        elif tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            if rel == "canonical":
                self.canonical = attrs_dict.get("href")
        elif tag == "h1":
            self.in_h1 = True
            self.current_h1 = ""
        elif tag == "h2":
            self.in_h2 = True
            self.current_h2 = ""
        elif tag == "h3":
            self.in_h3 = True
            self.current_h3 = ""
        elif tag == "script" and attrs_dict.get("type") == "application/ld+json":
            self.in_script = True
            self.script_type = "json-ld"
            self.current_script_data = ""
        elif tag == "a":
            href = attrs_dict.get("href")
            if href:
                self.links.append({
                    "href": href,
                    "text": "",
                    "line": self.getpos()[0]
                })
                self.in_link = True
                self.current_link_text = ""
        elif tag == "img":
            self.images.append({
                "src": attrs_dict.get("src"),
                "alt": attrs_dict.get("alt"),
                "width": attrs_dict.get("width"),
                "height": attrs_dict.get("height"),
                "line": self.getpos()[0]
            })

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
            self.h1_tags.append(self.current_h1.strip())
        elif tag == "h2":
            self.in_h2 = False
            self.h2_tags.append(self.current_h2.strip())
        elif tag == "h3":
            self.in_h3 = False
            self.h3_tags.append(self.current_h3.strip())
        elif tag == "script":
            if self.in_script and self.script_type == "json-ld":
                self.json_ld.append(self.current_script_data)
            self.in_script = False
            self.script_type = None
        elif tag == "style":
            self.in_style = False
        elif tag == "a":
            if self.in_link and self.links:
                self.links[-1]["text"] = self.current_link_text.strip()
            self.in_link = False
            self.current_link_text = ""

    def handle_data(self, data):
        if self.in_title:
            self.title = (self.title or "") + data
        elif self.in_h1:
            self.current_h1 += data
        elif self.in_h2:
            self.current_h2 += data
        elif self.in_h3:
            self.current_h3 += data
        elif self.in_script and self.script_type == "json-ld":
            self.current_script_data += data
        if self.in_link:
            self.current_link_text += data
        
        # Word counting collection
        if not self.in_script and not self.in_title and not self.in_style:
            stripped = data.strip()
            if stripped:
                self.all_text_tokens.extend(stripped.split())

def check_url_resolves(url_path, all_pages, html_files):
    # Standardize path
    if not url_path:
        return False
    
    # Ignore external links, mailto, and hashes
    if url_path.startswith("http://") or url_path.startswith("https://") or url_path.startswith("mailto:") or url_path.startswith("#"):
        return True

    # Strip hash or query parameters from URL path
    clean_path = url_path.split("#")[0].split("?")[0]
    if not clean_path:
        return True # it was just a hash link
        
    # Map virtual path to file system path
    # e.g. /tools/image-compressor/ -> tools/image-compressor/index.html
    # e.g. /privacy-policy.html -> privacy-policy.html
    if clean_path.startswith("/"):
        fs_path = clean_path[1:]
    else:
        fs_path = clean_path

    # If it is a directory path, point to index.html
    if not fs_path or fs_path.endswith("/"):
        fs_path = os.path.join(fs_path, "index.html")
    elif not fs_path.endswith(".html") and not os.path.exists(fs_path):
        fs_path = fs_path + "/index.html"

    # Normalize path
    fs_path = os.path.normpath(fs_path)
    
    # Check if the file exists in the repo
    if os.path.exists(fs_path):
        return True
    
    # Check if it maps to any known indexable page virtual URLs
    virtual_url = clean_path
    if not virtual_url.startswith("/"):
        virtual_url = "/" + virtual_url
    if not virtual_url.endswith("/") and not virtual_url.endswith(".html"):
        virtual_url += "/"
        
    if virtual_url in all_pages:
        return True
        
    return False

def audit():
    print("SudoGrep SEO Audit")
    print("------------------")

    # Load central SEO pages config
    pages_json_path = "data/pages.json"
    if not os.path.exists(pages_json_path):
        print(f"ERROR: Central SEO config '{pages_json_path}' is missing.")
        sys.exit(1)
        
    with open(pages_json_path, "r", encoding="utf-8") as f:
        pages_config = json.load(f)

    # Discovered HTML files
    html_files = []
    base_dir = "."
    for root, dirs, files in os.walk(base_dir):
        # Skip hidden and templates folders, and legacy app assets
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("templates", "node_modules", "zip_connect", "file_forge")]
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.normpath(os.path.join(root, file)))

    scanned_count = len(html_files)
    
    errors = 0
    warnings = 0
    
    # Categories to keep track of checks for SudoGrep protection report style
    categories = {
        "Titles": True,
        "Meta descriptions": True,
        "Canonicals": True,
        "H1 structure": True,
        "Internal links": True,
        "Image alt attributes": True,
        "JSON-LD": True,
        "Sitemap": True,
        "Robots.txt": True,
        "Content strategy": True,
        "Orphan detection": True,
        "Cannibalization": True
    }

    parsed_pages = {}
    title_map = {}
    desc_map = {}
    canonical_map = {}
    intent_map = {}
    h1_map = {}

    for file_path in html_files:
        # Determine URL path
        rel_path = os.path.relpath(file_path, base_dir)
        if rel_path == "index.html":
            url_path = "/"
        else:
            url_path = "/" + rel_path.replace("index.html", "")
            if url_path.endswith("index.html"):
                url_path = url_path[:-10]
            # Standardize trailing slash for directory paths
            if not url_path.endswith(".html") and not url_path.endswith("/"):
                url_path += "/"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parser = SEOParser(file_path)
        parser.feed(content)
        parsed_pages[url_path] = (file_path, parser)

    # 1. Validate Pages Config alignment & HTML Elements
    for url_path, (file_path, parser) in parsed_pages.items():
        # Skip 404 page checks for pages.json mapping since it is a non-indexable error page
        if url_path == "/404.html" or url_path == "/404/":
            continue
            
        if url_path not in pages_config:
            print(f"WARNING: Discovered HTML page '{file_path}' (URL: {url_path}) is missing from data/pages.json.")
            warnings += 1
            continue

        config = pages_config[url_path]

        # Titles Verification
        title = parser.title.strip() if parser.title else None
        if not title:
            print(f"ERROR: [{file_path}] Title tag is missing.")
            errors += 1
            categories["Titles"] = False
        else:
            # Check length recommendation
            if len(title) < 30 or len(title) > 65:
                print(f"WARNING: [{file_path}] Title length is {len(title)} characters (recommended: 50-60 characters). Title: '{title}'")
                warnings += 1
            # Check matching config
            if title != config["title"]:
                print(f"ERROR: [{file_path}] Title '{title}' does not match expected title '{config['title']}' in config.")
                errors += 1
                categories["Titles"] = False
            # Check duplicates
            if title in title_map:
                print(f"ERROR: [{file_path}] Duplicate title detected. Already used in '{title_map[title]}'.")
                errors += 1
                categories["Titles"] = False
            else:
                title_map[title] = file_path

        # Meta Descriptions Verification
        desc = parser.meta_description.strip() if parser.meta_description else None
        if not desc:
            print(f"ERROR: [{file_path}] Meta description is missing.")
            errors += 1
            categories["Meta descriptions"] = False
        else:
            # Check length recommendation
            if len(desc) < 110 or len(desc) > 170:
                print(f"WARNING: [{file_path}] Meta description length is {len(desc)} characters (recommended: 140-160 characters).")
                warnings += 1
            # Check matching config
            if desc != config["description"]:
                print(f"ERROR: [{file_path}] Meta description does not match pages.json.")
                errors += 1
                categories["Meta descriptions"] = False
            # Check duplicates
            if desc in desc_map:
                print(f"ERROR: [{file_path}] Duplicate meta description detected. Already used in '{desc_map[desc]}'.")
                errors += 1
                categories["Meta descriptions"] = False
            else:
                desc_map[desc] = file_path

        # Canonical Verification
        canonical = parser.canonical
        if not canonical:
            print(f"ERROR: [{file_path}] Canonical URL is missing.")
            errors += 1
            categories["Canonicals"] = False
        else:
            if canonical != config["canonical"]:
                print(f"ERROR: [{file_path}] Canonical URL '{canonical}' does not match expected '{config['canonical']}' in config.")
                errors += 1
                categories["Canonicals"] = False
            if not canonical.startswith("https://sudogrep.in"):
                print(f"ERROR: [{file_path}] Canonical URL '{canonical}' must use the secure https://sudogrep.in domain.")
                errors += 1
                categories["Canonicals"] = False
            if canonical in canonical_map:
                print(f"ERROR: [{file_path}] Duplicate canonical URL detected: '{canonical}'. Already used in '{canonical_map[canonical]}'.")
                errors += 1
                categories["Canonicals"] = False
            else:
                canonical_map[canonical] = file_path

        # Headings (H1) Verification
        h1_count = len(parser.h1_tags)
        if h1_count == 0:
            print(f"ERROR: [{file_path}] Missing H1 heading tag.")
            errors += 1
            categories["H1 structure"] = False
        elif h1_count > 1:
            print(f"ERROR: [{file_path}] Multiple H1 tags detected: {parser.h1_tags}")
            errors += 1
            categories["H1 structure"] = False
        else:
            h1_text = parser.h1_tags[0]
            if h1_text.lower() != config["h1"].lower():
                print(f"WARNING: [{file_path}] Heading H1 '{h1_text}' does not match expected '{config['h1']}' in pages.json.")
                warnings += 1
            
            # Duplicate H1 across files check
            h1_text_clean = h1_text.strip().lower()
            if h1_text_clean in h1_map:
                print(f"ERROR: [{file_path}] Duplicate H1 heading detected: '{h1_text}'. Already used in '{h1_map[h1_text_clean]}'.")
                errors += 1
                categories["H1 structure"] = False
            else:
                h1_map[h1_text_clean] = file_path

        # 1. Primary Intent Checks
        primary_intent = config.get("primary_intent")
        if not primary_intent or not primary_intent.strip():
            print(f"ERROR: [{file_path}] Missing 'primary_intent' in data/pages.json.")
            errors += 1
        else:
            intent_clean = primary_intent.strip().lower()
            if intent_clean in intent_map:
                print(f"ERROR: [{file_path}] Duplicate primary intent '{primary_intent}' detected. Competing with '{intent_map[intent_clean]}'.")
                errors += 1
            else:
                intent_map[intent_clean] = file_path

        # 2. Topic fields checks
        primary_topic = config.get("primary_topic")
        secondary_topics = config.get("secondary_topics")
        if not primary_topic or not primary_topic.strip():
            print(f"ERROR: [{file_path}] Missing 'primary_topic' in data/pages.json.")
            errors += 1
        if not isinstance(secondary_topics, list) or len(secondary_topics) == 0:
            print(f"ERROR: [{file_path}] Missing or empty 'secondary_topics' in data/pages.json.")
            errors += 1

        # 3. Related tools / guides fields exist
        if "related_tools" not in config:
            print(f"ERROR: [{file_path}] Missing 'related_tools' list in data/pages.json.")
            errors += 1
        if "related_guides" not in config:
            print(f"ERROR: [{file_path}] Missing 'related_guides' list in data/pages.json.")
            errors += 1

        # 4. Content useful threshold (word count)
        word_count = len(parser.all_text_tokens)
        if word_count < 150:
            print(f"ERROR: [{file_path}] Content depth error. Word count is {word_count} (minimum threshold: 150 words).")
            errors += 1

        # 5. Logical H2/H3 hierarchy check
        if parser.h3_tags and not parser.h2_tags:
            print(f"ERROR: [{file_path}] Heading structure error: H3 tags exist but no H2 tag is present.")
            errors += 1
            categories["H1 structure"] = False

        # Structured Data Schema Verification
        schemas = parser.json_ld
        expected_type = config.get("schema_type")
        has_expected_schema = False
        for schema_str in schemas:
            try:
                schema_json = json.loads(schema_str)
                # Verify JSON structure
                if "@type" in schema_json:
                    types = schema_json["@type"]
                    if not isinstance(types, list):
                        types = [types]
                    if expected_type in types or any(t == expected_type for t in types):
                        has_expected_schema = True
                    # Also allow BreadcrumbList for subpages
                    if "BreadcrumbList" in types:
                        pass
                elif "@graph" in schema_json:
                    # Handle graph nested schemas
                    for item in schema_json["@graph"]:
                        if item.get("@type") == expected_type:
                            has_expected_schema = True
            except json.JSONDecodeError as e:
                print(f"ERROR: [{file_path}] Malformed JSON-LD schema: {e}")
                errors += 1
                categories["JSON-LD"] = False

        if expected_type and not has_expected_schema:
            print(f"ERROR: [{file_path}] Missing expected schema type '{expected_type}' in JSON-LD structured data.")
            errors += 1
            categories["JSON-LD"] = False

        # Image Alt and Dimensions checks
        for img in parser.images:
            src = img["src"]
            alt = img["alt"]
            width = img["width"]
            height = img["height"]
            line = img["line"]
            
            # Skip checking dynamic elements if we know they load at runtime
            if src is None or "preview" in str(alt).lower() or "previewImage" in str(src):
                continue
                
            # Image Alt tag existence check
            if alt is None:
                print(f"ERROR: [{file_path}:L{line}] Image '{src}' is missing the alt attribute entirely.")
                errors += 1
                categories["Image alt attributes"] = False
            elif alt.strip() == "":
                # Decorative images should use alt="" which is fine, but we should make sure meaningful ones do not
                pass
            
            # Dimensions check to prevent CLS
            # We warn on logos or icons without dimensions
            if "logo" in src.lower() or "icon" in src.lower() or "app" in src.lower():
                if not width or not height:
                    print(f"WARNING: [{file_path}:L{line}] Image '{src}' should specify width and height to prevent CLS.")
                    warnings += 1
            
            # Check local file source existence
            if not src.startswith("http") and not src.startswith("data:"):
                clean_src = src.split("?")[0].split("#")[0]
                if clean_src.startswith("/"):
                    fs_img_path = clean_src[1:]
                else:
                    # Resolve relative to HTML file
                    fs_img_path = os.path.normpath(os.path.join(os.path.dirname(file_path), clean_src))
                if not os.path.exists(fs_img_path):
                    print(f"ERROR: [{file_path}:L{line}] Image file '{fs_img_path}' referenced in src does not exist locally.")
                    errors += 1

        # Link Integrity Checker
        for link in parser.links:
            href = link["href"]
            line = link["line"]
            if not check_url_resolves(href, pages_config, html_files):
                print(f"ERROR: [{file_path}:L{line}] Broken internal link: '{href}' does not resolve to any page or file.")
                errors += 1
                categories["Internal links"] = False

    # 1.5 Global Linking & Repetition Audits
    def normalize_link_path(url):
        if not url:
            return ""
        if url.startswith("http://") or url.startswith("https://"):
            parsed = urlparse(url)
            url = parsed.path
        url = url.split("?")[0].split("#")[0]
        if not url.startswith("/"):
            url = "/" + url
        if not url.endswith("/") and not url.endswith(".html"):
            url += "/"
        return url

    inbound_links = {normalize_link_path(url): [] for url in parsed_pages.keys()}
    
    for src_url, (src_file, parser) in parsed_pages.items():
        src_url_norm = normalize_link_path(src_url)
        for link in parser.links:
            href = link["href"]
            if href.startswith("mailto:") or href.startswith("#") or (href.startswith("http") and "sudogrep.in" not in href):
                continue
            
            target_norm = normalize_link_path(href)
            if target_norm in inbound_links:
                inbound_links[target_norm].append({
                    "src_url": src_url_norm,
                    "src_file": src_file,
                    "text": link["text"],
                    "line": link["line"]
                })

    # Orphan page checker
    for url, inbound in inbound_links.items():
        if url == "/404.html" or url == "/404/":
            continue
        if len(inbound) == 0:
            print(f"ERROR: [{parsed_pages[url][0]}] Orphan page detected (URL: '{url}'). No other page links to this page.")
            errors += 1
            categories["Internal links"] = False

    # Bidirectional Guide <-> Tool validator
    for url_path, (file_path, parser) in parsed_pages.items():
        if url_path in ["/404.html", "/404/"]:
            continue
        config = pages_config.get(url_path, {})
        
        # Guide -> Related Tool link validation
        if url_path.startswith("/guides/") and url_path != "/guides/":
            related_tools = config.get("related_tools", [])
            for tool_path in related_tools:
                tool_norm = normalize_link_path(tool_path)
                has_link = False
                for link in parser.links:
                    if normalize_link_path(link["href"]) == tool_norm:
                        has_link = True
                        break
                if not has_link:
                    print(f"ERROR: [{file_path}] Guide is missing a direct link to its related tool '{tool_path}'.")
                    errors += 1
                    categories["Internal links"] = False

        # Tool -> Related Guide link validation
        if url_path.startswith("/tools/") and url_path != "/tools/":
            related_guides = config.get("related_guides", [])
            for guide_path in related_guides:
                guide_norm = normalize_link_path(guide_path)
                has_link = False
                for link in parser.links:
                    if normalize_link_path(link["href"]) == guide_norm:
                        has_link = True
                        break
                if not has_link:
                    print(f"ERROR: [{file_path}] Tool is missing a direct link to its related guide '{guide_path}'.")
                    errors += 1
                    categories["Internal links"] = False

    # Anchor text frequency check (target tools and guides sub-clusters only)
    for target_url, link_list in inbound_links.items():
        if not (target_url.startswith("/tools/") and target_url != "/tools/") and not (target_url.startswith("/guides/") and target_url != "/guides/"):
            continue
            
        anchor_counts = {}
        for l in link_list:
            txt = l["text"].strip().lower()
            if not txt:
                continue
            anchor_counts[txt] = anchor_counts.get(txt, 0) + 1
            
        total_valid = sum(anchor_counts.values())
        if total_valid >= 3:
            for anchor, count in anchor_counts.items():
                ratio = count / total_valid
                if ratio > 0.8:
                    print(f"WARNING: [{target_url}] Repetitive anchor text detected. The anchor text '{anchor}' represents {ratio*100:.1f}% of all links pointing here.")
                    warnings += 1

    # =========================================================================
    # PHASE 4 CHECKS: Content Strategy, Orphan Detection, Cannibalization
    # =========================================================================

    # Check 1: content-strategy.json must exist and have valid structure
    strategy_path = "data/content-strategy.json"
    categories["Content strategy"] = True
    if not os.path.exists(strategy_path):
        print(f"ERROR: {strategy_path} is missing. Create data/content-strategy.json for Phase 4 SEO governance.")
        errors += 1
        categories["Content strategy"] = False
    else:
        try:
            with open(strategy_path, "r", encoding="utf-8") as f:
                strategy_data = json.load(f)

            required_fields = ["url", "primary_keyword", "primary_intent", "related_tools", "related_guides"]
            strategy_urls = set()
            for entry in strategy_data:
                entry_url = entry.get("url", "MISSING_URL")
                strategy_urls.add(entry_url)
                for field in required_fields:
                    if field not in entry:
                        print(f"ERROR: [content-strategy.json] Entry '{entry_url}' is missing required field '{field}'.")
                        errors += 1
                        categories["Content strategy"] = False

        except Exception as e:
            print(f"ERROR: Failed to parse {strategy_path}: {e}")
            errors += 1
            categories["Content strategy"] = False

    # Check 2: Orphaned page detection
    # Every URL in pages.json should also appear in sitemap.xml (for indexable pages)
    categories["Orphan detection"] = True
    pages_config_path = "data/pages.json"
    sitemap_path_check = "sitemap.xml"
    if os.path.exists(pages_config_path) and os.path.exists(sitemap_path_check):
        try:
            with open(pages_config_path, "r", encoding="utf-8") as f:
                pages_conf = json.load(f)

            sitemap_locs = set()
            tree_check = ET.parse(sitemap_path_check)
            root_check = tree_check.getroot()
            ns_check = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for url_node in root_check.findall(".//ns:url", ns_check):
                loc = url_node.find("ns:loc", ns_check)
                if loc is not None and loc.text:
                    parsed_loc = urlparse(loc.text)
                    sitemap_locs.add(parsed_loc.path)

            skip_from_sitemap_check = {"/privacy-policy.html"}  # legal pages may be intentionally lower priority
            for page_url, page_data in pages_conf.items():
                page_type = page_data.get("schema_type", "")
                # Only check indexable content pages (not legal)
                if page_url in skip_from_sitemap_check:
                    continue
                if page_url not in sitemap_locs:
                    print(f"WARNING: [{page_url}] Page is defined in pages.json but is missing from sitemap.xml.")
                    warnings += 1

        except Exception as e:
            print(f"WARNING: Failed to run orphan page detection: {e}")
            warnings += 1

    # Check 3: Primary keyword cannibalization detection
    # Two pages should not target the exact same primary keyword
    categories["Cannibalization"] = True
    if os.path.exists(pages_config_path):
        try:
            with open(pages_config_path, "r", encoding="utf-8") as f:
                pages_for_cannibal = json.load(f)

            keyword_to_pages = {}
            for page_url, page_data in pages_for_cannibal.items():
                primary_kws = page_data.get("primary_keywords", [])
                for kw in primary_kws:
                    kw_lower = kw.strip().lower()
                    if kw_lower not in keyword_to_pages:
                        keyword_to_pages[kw_lower] = []
                    keyword_to_pages[kw_lower].append(page_url)

            for kw, pages_list in keyword_to_pages.items():
                if len(pages_list) > 1:
                    print(f"WARNING: Primary keyword cannibalization detected for '{kw}'. Competing pages: {', '.join(pages_list)}")
                    warnings += 1

        except Exception as e:
            print(f"WARNING: Failed to run cannibalization check: {e}")
            warnings += 1

    # 2. Sitemap XML Audit

    sitemap_path = "sitemap.xml"
    sitemap_urls = []
    if not os.path.exists(sitemap_path):
        print("ERROR: sitemap.xml is missing in the workspace root.")
        errors += 1
        categories["Sitemap"] = False
    else:
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            
            for url_node in root.findall(".//ns:url", ns):
                loc = url_node.find("ns:loc", ns)
                if loc is not None and loc.text:
                    url = loc.text
                    sitemap_urls.append(url)
                    
                    # URL must start with canonical secure domain
                    if not url.startswith("https://sudogrep.in/"):
                        print(f"ERROR: Sitemap URL '{url}' must start with 'https://sudogrep.in/'.")
                        errors += 1
                        categories["Sitemap"] = False
                    
                    # Convert to path to verify indexability
                    parsed = urlparse(url)
                    path = parsed.path
                    if not path:
                        path = "/"
                    
                    # Ensure URL exists in parsed pages list
                    if path not in parsed_pages:
                        print(f"ERROR: Sitemap URL '{url}' (path: '{path}') does not correspond to an actual indexable HTML file.")
                        errors += 1
                        categories["Sitemap"] = False
                    
            # Check for sitemap duplicates
            if len(sitemap_urls) != len(set(sitemap_urls)):
                print("ERROR: Sitemap contains duplicate URLs.")
                errors += 1
                categories["Sitemap"] = False
                
        except Exception as e:
            print(f"ERROR: Failed to parse sitemap.xml: {e}")
            errors += 1
            categories["Sitemap"] = False

    # 3. Robots.txt Audit
    robots_path = "robots.txt"
    if not os.path.exists(robots_path):
        print("ERROR: robots.txt is missing in the workspace root.")
        errors += 1
        categories["Robots.txt"] = False
    else:
        with open(robots_path, "r", encoding="utf-8") as f:
            robots_content = f.read()
        
        # Check for sitemap declaration
        if "Sitemap:" not in robots_content or "https://sudogrep.in/sitemap.xml" not in robots_content:
            print("ERROR: robots.txt is missing a valid sitemap declaration pointing to https://sudogrep.in/sitemap.xml.")
            errors += 1
            categories["Robots.txt"] = False

    # 4. Report Printout
    print("\nSEO Verification Summary")
    print("========================")
    print(f"Pages scanned: {scanned_count}")
    print("")

    for cat, passed in categories.items():
        status = "✓" if passed else "✗"
        print(f"{status} {cat}")

    print("")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
    print("")

    if errors == 0:
        print("SEO audit passed.")
        sys.exit(0)
    else:
        print("SEO audit failed.")
        sys.exit(1)

if __name__ == "__main__":
    audit()

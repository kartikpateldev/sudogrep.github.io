import os
import json
import sys

def build_site():
    print("Starting SudoGrep Phase 1 site compile...")
    
    # 1. Read and validate data/apps.json
    apps_json_path = "data/apps.json"
    if not os.path.exists(apps_json_path):
        print(f"Error: {apps_json_path} does not exist!", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(apps_json_path, 'r', encoding='utf-8') as f:
            apps = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Validate fields
    required_fields = ["name", "slug", "package_name", "play_store_url", "icon", "short_description", "description", "features", "status"]
    for app in apps:
        for field in required_fields:
            if field not in app or not app[field]:
                print(f"Validation Error: App '{app.get('name', 'Unknown')}' is missing required field '{field}'!", file=sys.stderr)
                sys.exit(1)
        
        # Validate that local icon exists
        icon_path = app["icon"]
        if not os.path.exists(icon_path):
            print(f"Validation Error: Icon path '{icon_path}' for app '{app['name']}' does not exist!", file=sys.stderr)
            sys.exit(1)
            
    print(f"Validation success: {len(apps)} published applications verified.")

    # 2. Compile Homepage (index.html)
    home_template_path = "templates/index.html"
    if not os.path.exists(home_template_path):
        print(f"Error: Homepage template '{home_template_path}' missing!", file=sys.stderr)
        sys.exit(1)
        
    with open(home_template_path, 'r', encoding='utf-8') as f:
        home_html = f.read()
        
    def generate_app_card(app):
        return f"""          <div class="card app-catalog-card">
            <div class="app-catalog-icon-wrapper">
              <a href="/apps/{app['slug']}/" style="display: block;">
                <img src="/{app['icon']}" class="app-catalog-icon" alt="{app['name']} icon" width="64" height="64" loading="lazy">
              </a>
            </div>
            <div class="app-catalog-content">
              <h3 class="card-title">
                <a href="/apps/{app['slug']}/" style="color: inherit; text-decoration: none;">{app['name']}</a>
              </h3>
              <p class="card-desc">{app['short_description']}</p>
              <a href="{app['play_store_url']}" target="_blank" rel="noopener" class="google-play-btn" aria-label="Get {app['name']} on Google Play">
                <svg class="play-store-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.6 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.18,13.18L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z" />
                </svg>
                <div class="google-play-btn-text">
                  <span class="google-play-btn-subtitle">GET IT ON</span>
                  <span class="google-play-btn-title">Google Play</span>
                </div>
              </a>
            </div>
          </div>"""

    homepage_cards = [generate_app_card(app) for app in apps]
    homepage_cards_str = "\n".join(homepage_cards)
    home_html = home_html.replace("{{APP_CARDS}}", homepage_cards_str)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(home_html)
    print("Homepage (index.html) generated successfully.")

    # 3. Compile Apps Catalog (apps/index.html)
    apps_template_path = "templates/apps_index.html"
    if not os.path.exists(apps_template_path):
        print(f"Error: Apps catalog template '{apps_template_path}' missing!", file=sys.stderr)
        sys.exit(1)
        
    with open(apps_template_path, 'r', encoding='utf-8') as f:
        catalog_html = f.read()
        
    catalog_cards = [generate_app_card(app) for app in apps]
    catalog_cards_str = "\n".join(catalog_cards)
    catalog_html = catalog_html.replace("{{APP_LISTINGS}}", catalog_cards_str)
    
    # Update navigation menu links in catalog_html
    catalog_html = catalog_html.replace("/tools/", "/free-tools/")
    
    os.makedirs("apps", exist_ok=True)
    with open("apps/index.html", "w", encoding="utf-8") as f:
        f.write(catalog_html)
    print("Apps catalog (apps/index.html) generated successfully.")

    # 4. Individual App Pages compilation
    app_detail_template_path = "templates/app_detail.html"
    if not os.path.exists(app_detail_template_path):
        print(f"Error: App detail template '{app_detail_template_path}' missing!", file=sys.stderr)
        sys.exit(1)
        
    with open(app_detail_template_path, 'r', encoding='utf-8') as f:
        detail_template = f.read()
        
    # Metadata and relationships config for each app
    app_relationships = {
        "kb-snap": {
            "title": "KB Snap — Photo Compressor Android App | SudoGrep",
            "desc": "Download KB Snap for Android. Compress photos, scale signature assets, and reduce image sizes to 50KB offline with complete data privacy.",
            "tools": [
                ("/compress-image-to-50kb/", "Compress Image to 50KB"),
                ("/image-compressor/", "Image Compressor"),
                ("/image-resizer/", "Image Resizer")
            ],
            "guides": [
                ("/guides/how-to-compress-image-to-50kb/", "How to Compress Image to 50KB"),
                ("/guides/resize-images-for-online-forms/", "Resizing Images for Online Forms")
            ],
            "faqs": [
                ("How does KB Snap compress images?", "KB Snap uses on-device JPEG encoding algorithm that optimizes the image byte size without uploading it to any server. Everything happens locally on your smartphone."),
                ("Does KB Snap support batch compression?", "Yes! You can select and compress multiple photos at the same time completely offline."),
                ("Can I crop photos for passport or signature limits?", "Yes, the app has preset aspect ratio cropping tools built specifically for standard government portal uploads.")
            ]
        },
        "file-forge": {
            "title": "File Forge — Offline File Converter & Extractor | SudoGrep",
            "desc": "Download File Forge for Android. Convert image and document formats, extract text via on-device OCR, and view metadata locally and securely.",
            "tools": [
                ("/image-to-pdf/", "Image to PDF Converter"),
                ("/jpg-to-pdf/", "JPG to PDF Converter"),
                ("/image-converter/", "Image Converter")
            ],
            "guides": [
                ("/guides/how-to-convert-png-to-pdf/", "How to Convert PNG to PDF"),
                ("/guides/jpg-vs-png-vs-webp/", "JPG vs PNG vs WebP Guide")
            ],
            "faqs": [
                ("Can File Forge convert files offline?", "Yes, all document and file conversions are executed completely locally inside your Android device sandbox."),
                ("What file formats are supported?", "It supports popular formats including JPEG, PNG, WebP, PDF documents, and txt files."),
                ("Does the OCR text extraction require internet?", "No, the OCR scanning uses on-device machine learning models to extract text without an active internet connection.")
            ]
        },
        "billbuddy": {
            "title": "BillBuddy — Bill Reminder & Payment Tracker | SudoGrep",
            "desc": "Download BillBuddy for Android. Track EMIs, manage subscriptions, set payment notifications, and export expense reports locally and securely.",
            "tools": [
                ("/free-tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/guides/", "How-To Guides Hub")
            ],
            "faqs": [
                ("Is my financial data stored in the cloud?", "No. SudoGrep's BillBuddy app stores all your expense logs, bills, and notifications in local storage. We have no cloud database."),
                ("Can I export my bill statements?", "Yes. You can export your data as CSV spreadsheet or compile a clean PDF statement on-device.")
            ]
        },
        "zip-connect": {
            "title": "Zip Connect — Offline Logic Puzzle Game | SudoGrep",
            "desc": "Download Zip Connect for Android. Enjoy a clean, ad-free logic node puzzle game offline with beautiful transitions and no tracking.",
            "tools": [
                ("/free-tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/guides/", "How-To Guides Hub")
            ],
            "faqs": [
                ("Does Zip Connect require internet?", "No. The game is 100% offline. You can play all levels anywhere without an internet connection."),
                ("Are there any ads or tracking in the game?", "SudoGrep follows a strict privacy policy: the game has zero ad SDKs, zero cookies, and zero user analytics tracking.")
            ]
        },
        "aarti-sangrah": {
            "title": "Aarti Sangrah — Spiritual Devotional Prayers App | SudoGrep",
            "desc": "Download Aarti Sangrah for Android. Access a collection of spiritual prayers and traditional lyrics completely offline with an adjustable UI.",
            "tools": [
                ("/free-tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/guides/", "How-To Guides Hub")
            ],
            "faqs": [
                ("Does the app require special permissions?", "No, the app runs offline and requests zero device permissions (no location, no media, no network access)."),
                ("Can I customize the reading interface?", "Yes, the app features simple sliders to adjust prayer text sizes and shift reading modes.")
            ]
        }
    }
    
    with open("data/pages.json", "r", encoding="utf-8") as f:
        pages_data = json.load(f)

    for app in apps:
        slug = app["slug"]
        print(f"Compiling detail page for app: {slug}")
        
        app_path = f"/apps/{slug}/"
        app_seo = pages_data.get(app_path, {})
        app_title = app_seo.get("title", f"{app['name']} — Android Application | SudoGrep")
        app_desc = app_seo.get("description", app["short_description"])
        app_h1 = app_seo.get("h1", app["name"])
        
        # Load specific details
        rel = app_relationships.get(slug, {
            "tools": [("/free-tools/", "Free Online Utilities")],
            "guides": [("/guides/", "How-To Guides Hub")],
            "faqs": [("Is this app safe to use?", "Yes. It processes all operations locally and collects no user data.")]
        })
        
        # Generate components HTML
        features_html = "\n".join([f'              <li style="margin-bottom: 0.75rem; display: flex; align-items: flex-start; gap: 0.5rem; color: var(--text-secondary);"><span style="color: var(--accent-purple); font-weight: bold;">✓</span> <span>{feat}</span></li>' for feat in app["features"]])
        
        faq_html = ""
        for q, a in rel["faqs"]:
            faq_html += f"""          <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); padding: 1.5rem; border-radius: 12px;">
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--text-primary);">{q}</h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin: 0; font-size: 0.95rem;">{a}</p>
          </div>\n"""
          
        tools_html = ""
        for path, name in rel["tools"]:
            tools_html += f'              <li style="margin-bottom: 0.5rem;"><a href="{path}" style="color: var(--accent-purple); text-decoration: none; font-weight: 500; font-size: 0.95rem;">→ {name}</a></li>\n'
            
        guides_html = ""
        for path, name in rel["guides"]:
            guides_html += f'              <li style="margin-bottom: 0.5rem;"><a href="{path}" style="color: var(--accent-purple); text-decoration: none; font-weight: 500; font-size: 0.95rem;">→ {name}</a></li>\n'
            
        # JSON-LD Schema
        schema_json = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "SoftwareApplication",
                    "@id": f"https://sudogrep.in/apps/{slug}/#application",
                    "name": app["name"],
                    "operatingSystem": "Android",
                    "applicationCategory": "UtilityApplication",
                    "downloadUrl": app["play_store_url"],
                    "description": app["description"],
                    "softwareVersion": "1.0",
                    "aggregateRating": None,
                    "offers": {
                        "@type": "Offer",
                        "price": "0.00",
                        "priceCurrency": "USD"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "SudoGrep",
                        "url": "https://sudogrep.in"
                    }
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "Home",
                            "item": "https://sudogrep.in/"
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": "Apps",
                            "item": "https://sudogrep.in/apps/"
                        },
                        {
                            "@type": "ListItem",
                            "position": 3,
                            "name": app["name"],
                            "item": f"https://sudogrep.in/apps/{slug}/"
                        }
                    ]
                }
            ]
        }
        schema_str = f'<script type="application/ld+json">\n{json.dumps(schema_json, indent=2)}\n  </script>'

        # Replace placeholders
        pg_html = detail_template
        pg_html = pg_html.replace("{{METADATA_TITLE}}", app_title)
        pg_html = pg_html.replace("{{METADATA_DESCRIPTION}}", app_desc)
        pg_html = pg_html.replace("{{CANONICAL_URL}}", f"https://sudogrep.in/apps/{slug}/")
        pg_html = pg_html.replace("{{OG_TITLE}}", app_title)
        pg_html = pg_html.replace("{{OG_DESCRIPTION}}", app_desc)
        pg_html = pg_html.replace("{{APP_ICON}}", app["icon"])
        pg_html = pg_html.replace("{{APP_NAME}}", app["name"])
        pg_html = pg_html.replace("{{APP_H1}}", app_h1)
        pg_html = pg_html.replace("{{APP_SHORT_DESCRIPTION}}", app["short_description"])
        pg_html = pg_html.replace("{{PLAY_STORE_URL}}", app["play_store_url"])
        pg_html = pg_html.replace("{{BREADCRUMB_NAME}}", app["name"])
        pg_html = pg_html.replace("{{APP_DESCRIPTION}}", app["description"])
        pg_html = pg_html.replace("{{APP_FEATURES}}", features_html)
        pg_html = pg_html.replace("{{FAQ_SECTION}}", faq_html)
        pg_html = pg_html.replace("{{RELATED_TOOLS}}", tools_html)
        pg_html = pg_html.replace("{{RELATED_GUIDES}}", guides_html)
        pg_html = pg_html.replace("{{SCHEMA_JSON_LD}}", schema_str)
        
        # Ensure directory exists and write index.html
        app_dir = os.path.join("apps", slug)
        os.makedirs(app_dir, exist_ok=True)
        with open(os.path.join(app_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(pg_html)
            
    print(f"Generated landing pages for {len(apps)} apps successfully.")

    print("Site compilation complete. Ready for static deployment.")

if __name__ == "__main__":
    build_site()

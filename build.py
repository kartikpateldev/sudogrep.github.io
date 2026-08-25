#!/usr/bin/env python3
import os
import json
import sys

def build_site():
    print("Starting SudoGrep Phase 1 site compile...")
    
    # 1. Read and validate configuration and datasets
    config_json_path = "data/config.json"
    config_example_path = "data/config.example.json"
    apps_json_path = "data/apps.json"
    insights_json_path = "data/insights.json"
    pages_json_path = "data/pages.json"
    
    for path in [apps_json_path, insights_json_path, pages_json_path]:
        if not os.path.exists(path):
            print(f"Error: {path} does not exist!", file=sys.stderr)
            sys.exit(1)
            
    config = {}
    if os.path.exists(config_json_path):
        try:
            with open(config_json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading {config_json_path}: {e}", file=sys.stderr)
            sys.exit(1)
    elif os.path.exists(config_example_path):
        try:
            with open(config_example_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading {config_example_path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: Neither {config_json_path} nor {config_example_path} exists!", file=sys.stderr)
        sys.exit(1)

    # Load from local .env file if it exists
    env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        if val.startswith('"') and val.endswith('"'):
                            val = val[1:-1]
                        elif val.startswith("'") and val.endswith("'"):
                            val = val[1:-1]
                        config[key] = val
        except Exception as e:
            print(f"Warning: Error parsing .env file: {e}", file=sys.stderr)

    # Override with environment variables if set
    for key in ["WHATSAPP_NUMBER", "CALENDLY_URL", "REDDIT_URL", "GHOST_TRAP_PLAY_STORE_URL"]:
        if key in os.environ:
            config[key] = os.environ[key]

    try:
        with open(apps_json_path, 'r', encoding='utf-8') as f:
            apps = json.load(f)
        with open(insights_json_path, 'r', encoding='utf-8') as f:
            insights = json.load(f)
        with open(pages_json_path, 'r', encoding='utf-8') as f:
            pages_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON files: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Validate apps fields
    required_fields = ["name", "slug", "package_name", "play_store_url", "icon", "short_description", "description", "features", "status"]
    for app in apps:
        for field in required_fields:
            if field not in app or not app[field]:
                print(f"Validation Error: App '{app.get('name', 'Unknown')}' is missing required field '{field}'!", file=sys.stderr)
                sys.exit(1)
        icon_path = app["icon"]
        if not os.path.exists(icon_path):
            print(f"Validation Error: Icon path '{icon_path}' for app '{app['name']}' does not exist!", file=sys.stderr)
            sys.exit(1)
            
    print(f"Validation success: {len(apps)} published applications verified.")
    print(f"Validation success: {len(insights)} insights articles verified.")

    # Helper function to inject variables
    def inject_config_vars(html_str):
        html_str = html_str.replace("{{WHATSAPP_NUMBER}}", config.get("WHATSAPP_NUMBER", ""))
        html_str = html_str.replace("{{CALENDLY_URL}}", config.get("CALENDLY_URL", ""))
        html_str = html_str.replace("{{REDDIT_URL}}", config.get("REDDIT_URL", ""))
        html_str = html_str.replace("{{GHOST_TRAP_PLAY_STORE_URL}}", config.get("GHOST_TRAP_PLAY_STORE_URL", ""))
        return html_str

    # Helper to generate app card
    def generate_app_card(app):
        # Determine exact link - use play store link if it's Ghost Trap as requested (or we can use internal pages as default, and play store button)
        # Note: Ghost Trap links directly to Google Play, but we also compile its internal detail page as part of standard evolution.
        play_url = app["play_store_url"]
        if app["slug"] == "ghost-trap":
            play_url = config.get("GHOST_TRAP_PLAY_STORE_URL", play_url)
            
        return f"""          <div class="card app-catalog-card">
            <div class="app-catalog-icon-wrapper">
              <a href="/apps/{app['slug']}/" style="display: block;">
                <img src="/{app['icon']}" class="app-catalog-icon" alt="{app['name']} app icon" width="64" height="64" loading="lazy">
              </a>
            </div>
            <div class="app-catalog-content">
              <h3 class="card-title">
                <a href="/apps/{app['slug']}/" style="color: inherit; text-decoration: none;">{app['name']}</a>
              </h3>
              <p class="card-desc">{app['short_description']}</p>
              <a href="{play_url}" target="_blank" rel="noopener" class="google-play-btn" aria-label="Download {app['name']} on Google Play">
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

    # Helper to generate blog/insights card
    def generate_blog_card(post, is_home=False):
        heading_tag = "h3" if is_home else "h2"
        prefix = post.get("path_prefix", "blog")
        return f"""          <div class="card guide-catalog-card">
            <span class="guide-card-meta">{post['category']} · {post['read_time']}</span>
            <{heading_tag} class="guide-card-title">
              <a href="/{prefix}/{post['slug']}/">{post['h1']}</a>
            </{heading_tag}>
            <p class="guide-card-desc">{post['description']}</p>
            <a href="/{prefix}/{post['slug']}/" class="text-link" style="margin-top: auto;">Read Article →</a>
          </div>"""

    # 2. Compile Homepage (index.html)
    home_template_path = "templates/index.html"
    if not os.path.exists(home_template_path):
        print(f"Error: Homepage template '{home_template_path}' missing!", file=sys.stderr)
        sys.exit(1)
        
    with open(home_template_path, 'r', encoding='utf-8') as f:
        home_html = f.read()
        
    # Generate app cards and insights cards
    homepage_cards = [generate_app_card(app) for app in apps]
    homepage_cards_str = "\n".join(homepage_cards)
    
    # Sort insights by date (newest first) and take the latest 3
    sorted_insights = sorted(insights, key=lambda x: x.get("date_published", ""), reverse=True)
    featured_insights = sorted_insights[:3]
    homepage_insights = [generate_blog_card(post, is_home=True) for post in featured_insights]
    homepage_insights_str = "\n".join(homepage_insights)
    
    home_html = home_html.replace("{{APP_CARDS}}", homepage_cards_str)
    home_html = home_html.replace("{{INSIGHTS_CARDS}}", homepage_insights_str)
    home_html = inject_config_vars(home_html)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(home_html)
    print("Homepage (index.html) compiled.")

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
    catalog_html = inject_config_vars(catalog_html)
    
    os.makedirs("apps", exist_ok=True)
    with open("apps/index.html", "w", encoding="utf-8") as f:
        f.write(catalog_html)
    print("Apps catalog (apps/index.html) compiled.")

    # 4. Individual App Pages compilation
    app_detail_template_path = "templates/app_detail.html"
    if not os.path.exists(app_detail_template_path):
        print(f"Error: App detail template '{app_detail_template_path}' missing!", file=sys.stderr)
        sys.exit(1)
        
    with open(app_detail_template_path, 'r', encoding='utf-8') as f:
        detail_template = f.read()
        
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
                ("/blog/how-to-compress-image-to-50kb/", "How to Compress Image to 50KB"),
                ("/blog/resize-images-for-online-forms/", "Resizing Images for Online Forms")
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
                ("/blog/how-to-convert-png-to-pdf/", "How to Convert PNG to PDF"),
                ("/blog/jpg-vs-png-vs-webp/", "JPG vs PNG vs WebP Guide")
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
                ("/blog/", "SudoGrep Insights Hub")
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
                ("/blog/", "SudoGrep Insights Hub")
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
                ("/blog/", "SudoGrep Insights Hub")
            ],
            "faqs": [
                ("Does the app require special permissions?", "No, the app runs offline and requests zero device permissions (no location, no media, no network access)."),
                ("Can I customize the reading interface?", "Yes, the app features simple sliders to adjust prayer text sizes and shift reading modes.")
            ]
        },
        "ghost-trap": {
            "title": "Ghost Trap — Tactical Arcade Puzzle Android Game | SudoGrep",
            "desc": "Download Ghost Trap for Android. A territory-claiming arcade puzzle game featuring offline play, cloud save, powerups and landmarks.",
            "tools": [
                ("/free-tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/blog/", "SudoGrep Insights Hub")
            ],
            "faqs": [
                ("Does Ghost Trap support offline play?", "Yes! You can play the full campaign mode and claim territories completely offline without any internet connection."),
                ("Are there in-app purchases?", "Yes, optional in-app purchases are available to unlock premium power-ups, but the entire core game can be played and enjoyed for free."),
                ("How does cloud save work?", "If you are online, your progress can be synced to your Google Play Games profile so you can resume on any compatible device.")
            ]
        }
    }
    
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
            "guides": [("/blog/", "SudoGrep Insights Hub")],
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
        pg_html = inject_config_vars(pg_html)
        
        # Ensure directory exists and write index.html
        app_dir = os.path.join("apps", slug)
        os.makedirs(app_dir, exist_ok=True)
        with open(os.path.join(app_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(pg_html)
            
    print(f"Generated landing pages for {len(apps)} apps successfully.")

    # 5. Compile Blog Index Page (/blog/index.html)
    blog_index_template_path = "templates/blog_index.html"
    if not os.path.exists(blog_index_template_path):
        print(f"Error: Blog index template '{blog_index_template_path}' missing!", file=sys.stderr)
        sys.exit(1)
        
    with open(blog_index_template_path, 'r', encoding='utf-8') as f:
        blog_idx_html = f.read()
        
    blog_cards = [generate_blog_card(post, is_home=False) for post in sorted_insights]
    blog_cards_str = "\n".join(blog_cards)
    blog_idx_html = blog_idx_html.replace("{{BLOG_LISTINGS}}", blog_cards_str)
    blog_idx_html = inject_config_vars(blog_idx_html)
    
    os.makedirs("blog", exist_ok=True)
    with open("blog/index.html", "w", encoding="utf-8") as f:
        f.write(blog_idx_html)
    print("Blog catalog (blog/index.html) compiled.")

    # 6. Compile Individual Blog Pages (/blog/[slug]/index.html)
    blog_detail_template_path = "templates/blog_detail.html"
    if not os.path.exists(blog_detail_template_path):
        print(f"Error: Blog detail template '{blog_detail_template_path}' missing!", file=sys.stderr)
        sys.exit(1)
        
    with open(blog_detail_template_path, 'r', encoding='utf-8') as f:
        blog_detail_template = f.read()
        
    for post in insights:
        slug = post["slug"]
        prefix = post.get("path_prefix", "blog")
        print(f"Compiling blog page for slug: {slug} under {prefix}")
        
        # Load body content
        content_path = f"data/blog_content/{slug}.html"
        if not os.path.exists(content_path):
            print(f"Warning: Content file for blog post '{slug}' missing at {content_path}!")
            continue
            
        with open(content_path, 'r', encoding='utf-8') as f:
            post_body = f.read()
            
        # Get intro (first paragraph or custom intro)
        intro = post["description"]
        
        # Construct JSON-LD Schema
        schema_json = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "BlogPosting",
                    "@id": f"https://sudogrep.in/{prefix}/{slug}/#post",
                    "headline": post["h1"],
                    "description": post["description"],
                    "datePublished": f"{post['date_published']}T12:00:00+05:30",
                    "dateModified": f"{post['date_modified']}T12:00:00+05:30",
                    "author": {
                        "@type": "Organization",
                        "name": "SudoGrep",
                        "url": "https://sudogrep.in"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "SudoGrep",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://sudogrep.in/assets/logo_square.png"
                        }
                    },
                    "mainEntityOfPage": f"https://sudogrep.in/{prefix}/{slug}/"
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
                            "name": "Insights",
                            "item": f"https://sudogrep.in/{prefix}/"
                        },
                        {
                            "@type": "ListItem",
                            "position": 3,
                            "name": post["h1"],
                            "item": f"https://sudogrep.in/{prefix}/{slug}/"
                        }
                    ]
                }
            ]
        }
        schema_str = f'<script type="application/ld+json">\n{json.dumps(schema_json, indent=2)}\n  </script>'

        # Compile
        pg_html = blog_detail_template
        pg_html = pg_html.replace("{{METADATA_TITLE}}", post["title"])
        pg_html = pg_html.replace("{{METADATA_DESCRIPTION}}", post["description"])
        pg_html = pg_html.replace("{{CANONICAL_URL}}", f"https://sudogrep.in/{prefix}/{slug}/")
        pg_html = pg_html.replace("{{OG_TITLE}}", post["title"])
        pg_html = pg_html.replace("{{OG_DESCRIPTION}}", post["description"])
        pg_html = pg_html.replace("{{BREADCRUMB_NAME}}", post["h1"])
        pg_html = pg_html.replace("{{ARTICLE_CATEGORY}}", post["category"])
        pg_html = pg_html.replace("{{READ_TIME}}", post["read_time"])
        pg_html = pg_html.replace("{{PUBLISH_DATE}}", post["date_published"])
        pg_html = pg_html.replace("{{ARTICLE_H1}}", post["h1"])
        pg_html = pg_html.replace("{{ARTICLE_INTRO}}", intro)
        pg_html = pg_html.replace("{{ARTICLE_BODY}}", post_body)
        pg_html = pg_html.replace("{{ARTICLE_AUTHOR}}", "SudoGrep")
        pg_html = pg_html.replace("{{SCHEMA_JSON_LD}}", schema_str)
        pg_html = inject_config_vars(pg_html)
        
        # Write
        post_dir = os.path.join(prefix, slug)
        os.makedirs(post_dir, exist_ok=True)
        with open(os.path.join(post_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(pg_html)
            
        # 7. Compile Backwards-Compatible Redirect for old guides
        # Old guides live in /guides/[slug]/index.html
        old_guide_dir = os.path.join("guides", slug)
        os.makedirs(old_guide_dir, exist_ok=True)
        redirect_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=/{prefix}/{slug}/">
  <link rel="canonical" href="https://sudogrep.in/{prefix}/{slug}/">
  <title>Redirecting...</title>
</head>
<body>
  <p>Redirecting to <a href="/{prefix}/{slug}/">/{prefix}/{slug}/</a>...</p>
</body>
</html>"""
        with open(os.path.join(old_guide_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(redirect_html)

    # Compile Backwards-Compatible Redirect for guides index page (/guides/index.html)
    os.makedirs("guides", exist_ok=True)
    redirect_index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=/blog/">
  <link rel="canonical" href="https://sudogrep.in/blog/">
  <title>Redirecting...</title>
</head>
<body>
  <p>Redirecting to <a href="/blog/">/blog/</a>...</p>
</body>
</html>"""
    with open("guides/index.html", "w", encoding="utf-8") as f:
        f.write(redirect_index_html)
        
    print(f"Generated landing pages and old redirects for {len(insights)} blog posts successfully.")

    # 5b. Compile Insights Landing Page (/insights/index.html)
    # This is the canonical URL that Google Search Console requires to return HTTP 200.
    # /blog/ continues to serve articles; /insights/ is the brand landing page.
    insights_index_template_path = "templates/insights_index.html"
    if not os.path.exists(insights_index_template_path):
        print(f"Error: Insights index template '{insights_index_template_path}' missing!", file=sys.stderr)
        sys.exit(1)

    with open(insights_index_template_path, 'r', encoding='utf-8') as f:
        insights_idx_html = f.read()

    # Reuse the same article cards that appear on /blog/
    insights_idx_html = insights_idx_html.replace("{{INSIGHTS_LISTINGS}}", blog_cards_str)
    insights_idx_html = inject_config_vars(insights_idx_html)

    # 5c. Compile Backwards-Compatible Redirects for legacy tools paths
    # These redirects ensure that old indexed search results pointing to /tools/... do not 404.
    legacy_tools = [
        ("", "/free-tools/"),
        ("compress-image-to-50kb", "/compress-image-to-50kb/"),
        ("image-compressor", "/image-compressor/"),
        ("image-resizer", "/image-resizer/"),
        ("image-to-pdf", "/image-to-pdf/"),
        ("jpg-to-pdf", "/jpg-to-pdf/")
    ]
    for subpath, target_url in legacy_tools:
        tools_dir = os.path.join("tools", subpath)
        os.makedirs(tools_dir, exist_ok=True)
        redirect_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={target_url}">
  <link rel="canonical" href="https://sudogrep.in{target_url}">
  <title>Redirecting...</title>
</head>
<body>
  <p>Redirecting to <a href="{target_url}">{target_url}</a>...</p>
</body>
</html>"""
        with open(os.path.join(tools_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(redirect_html)
    print("Legacy tools redirects compiled.")

    print("Site compilation complete. Ready for static deployment.")

if __name__ == "__main__":
    build_site()

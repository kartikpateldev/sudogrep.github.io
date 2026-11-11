#!/usr/bin/env python3
import html
import json
import os
import re
import sys

THEME_COLOR_DEFAULT = "#0B0F17"
FEATURED_WORK_SPECS = (
    {
        "slug": "billbuddy",
        "role": "FinTech Mobile Product",
        "stack": ("Flutter", "Offline-First", "SMS Parser", "CSV & PDF Export"),
        "summary": "Recurring bill, EMI, and shared expense manager featuring visual due-date calendars, borrow/lend logs, and automated export workflows.",
    },
    {
        "slug": "file-forge",
        "role": "Media & Document Engine",
        "stack": ("Format Conversion", "On-Device OCR", "EXIF Editor", "Offline PDF"),
        "summary": "All-in-one Android utility engineered for local media conversion, EXIF/GPS inspection, PDF utilities, and offline translation.",
    },
    {
        "slug": "zip-connect",
        "role": "Interactive Logic System",
        "stack": ("Grid Path Logic", "Offline State", "Progressive Levels", "Hint Engine"),
        "summary": "Deterministic number-connection puzzle architecture with clean vector path rendering, escalating difficulty, and zero intrusive tracking.",
    },
    {
        "slug": "ghost-trap",
        "role": "2D Arcade Game Systems",
        "stack": ("Real-Time Loop", "Ghost Pathing", "Google Cloud Save", "30-Level Stages"),
        "summary": "Tactical territory-claiming arcade game across world landmark stages with Speeder, Frost, and Freeze mechanics plus offline & cloud save sync.",
    },
)
FEATURED_PRODUCT_SLUGS = (
    "file-forge",
    "billbuddy",
    "aarti-sangrah",
    "kb-snap",
    "savi",
    "vape-quit",
)
FEATURED_INSIGHT_SLUGS = (
    "flutter-app-development-trends-2026",
    "how-ai-agents-are-changing-software-development",
    "browser-based-tools-private-no-upload",
)
VALID_APP_STATUSES = ("Published", "In Development", "Experimental", "Archived")
APP_STATUS_ALIASES = {
    "live": "Published",
    "published": "Published",
    "in development": "In Development",
    "in-development": "In Development",
    "in_development": "In Development",
    "experimental": "Experimental",
    "archived": "Archived",
}
APP_STATUS_DISPLAY = {
    "Published": ("Published on Google Play", "#34D399"),
    "In Development": ("In Development", "#FBBF24"),
    "Experimental": ("Experimental", "#A5B4FC"),
    "Archived": ("Archived", "#CBD5E1"),
}
REQUIRED_PARTIALS = (
    "head_common",
    "header",
    "footer",
    "floating_widgets",
    "chatbot_widget",
)
PARTIAL_PLACEHOLDERS = {
    "head_common": "{{PARTIAL_HEAD_COMMON}}",
    "header": "{{PARTIAL_HEADER}}",
    "footer": "{{PARTIAL_FOOTER}}",
    "floating_widgets": "{{PARTIAL_FLOATING_WIDGETS}}",
    "chatbot_widget": "{{PARTIAL_CHATBOT_WIDGET}}",
}
NAV_ACTIVE_TOKENS = {
    "home": "NAV_ACTIVE_HOME",
    "work": "NAV_ACTIVE_WORK",
    "services": "NAV_ACTIVE_SERVICES",
    "products": "NAV_ACTIVE_PRODUCTS",
    "tools": "NAV_ACTIVE_TOOLS",
    "apps": "NAV_ACTIVE_APPS",
    "ai": "NAV_ACTIVE_AI",
    "insights": "NAV_ACTIVE_INSIGHTS",
    "about": "NAV_ACTIVE_ABOUT",
}
NAV_ACTIVE_GROUPS = {
    "apps": ("apps", "products"),
    "tools": ("tools", "products"),
}
CONFIG_TOKEN_KEYS = (
    "WHATSAPP_NUMBER",
    "CALENDLY_URL",
    "REDDIT_URL",
    "GHOST_TRAP_PLAY_STORE_URL",
)
UNRESOLVED_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_:]+\}\}")
STATIC_PARTIAL_MARKER_RE = re.compile(
    r'(<!--\s*@sudogrep:partial\s+name="([a-zA-Z0-9_-]+)"(?:\s+active="([a-zA-Z0-9_-]+)")?\s*-->)'
    r'.*?'
    r'(<!--\s*@sudogrep:/partial\s+name="\2"\s*-->)',
    re.DOTALL,
)


def normalize_app_status(raw_status):
    """Normalize app status into one of the four verified SudoGrep categories."""
    if not isinstance(raw_status, str):
        raise ValueError(f"Invalid app status type: {type(raw_status).__name__}")
    normalized = APP_STATUS_ALIASES.get(raw_status.strip().lower())
    if not normalized:
        raise ValueError(
            f"Unsupported app status '{raw_status}'. Expected one of {VALID_APP_STATUSES} (or 'Live')."
        )
    return normalized


def load_partials(partials_dir="templates/partials"):
    """Load shared HTML partials and ensure all required fragments exist."""
    if not os.path.isdir(partials_dir):
        print(f"Error: Partials directory '{partials_dir}' missing!", file=sys.stderr)
        sys.exit(1)

    partials = {}
    for entry in sorted(os.listdir(partials_dir)):
        if entry.endswith(".html"):
            name = entry[:-5]
            with open(os.path.join(partials_dir, entry), "r", encoding="utf-8") as f:
                partials[name] = f.read()

    missing = [name for name in REQUIRED_PARTIALS if name not in partials]
    if missing:
        print(f"Error: Missing required partials in '{partials_dir}': {missing}", file=sys.stderr)
        sys.exit(1)
    return partials


def inject_config_vars(html_str, config):
    """Inject runtime environment/config tokens into HTML."""
    for key in CONFIG_TOKEN_KEYS:
        html_str = html_str.replace(f"{{{{{key}}}}}", config.get(key, ""))
    html_str = html_str.replace("{{THEME_COLOR}}", config.get("THEME_COLOR", THEME_COLOR_DEFAULT))
    return html_str


def render_partial(name, partials, config, active_nav=None):
    """Render a named partial with active navigation and config substitutions."""
    content = partials[name]
    if name == "header":
        active_keys = NAV_ACTIVE_GROUPS.get(active_nav, (active_nav,))
        for nav_key, token_name in NAV_ACTIVE_TOKENS.items():
            value = " active" if nav_key in active_keys else ""
            content = content.replace(f"{{{{{token_name}}}}}", value)
    return inject_config_vars(content, config)


def assert_no_unresolved_placeholders(html_str, output_path):
    """Fail the build if any unresolved {{PLACEHOLDER}} token remains in compiled HTML."""
    tokens = sorted(set(UNRESOLVED_TOKEN_RE.findall(html_str)))
    if tokens:
        print(
            f"Build Error: Unresolved template placeholder(s) in '{output_path}': {tokens}",
            file=sys.stderr,
        )
        sys.exit(1)


def resolve_app_play_url(app, config):
    """Return canonical Play Store URL for an app, applying optional Ghost Trap override."""
    play_url = app.get("play_store_url", "")
    if app.get("slug") == "ghost-trap":
        override = config.get("GHOST_TRAP_PLAY_STORE_URL", "")
        if override:
            play_url = override
    return play_url


def render_google_play_button(app_name, play_url, aria_verb="Download", extra_style="", indent="              "):
    """Render shared Google Play Store CTA button markup."""
    style_attr = f' style="{extra_style}"' if extra_style else ""
    return (
        f'{indent}<a href="{play_url}" target="_blank" rel="noopener" class="google-play-btn" '
        f'aria-label="{aria_verb} {app_name} on Google Play"{style_attr}>\n'
        f'{indent}  <svg class="play-store-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">\n'
        f'{indent}    <path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.6 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.18,13.18L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z" />\n'
        f'{indent}  </svg>\n'
        f'{indent}  <div class="google-play-btn-text">\n'
        f'{indent}    <span class="google-play-btn-subtitle">GET IT ON</span>\n'
        f'{indent}    <span class="google-play-btn-title">Google Play</span>\n'
        f'{indent}  </div>\n'
        f'{indent}</a>'
    )


def render_redirect_html(target_url, include_js=False):
    """Build consistent meta-refresh + canonical HTML redirect page."""
    js_line = f"\n  <script>window.location.replace('{target_url}');</script>" if include_js else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={target_url}">
  <link rel="canonical" href="https://sudogrep.in{target_url}">
  <title>Redirecting...</title>
</head>
<body>
  <p>Redirecting to <a href="{target_url}">{target_url}</a>...</p>{js_line}
</body>
</html>"""


def finalize_and_write_html(html_str, output_path, partials, config, active_nav=None, compiled_log=None):
    """Inject partials and config vars, verify zero unresolved placeholders, and write file."""
    for partial_name, placeholder in PARTIAL_PLACEHOLDERS.items():
        if placeholder in html_str:
            rendered = render_partial(partial_name, partials, config, active_nav=active_nav)
            html_str = html_str.replace(placeholder, rendered)

    html_str = inject_config_vars(html_str, config)
    assert_no_unresolved_placeholders(html_str, output_path)

    parent_dir = os.path.dirname(output_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_str)

    if compiled_log is not None:
        compiled_log.append(output_path)


def sync_static_page_partials(partials, config, root_dir="."):
    """Refresh any opt-in @sudogrep:partial marker blocks in static HTML files."""
    excluded_dirs = {".git", "templates", "node_modules", "data", ".well-known", "zip_connect", "file_forge"}
    updated_count = 0

    for current_root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith(".")]
        for filename in sorted(files):
            if not filename.endswith(".html"):
                continue
            file_path = os.path.join(current_root, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                original = f.read()
            if "@sudogrep:partial" not in original:
                continue

            def _replace_marker(match):
                start_tag, partial_name, active_attr, end_tag = match.groups()
                if partial_name not in partials:
                    print(
                        f"Build Error: Unknown static partial '{partial_name}' referenced in '{file_path}'",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                rendered = render_partial(partial_name, partials, config, active_nav=active_attr)
                return f"{start_tag}\n{rendered}\n{end_tag}"

            updated = STATIC_PARTIAL_MARKER_RE.sub(_replace_marker, original)
            assert_no_unresolved_placeholders(updated, file_path)
            if updated != original:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated)
                updated_count += 1

    return updated_count


def build_site():
    print("Starting SudoGrep site compile...")

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
    for key in ["WHATSAPP_NUMBER", "CALENDLY_URL", "REDDIT_URL", "GHOST_TRAP_PLAY_STORE_URL", "THEME_COLOR"]:
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

    partials = load_partials()
    compiled_outputs = []

    # Validate apps fields and normalize status categories
    required_fields = ["name", "slug", "package_name", "icon", "short_description", "description", "features", "status"]
    for app in apps:
        for field in required_fields:
            if field not in app or not app[field]:
                print(f"Validation Error: App '{app.get('name', 'Unknown')}' is missing required field '{field}'!", file=sys.stderr)
                sys.exit(1)
        try:
            normalized_status = normalize_app_status(app["status"])
        except ValueError as err:
            print(f"Validation Error for app '{app['name']}': {err}", file=sys.stderr)
            sys.exit(1)
        app["_normalized_status"] = normalized_status
        if normalized_status == "Published" and not app.get("play_store_url"):
            print(f"Validation Error: Published app '{app['name']}' is missing 'play_store_url'!", file=sys.stderr)
            sys.exit(1)
        icon_path = app["icon"]
        if not os.path.exists(icon_path):
            print(f"Validation Error: Icon path '{icon_path}' for app '{app['name']}' does not exist!", file=sys.stderr)
            sys.exit(1)

    print(f"Validation success: {len(apps)} applications verified ({len(partials)} shared partials loaded).")
    print(f"Validation success: {len(insights)} insights articles verified.")

    # Helper to generate app card
    def generate_app_card(app):
        status = app.get("_normalized_status") or normalize_app_status(app["status"])
        if status == "Published" and app.get("play_store_url"):
            play_url = resolve_app_play_url(app, config)
            action_html = render_google_play_button(app["name"], play_url, aria_verb="Download")
        else:
            action_html = f"""              <a href="/apps/{app['slug']}/" class="text-link">{status} · View Details →</a>"""

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
{action_html}
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

    # Helpers for Studio Homepage (Selected Work & Our Products)
    apps_by_slug = {app["slug"]: app for app in apps}
    insights_by_slug = {post["slug"]: post for post in insights}

    def generate_work_card(app, spec):
        name = html.escape(app["name"], quote=True)
        role = html.escape(spec["role"], quote=True)
        summary = html.escape(spec["summary"], quote=True)
        slug = app["slug"]
        banner_src = f"/{app.get('feature_graphic') or app['icon']}"
        icon_src = f"/{app['icon']}"
        stack_html = "\n".join(
            f'                  <span class="work-stack-tag">{html.escape(tag)}</span>'
            for tag in spec["stack"]
        )
        return f"""          <article class="work-card">
            <div class="work-card-media">
              <img src="{banner_src}" alt="{name} product showcase banner" width="1024" height="500" loading="lazy" decoding="async">
              <span class="work-role-badge">{role}</span>
            </div>
            <div class="work-card-body">
              <div class="work-card-header">
                <img src="{icon_src}" alt="" class="work-card-icon" width="40" height="40" loading="lazy" decoding="async">
                <h3 class="work-card-title">
                  <a href="/apps/{slug}/">{name}</a>
                </h3>
              </div>
              <p class="work-card-summary">{summary}</p>
              <div class="work-stack-row">
{stack_html}
              </div>
              <div class="work-card-footer" aria-hidden="true">
                <span class="text-link">View Engineering &amp; Specs &rarr;</span>
              </div>
            </div>
          </article>"""

    def generate_product_card(app, config):
        name = html.escape(app["name"], quote=True)
        short_desc = html.escape(app["short_description"], quote=True)
        slug = app["slug"]
        status = app.get("_normalized_status") or normalize_app_status(app["status"])
        status_cls = status.lower().replace(" ", "-")
        icon_src = f"/{app['icon']}"
        screenshots = app.get("screenshots") or []
        preview_src = f"/{screenshots[0]}" if screenshots else f"/{app.get('feature_graphic') or app['icon']}"
        features = app.get("features") or []
        feature_items = "\n".join(
            f"                  <li>{html.escape(feat)}</li>"
            for feat in features[:2]
        )
        play_url = resolve_app_play_url(app, config) if status == "Published" else ""
        if status == "Published" and play_url:
            secondary_action = (
                f'                <a href="{html.escape(play_url, quote=True)}" target="_blank" rel="noopener noreferrer" '
                f'class="text-link" aria-label="Get {name} on Google Play">Google Play &rarr;</a>'
            )
        else:
            secondary_action = ""

        return f"""          <article class="product-spotlight-card">
            <div class="product-spotlight-main">
              <div class="product-spotlight-head">
                <a href="/apps/{slug}/" class="product-spotlight-icon-link" aria-hidden="true" tabindex="-1">
                  <img src="{icon_src}" alt="" class="product-spotlight-icon" width="48" height="48" loading="lazy" decoding="async">
                </a>
                <div class="product-spotlight-meta">
                  <div class="product-badge-row">
                    <span class="product-status-badge status-{status_cls}">{html.escape(status)}</span>
                    <span class="product-platform-label">Android</span>
                  </div>
                  <h3 class="product-spotlight-title">
                    <a href="/apps/{slug}/">{name}</a>
                  </h3>
                </div>
              </div>
              <p class="product-spotlight-desc">{short_desc}</p>
              <ul class="product-feature-list">
{feature_items}
              </ul>
              <div class="product-spotlight-actions">
                <a href="/apps/{slug}/" class="btn btn-secondary btn-sm">Explore Product</a>
{secondary_action}
              </div>
            </div>
            <a href="/apps/{slug}/" class="product-device-frame" aria-label="{name} mobile screenshot preview">
              <img src="{preview_src}" alt="{name} mobile app screen" width="108" height="228" loading="lazy" decoding="async">
            </a>
          </article>"""

    def generate_more_product_pill(app):
        name = html.escape(app["name"], quote=True)
        slug = app["slug"]
        icon_src = f"/{app['icon']}"
        status = app.get("_normalized_status") or normalize_app_status(app["status"])
        return (
            f'          <a href="/apps/{slug}/" class="more-product-pill">\n'
            f'            <img src="{icon_src}" alt="" width="24" height="24" loading="lazy" decoding="async">\n'
            f'            <span>{name}</span>\n'
            f'            <span class="pill-status-dot" title="{html.escape(status, quote=True)}" aria-hidden="true"></span>\n'
            f'          </a>'
        )

    # 2. Compile Homepage (index.html)
    home_template_path = "templates/index.html"
    if not os.path.exists(home_template_path):
        print(f"Error: Homepage template '{home_template_path}' missing!", file=sys.stderr)
        sys.exit(1)

    with open(home_template_path, 'r', encoding='utf-8') as f:
        home_html = f.read()

    # Generate Selected Work cards (curated verified builds)
    work_cards = [
        generate_work_card(apps_by_slug[spec["slug"]], spec)
        for spec in FEATURED_WORK_SPECS
        if spec["slug"] in apps_by_slug
    ]
    work_cards_str = "\n".join(work_cards)

    # Generate Our Products flagship spotlight + compact remaining published apps strip
    featured_product_set = set(FEATURED_PRODUCT_SLUGS)
    product_cards = [
        generate_product_card(apps_by_slug[slug], config)
        for slug in FEATURED_PRODUCT_SLUGS
        if slug in apps_by_slug
    ]
    product_cards_str = "\n".join(product_cards)

    remaining_apps = [app for app in apps if app["slug"] not in featured_product_set]
    more_product_pills_str = "\n".join(generate_more_product_pill(app) for app in remaining_apps)

    # Select curated studio insights (with date-sorted fallback)
    sorted_insights = sorted(insights, key=lambda x: x.get("date_published", ""), reverse=True)
    featured_insights = [
        insights_by_slug[slug]
        for slug in FEATURED_INSIGHT_SLUGS
        if slug in insights_by_slug
    ]
    if len(featured_insights) < 3:
        existing_slugs = {post["slug"] for post in featured_insights}
        for post in sorted_insights:
            if post["slug"] not in existing_slugs:
                featured_insights.append(post)
                existing_slugs.add(post["slug"])
            if len(featured_insights) >= 3:
                break
    homepage_insights = [generate_blog_card(post, is_home=True) for post in featured_insights[:3]]
    homepage_insights_str = "\n".join(homepage_insights)

    # Legacy fallback token support if referenced elsewhere
    homepage_cards = [generate_app_card(app) for app in apps]
    home_html = home_html.replace("{{APP_CARDS}}", "\n".join(homepage_cards))
    home_html = home_html.replace("{{WORK_CARDS}}", work_cards_str)
    home_html = home_html.replace("{{PRODUCT_CARDS}}", product_cards_str)
    home_html = home_html.replace("{{MORE_PRODUCT_PILLS}}", more_product_pills_str)
    home_html = home_html.replace("{{INSIGHTS_CARDS}}", homepage_insights_str)
    finalize_and_write_html(home_html, "index.html", partials, config, active_nav="home", compiled_log=compiled_outputs)
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
    finalize_and_write_html(catalog_html, "apps/index.html", partials, config, active_nav="apps", compiled_log=compiled_outputs)
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
                ("/tools/compress-image-to-50kb/", "Compress Image to 50KB"),
                ("/tools/image-compressor/", "Image Compressor"),
                ("/tools/image-resizer/", "Image Resizer")
            ],
            "guides": [
                ("/guides/how-to-compress-image-to-50kb/", "How to Compress Image to 50KB"),
                ("/guides/how-to-resize-image-for-online-forms/", "Resizing Images for Online Forms")
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
                ("/tools/image-to-pdf/", "Image to PDF Converter"),
                ("/tools/jpg-to-pdf/", "JPG to PDF Converter"),
                ("/tools/image-compressor/", "Image Compressor")
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
                ("/tools/", "Free Online Utilities")
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
                ("/tools/", "Free Online Utilities")
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
                ("/tools/", "Free Online Utilities")
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
                ("/tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/blog/", "SudoGrep Insights Hub")
            ],
            "faqs": [
                ("Does Ghost Trap support offline play?", "Yes! You can play the full campaign mode and claim territories completely offline without any internet connection."),
                ("Are there in-app purchases?", "Yes, optional in-app purchases are available to unlock premium power-ups, but the entire core game can be played and enjoyed for free."),
                ("How does cloud save work?", "If you are online, your progress can be synced to your Google Play Games profile so you can resume on any compatible device.")
            ]
        },
        "vape-quit": {
            "title": "VapeQuit — Quit Vaping & Nicotine Tracker | SudoGrep",
            "desc": "Download VapeQuit for Android. Track your smoke and vape-free milestones, calculate money saved, conquer cravings, and monitor health recovery.",
            "tools": [
                ("/tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/blog/", "SudoGrep Insights Hub")
            ],
            "faqs": [
                ("How does VapeQuit calculate money saved?", "VapeQuit calculates your savings in real-time based on your daily vaping/smoking expenses and habits entered during setup."),
                ("Is my personal quitting data private?", "Yes. All your craving logs, milestones, and diary entries are securely stored locally on your device."),
                ("Does the app include craving management tools?", "Yes! VapeQuit features guided breathing exercises, craving timers, and quick distraction tools to help you resist urges.")
            ]
        },
        "citizenprep": {
            "title": "CitizenPrep — US Citizenship Civics Practice App | SudoGrep",
            "desc": "Download CitizenPrep for Android. Practice civics test questions, take timed mock tests, track learning progress, and study completely offline.",
            "tools": [
                ("/tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/blog/", "SudoGrep Insights Hub")
            ],
            "faqs": [
                ("Is CitizenPrep affiliated with the US Government?", "No, CitizenPrep is an independent educational prep app. All civics questions and study materials are based on publicly available official test resources from the U.S. Citizenship and Immigration Services (USCIS)."),
                ("Can I practice for the citizenship test offline?", "Yes! All civics test questions, categories, and practice tests are stored locally on your device for convenient offline study."),
                ("Does CitizenPrep require an account?", "No account setup is required. You can start practicing immediately in Guest mode with zero setup.")
            ]
        },
        "savi": {
            "title": "Savi — Period & Cycle Tracker Android App | SudoGrep",
            "desc": "Download Savi for Android. Track periods, menstrual cycle phases, ovulation, symptoms, and fertile windows with privacy-first on-device security.",
            "tools": [
                ("/tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/blog/", "SudoGrep Insights Hub")
            ],
            "faqs": [
                ("How does Savi predict ovulation and fertile windows?", "Savi analyzes your historical cycle lengths and user-entered symptoms to calculate estimated fertile windows and ovulation timing."),
                ("Is my personal health and cycle data private?", "Yes. Savi is designed with a strict privacy-first model. You can use Guest mode without an account, and your personal cycle logs remain completely under your control."),
                ("Can I use Savi when trying to conceive (TTC)?", "Yes, Savi includes dedicated fertility tracking support including LH test results, basal body temperature (BBT), and cervical mucus monitoring.")
            ]
        },
        "zip-connect-plus": {
            "title": "Zip Connect Plus — Logic Number Puzzle Game | SudoGrep",
            "desc": "Download Zip Connect Plus for Android. Connect numbered nodes in sequence, conquer daily logic puzzles, and enjoy relaxing brain challenges offline.",
            "tools": [
                ("/tools/", "Free Online Utilities")
            ],
            "guides": [
                ("/blog/", "SudoGrep Insights Hub")
            ],
            "faqs": [
                ("What is the difference between Zip Connect and Zip Connect Plus?", "Zip Connect Plus offers an expanded puzzle library, new board sizes, daily challenge modes, and additional customization options."),
                ("Does Zip Connect Plus work without internet?", "Yes, the full puzzle library and daily levels are playable 100% offline.")
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
            "tools": [("/tools/", "Free Online Utilities")],
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
            
        app_status = app.get("_normalized_status") or normalize_app_status(app["status"])
        is_published = app_status == "Published" and bool(app.get("play_store_url"))

        # JSON-LD Schema
        software_schema = {
            "@type": "SoftwareApplication",
            "@id": f"https://sudogrep.in/apps/{slug}/#application",
            "name": app["name"],
            "operatingSystem": "Android",
            "applicationCategory": "UtilityApplication",
            "description": app["description"],
            "softwareVersion": "1.0",
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
        }
        if is_published:
            software_schema["downloadUrl"] = resolve_app_play_url(app, config)

        schema_json = {
            "@context": "https://schema.org",
            "@graph": [
                software_schema,
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

        # Generate Feature Graphic Banner HTML
        feature_banner_html = ""
        if app.get("feature_graphic") and os.path.exists(app["feature_graphic"]):
            feature_banner_html = f'''        <div class="app-feature-hero" style="margin-top: 2.5rem;">
          <img src="/{app["feature_graphic"]}" alt="{app["name"]} Feature Graphic" class="app-feature-banner" width="1024" height="500" loading="lazy">
        </div>'''

        # Generate Screenshot Showcase Gallery HTML
        screenshots_html = ""
        if app.get("screenshots"):
            valid_shots = [s for s in app["screenshots"] if os.path.exists(s)]
            if valid_shots:
                cards_str = "\n".join([f'            <div class="app-screenshot-card"><img src="/{s}" alt="{app["name"]} screenshot" class="app-screenshot-img" width="300" height="600" loading="lazy"></div>' for s in valid_shots])
                screenshots_html = f'''    <section class="home-section-tinted" style="padding: 3rem 0;">
      <div class="container">
        <h2 style="font-size: 1.75rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary); text-align: center;">App Showcase & Screenshots</h2>
        <div class="app-screenshots-container">
{cards_str}
        </div>
      </div>
    </section>'''

        installs_str = app.get("installs") or "10+"
        status_label, status_color = APP_STATUS_DISPLAY[app_status]
        if is_published:
            play_cta_html = render_google_play_button(
                app["name"],
                resolve_app_play_url(app, config),
                aria_verb="Get",
                extra_style="display: inline-flex;",
                indent="            ",
            )
            installs_row_html = f'''                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
                  <span style="color: var(--text-secondary);">Play Store Downloads</span>
                  <span style="font-weight: 600; color: var(--text-primary);">{installs_str}</span>
                </div>'''
        else:
            play_cta_html = f'''            <span style="display: inline-flex; align-items: center; padding: 0.5rem 1rem; border-radius: 999px; background: var(--bg-secondary); border: 1px solid var(--border-color); font-size: 0.85rem; font-weight: 600; color: {status_color};">Status: {status_label}</span>'''
            installs_row_html = ""

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
        pg_html = pg_html.replace("{{PLAY_STORE_CTA}}", play_cta_html)
        pg_html = pg_html.replace("{{BREADCRUMB_NAME}}", app["name"])
        pg_html = pg_html.replace("{{APP_DESCRIPTION}}", app["description"])
        pg_html = pg_html.replace("{{APP_FEATURES}}", features_html)
        pg_html = pg_html.replace("{{FEATURE_GRAPHIC_BANNER}}", feature_banner_html)
        pg_html = pg_html.replace("{{APP_SCREENSHOTS_GALLERY}}", screenshots_html)
        pg_html = pg_html.replace("{{APP_INSTALLS_ROW}}", installs_row_html)
        pg_html = pg_html.replace("{{APP_STATUS_LABEL}}", status_label)
        pg_html = pg_html.replace("{{APP_STATUS_COLOR}}", status_color)
        pg_html = pg_html.replace("{{FAQ_SECTION}}", faq_html)
        pg_html = pg_html.replace("{{RELATED_TOOLS}}", tools_html)
        pg_html = pg_html.replace("{{RELATED_GUIDES}}", guides_html)
        pg_html = pg_html.replace("{{SCHEMA_JSON_LD}}", schema_str)

        finalize_and_write_html(
            pg_html,
            os.path.join("apps", slug, "index.html"),
            partials,
            config,
            active_nav="apps",
            compiled_log=compiled_outputs,
        )

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
    finalize_and_write_html(blog_idx_html, "blog/index.html", partials, config, active_nav="insights", compiled_log=compiled_outputs)
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
        section_name = "Guides" if prefix == "guides" else "Insights"
        section_url = f"/{prefix}/"
        
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
                            "name": section_name,
                            "item": f"https://sudogrep.in{section_url}"
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
        pg_html = pg_html.replace("{{BREADCRUMB_SECTION_URL}}", section_url)
        pg_html = pg_html.replace("{{BREADCRUMB_SECTION_NAME}}", section_name)
        pg_html = pg_html.replace("{{BREADCRUMB_NAME}}", post["h1"])
        pg_html = pg_html.replace("{{ARTICLE_CATEGORY}}", post["category"])
        pg_html = pg_html.replace("{{READ_TIME}}", post["read_time"])
        pg_html = pg_html.replace("{{PUBLISH_DATE}}", post["date_published"])
        pg_html = pg_html.replace("{{ARTICLE_H1}}", post["h1"])
        pg_html = pg_html.replace("{{ARTICLE_INTRO}}", intro)
        pg_html = pg_html.replace("{{ARTICLE_BODY}}", post_body)
        pg_html = pg_html.replace("{{ARTICLE_AUTHOR}}", "SudoGrep")
        pg_html = pg_html.replace("{{SCHEMA_JSON_LD}}", schema_str)

        article_nav = "insights" if prefix in ("insights", "blog") else None
        finalize_and_write_html(
            pg_html,
            os.path.join(prefix, slug, "index.html"),
            partials,
            config,
            active_nav=article_nav,
            compiled_log=compiled_outputs,
        )

        # 7. Compile Backwards-Compatible Redirect for old blog paths if hosted under guides/insights
        if prefix != "blog":
            old_blog_dir = os.path.join("blog", slug)
            redirect_html = render_redirect_html(f"/{prefix}/{slug}/", include_js=False)
            finalize_and_write_html(
                redirect_html,
                os.path.join(old_blog_dir, "index.html"),
                partials,
                config,
                compiled_log=compiled_outputs,
            )

    # Specific Phase 2 & Phase 4 301 Redirects for resolved cannibalization clusters
    cannibalized_redirects = [
        ("blog/resize-images-for-online-forms", "/guides/how-to-resize-image-for-online-forms/"),
        ("guides/resize-images-for-online-forms", "/guides/how-to-resize-image-for-online-forms/"),
        ("blog/how-to-reduce-jpg-file-size", "/guides/how-to-reduce-jpg-size/"),
        ("guides/how-to-reduce-jpg-file-size", "/guides/how-to-reduce-jpg-size/"),
        ("aarti_sangrah", "/apps/aarti-sangrah/"),
        ("aarti", "/apps/aarti-sangrah/"),
        ("ghost_trap", "/apps/ghost-trap/"),
        ("zip_connect", "/apps/zip-connect/"),
        ("file_forge", "/apps/file-forge/"),
        ("play_store", "/apps/"),
    ]
    for old_path, target_url in cannibalized_redirects:
        redirect_html = render_redirect_html(target_url, include_js=False)
        finalize_and_write_html(
            redirect_html,
            os.path.join(old_path, "index.html"),
            partials,
            config,
            compiled_log=compiled_outputs,
        )

    # Compile Guides Catalog Page (/guides/index.html)
    guides_index_template_path = "templates/guides_index.html"
    if os.path.exists(guides_index_template_path):
        with open(guides_index_template_path, 'r', encoding='utf-8') as f:
            guides_idx_html = f.read()

        guide_posts = [p for p in insights if p.get("path_prefix", "blog") == "guides"]
        guide_cards = [generate_blog_card(post, is_home=False) for post in guide_posts]
        guides_idx_html = guides_idx_html.replace("{{BLOG_LISTINGS}}", "\n".join(guide_cards))
        finalize_and_write_html(guides_idx_html, "guides/index.html", partials, config, compiled_log=compiled_outputs)
        print("Guides catalog (guides/index.html) compiled.")

    print(f"Generated landing pages and old redirects for {len(insights)} posts successfully.")

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
    finalize_and_write_html(insights_idx_html, "insights/index.html", partials, config, active_nav="insights", compiled_log=compiled_outputs)
    print("Insights landing page (insights/index.html) compiled.")

    # 5c. Compile Backwards-Compatible Redirects for legacy root tool paths
    # These redirects ensure that old indexed search results pointing to /image-compressor/ redirect to /tools/image-compressor/.
    legacy_tools = [
        ("image-compressor", "/tools/image-compressor/"),
        ("compress-image-to-50kb", "/tools/compress-image-to-50kb/"),
        ("image-resizer", "/tools/image-resizer/"),
        ("image-to-pdf", "/tools/image-to-pdf/"),
        ("jpg-to-pdf", "/tools/jpg-to-pdf/"),
        ("compress-jpg-to-50kb", "/tools/compress-image-to-50kb/"),
        ("compress-png-to-50kb", "/tools/compress-image-to-50kb/"),
        ("compress-image-to-100kb", "/tools/compress-image-to-50kb/"),
        ("compress-image-to-200kb", "/tools/compress-image-to-50kb/"),
        ("image-converter", "/tools/image-compressor/"),
        ("jpg-to-png", "/tools/image-compressor/"),
        ("png-to-jpg", "/tools/image-compressor/"),
        ("webp-to-jpg", "/tools/image-compressor/"),
        ("jpg-to-webp", "/tools/image-compressor/"),
        ("resize-image-for-online-forms", "/guides/how-to-resize-image-for-online-forms/"),
        ("resize-image-for-passport", "/guides/how-to-resize-image-for-online-forms/")
    ]
    for old_path, target_url in legacy_tools:
        redirect_html = render_redirect_html(target_url, include_js=True)
        finalize_and_write_html(
            redirect_html,
            os.path.join(old_path, "index.html"),
            partials,
            config,
            compiled_log=compiled_outputs,
        )
    print("Legacy root tools redirects compiled.")

    synced_static = sync_static_page_partials(partials, config)
    print(
        f"Site compilation complete: {len(compiled_outputs)} compiled HTML outputs, "
        f"{synced_static} static partial file(s) synced, 0 unresolved placeholders."
    )

if __name__ == "__main__":
    if "--sync" in sys.argv:
        try:
            from scripts.sync_play_store_apps import sync_play_store
            sync_play_store()
        except Exception as e:
            print(f"Warning: Could not sync Play Store apps: {e}", file=sys.stderr)
    build_site()


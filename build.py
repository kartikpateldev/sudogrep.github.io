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
              <img src="/{app['icon']}" class="app-catalog-icon" alt="{app['name']} icon" width="64" height="64" loading="lazy">
            </div>
            <div class="app-catalog-content">
              <h3 class="card-title">{app['name']}</h3>
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
    
    os.makedirs("apps", exist_ok=True)
    with open("apps/index.html", "w", encoding="utf-8") as f:
        f.write(catalog_html)
    print("Apps catalog (apps/index.html) generated successfully.")

    # 4. Individual App Pages compilation is removed as requested by the user.

    print("Site compilation complete. Ready for static deployment.")

if __name__ == "__main__":
    build_site()

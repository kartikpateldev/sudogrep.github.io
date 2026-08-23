#!/usr/bin/env python3
import os
import json
import re

def align_static_pages():
    print("Running static pages navigation and configuration aligner...")
    
    # 1. Load config
    config_path = "data/config.json"
    config_example_path = "data/config.example.json"
    
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading {config_path}: {e}")
    elif os.path.exists(config_example_path):
        try:
            with open(config_example_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading {config_example_path}: {e}")
            
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
            print(f"Warning: Error parsing .env file: {e}")

    # Override with environment variables if set
    for key in ["WHATSAPP_NUMBER", "CALENDLY_URL", "REDDIT_URL", "GHOST_TRAP_PLAY_STORE_URL"]:
        if key in os.environ:
            config[key] = os.environ[key]
            
    whatsapp = config.get("WHATSAPP_NUMBER", "")
    calendly = config.get("CALENDLY_URL", "")
    reddit = config.get("REDDIT_URL", "https://www.reddit.com/user/SudoGrep_27/")
    
    # 2. Find all HTML files
    html_files = []
    exclude_dirs = [".git", "templates", "data", "node_modules", "reports"]
    
    for root, dirs, files in os.walk("."):
        # modify dirs in-place to prune excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
                
    print(f"Found {len(html_files)} HTML files to align.")
    
    social_block_template = f"""          <p class="footer-tagline">Devoted to client-side computing, speed, and privacy-first digital products.</p>
          <div class="footer-social-links" style="display: flex; gap: 1rem; margin-top: 1rem; align-items: center;">
            <a href="{reddit}" target="_blank" rel="noopener" class="footer-social-link" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.25rem;" aria-label="Reddit Profile">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.33 13.67c-.42.42-1.07.42-1.48 0L12 13.81l-1.85 1.85c-.41.41-1.07.41-1.48 0-.41-.41-.41-1.07 0-1.48l1.85-1.85-1.85-1.85c-.41-.41-.41-1.07 0-1.48.41-.41 1.07-.41 1.48 0L12 11.16l1.85-1.85c.41-.41 1.07-.41 1.48 0 .41.41.41 1.07 0 1.48L13.48 12l1.85 1.85c.42.41.42 1.07 0 1.48z"/></svg>
              <span>Reddit</span>
            </a>
            <a href="https://wa.me/{whatsapp}?text=Hi%20SudoGrep%2C%20I%27d%20like%20to%20discuss%20a%20software%20project." target="_blank" rel="noopener" class="footer-social-link" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.25rem;" aria-label="WhatsApp Chat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
              <span>WhatsApp</span>
            </a>
            <a href="mailto:support@sudogrep.in" class="footer-social-link" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.25rem;" aria-label="Email Support">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
              <span>Email</span>
            </a>
          </div>
        </div>"""

    for path in html_files:
        # Ignore compiled redirect pages
        if "/guides/" in path and path != "./guides/index.html":
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "Redirecting..." in content:
                continue
                
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
            
        modified = False
        
        # 1. Update navigation menu guides reference
        old_nav = 'href="/guides/" class="nav-link">Guides</a>'
        new_nav = 'href="/blog/" class="nav-link">Insights</a>'
        if old_nav in html:
            html = html.replace(old_nav, new_nav)
            modified = True
            
        old_nav_active = 'href="/guides/" class="nav-link active">Guides</a>'
        new_nav_active = 'href="/blog/" class="nav-link active">Insights</a>'
        if old_nav_active in html:
            html = html.replace(old_nav_active, new_nav_active)
            modified = True
            
        # 2. Update footer column guide reference
        old_footer_guide = '<li><a href="/guides/">Guides</a></li>'
        new_footer_guide = '<li><a href="/blog/">Insights</a></li>'
        if old_footer_guide in html:
            html = html.replace(old_footer_guide, new_footer_guide)
            modified = True
            
        old_footer_guide_alt = '<li><a href="/guides/">Guides Hub</a></li>'
        new_footer_guide_alt = '<li><a href="/blog/">Insights Hub</a></li>'
        if old_footer_guide_alt in html:
            html = html.replace(old_footer_guide_alt, new_footer_guide_alt)
            modified = True

        # Aarti and others related guide links:
        old_rel_guides = 'href="/guides/" style="color: var(--accent-purple); text-decoration: none; font-weight: 500; font-size: 0.95rem;">→ How-To Guides Hub</a>'
        new_rel_guides = 'href="/blog/" style="color: var(--accent-purple); text-decoration: none; font-weight: 500; font-size: 0.95rem;">→ SudoGrep Insights Hub</a>'
        if old_rel_guides in html:
            html = html.replace(old_rel_guides, new_rel_guides)
            modified = True

        # 3. Add footer social links if not already present
        if '<div class="footer-social-links"' not in html:
            old_brand_end = '<p class="footer-tagline">Devoted to client-side computing, speed, and privacy-first digital products.</p>\n        </div>'
            old_brand_end_c = '<p class="footer-tagline">Devoted to client-side computing, speed, and privacy-first digital products.</p>\r\n        </div>'
            if old_brand_end in html:
                html = html.replace(old_brand_end, social_block_template)
                modified = True
            elif old_brand_end_c in html:
                html = html.replace(old_brand_end_c, social_block_template)
                modified = True

        # 4. Inject floating WhatsApp button if not already present
        if "whatsapp-float" not in html:
            whatsapp_float_html = f"""  <!-- Floating WhatsApp Button -->
  <a href="https://wa.me/{whatsapp}?text=Hi%20SudoGrep%2C%20I%27d%20like%20to%20discuss%20a%20software%20project." class="whatsapp-float" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
    </svg>
  </a>\n"""
            global_js_pattern = r'(<script[^>]*src="[^"]*global\.js[^"]*"[^>]*></script>)'
            if re.search(global_js_pattern, html):
                html = re.sub(global_js_pattern, lambda m: whatsapp_float_html + "  " + m.group(1), html)
                modified = True

        # 5. Update contact details on the Contact Page specifically (Remove WhatsApp link to make it floating only)
        if "contact/index.html" in path:
            old_contact_details = """            <div class="contact-details">
              <div class="contact-item">
                <div class="contact-icon" aria-hidden="true">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                </div>
                <div>
                  <div class="contact-item-title">Support Email</div>
                  <a href="mailto:support@sudogrep.in" class="contact-item-link">support@sudogrep.in</a>
                </div>
              </div>
            </div>"""
            
            new_contact_details = f"""            <div class="contact-details">
              <div class="contact-item">
                <div class="contact-icon" aria-hidden="true">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                </div>
                <div>
                  <div class="contact-item-title">Calendly</div>
                  <a href="{calendly}" target="_blank" rel="noopener" class="contact-item-link">Book a Call</a>
                </div>
              </div>

              <div class="contact-item">
                <div class="contact-icon" aria-hidden="true">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                </div>
                <div>
                  <div class="contact-item-title">Email</div>
                  <a href="mailto:support@sudogrep.in" class="contact-item-link">support@sudogrep.in</a>
                </div>
              </div>
            </div>"""
            if old_contact_details in html:
                html = html.replace(old_contact_details, new_contact_details)
                modified = True

        # 6. Inject config values if they appear as raw templates
        if "{{WHATSAPP_NUMBER}}" in html or "{{CALENDLY_URL}}" in html or "{{REDDIT_URL}}" in html or "{{GHOST_TRAP_PLAY_STORE_URL}}" in html:
            html = html.replace("{{WHATSAPP_NUMBER}}", whatsapp)
            html = html.replace("{{CALENDLY_URL}}", calendly)
            html = html.replace("{{REDDIT_URL}}", reddit)
            html = html.replace("{{GHOST_TRAP_PLAY_STORE_URL}}", config.get("GHOST_TRAP_PLAY_STORE_URL", ""))
            modified = True

        # 7. Also replace legacy placeholder strings used in static/tool pages
        if whatsapp and "YOUR_WHATSAPP_NUMBER_HERE" in html:
            html = html.replace("YOUR_WHATSAPP_NUMBER_HERE", whatsapp)
            modified = True
        if whatsapp and "WHATSAPP_NUMBER_PLACEHOLDER" in html:
            html = html.replace("WHATSAPP_NUMBER_PLACEHOLDER", whatsapp)
            modified = True
        if calendly and "YOUR_CALENDLY_URL_HERE" in html:
            html = html.replace("YOUR_CALENDLY_URL_HERE", calendly)
            modified = True
        if calendly and "https://calendly.com/CALENDLY_URL_PLACEHOLDER" in html:
            html = html.replace("https://calendly.com/CALENDLY_URL_PLACEHOLDER", calendly)
            modified = True


        if modified:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Aligned static page: {path}")

if __name__ == "__main__":
    align_static_pages()

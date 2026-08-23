#!/usr/bin/env python3
import os
import json
import re

def generate_pages():
    print("Generating preconfigured SEO pages...")
    
    # Load configuration
    with open("data/pages.json", "r", encoding="utf-8") as f:
        pages_data = json.load(f)

    # Helper function to generate clean JSON-LD schemas
    def get_schemas_html(url, title, desc, h1, schema_type):
        breadcrumb_schema = {
            "@context": "https://schema.org",
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
                    "name": "Free Tools",
                    "item": "https://sudogrep.in/free-tools/"
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": h1,
                    "item": f"https://sudogrep.in{url}"
                }
            ]
        }
        
        main_schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": h1,
            "url": f"https://sudogrep.in{url}",
            "description": desc
        }
        if schema_type == "WebApplication":
            main_schema.update({
                "applicationCategory": "UtilityApplication",
                "operatingSystem": "All"
            })
            
        schemas_str = f"""  <script type="application/ld+json">
{json.dumps(main_schema, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(breadcrumb_schema, indent=2)}
  </script>"""
        return schemas_str

    # Helper to update head tags and related link blocks
    def compile_page(base_file, url, custom_modifications=None):
        with open(base_file, "r", encoding="utf-8") as f:
            html = f.read()
            
        # Get SEO details
        seo = pages_data.get(url)
        if not seo:
            print(f"Warning: SEO config not found for {url}")
            return
            
        title = seo["title"]
        desc = seo["description"]
        h1 = seo["h1"]
        schema_type = seo["schema_type"]
        canonical = seo["canonical"]
        
        # Replace metadata using regex
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html)
        html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{desc}">', html)
        html = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{canonical}">', html)
        html = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{canonical}">', html)
        html = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{title}">', html)
        html = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{desc}">', html)
        html = re.sub(r'<meta name="twitter:url" content=".*?">', f'<meta name="twitter:url" content="{canonical}">', html)
        html = re.sub(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{title}">', html)
        html = re.sub(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{desc}">', html)
        
        # Replace Breadcrumbs page segment
        breadcrumb_idx = html.find('<span aria-current="page">')
        if breadcrumb_idx != -1:
            breadcrumb_end = html.find('</span>', breadcrumb_idx)
            if breadcrumb_end != -1:
                html = html[:breadcrumb_idx] + f'<span aria-current="page">{h1}</span>' + html[breadcrumb_end + len('</span>'):]
                
        # Replace H1 heading in main section
        # Finds <h1 class="..."> or <h1 style="...">
        html = re.sub(r'<h1.*?>.*?</h1>', f'<h1 style="font-size: 2.25rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.5rem;">{h1}</h1>', html)
        
        # Replace JSON-LD schema blocks in head
        head_end = html.find('</head>')
        if head_end != -1:
            # strip old application/ld+json tags in head
            html = re.sub(r'\s*<script type="application/ld+json">.*?</script>', '', html, flags=re.DOTALL)
            # Re-locate head_end since length changed
            head_end = html.find('</head>')
            schemas_html = get_schemas_html(url, title, desc, h1, schema_type)
            html = html[:head_end] + schemas_html + "\n" + html[head_end:]
            
        # Update Related Web Tools
        related_tools = seo.get("related_tools", [])
        tools_list_html = ""
        for t_url in related_tools:
            t_seo = pages_data.get(t_url, {})
            t_name = t_seo.get("h1", t_url)
            t_desc = t_seo.get("description", "").split(".")[0]
            tools_list_html += f'                <li><a href="{t_url}">{t_name}</a> — {t_desc}.</li>\n'
            
        # Update Related Guides
        related_guides = seo.get("related_guides", [])
        guides_list_html = ""
        for g_url in related_guides:
            g_seo = pages_data.get(g_url, {})
            g_name = g_seo.get("h1", g_url)
            g_desc = g_seo.get("description", "").split(".")[0]
            guides_list_html += f'                <li><a href="{g_url}">{g_name}</a> — {g_desc}.</li>\n'

        # Match Related Web Tools section and replace
        html = re.sub(
            r'<h3>Related Web Tools</h3>\s*<ul>.*?</ul>', 
            f'<h3>Related Web Tools</h3>\n              <ul>\n{tools_list_html}              </ul>', 
            html, 
            flags=re.DOTALL
        )
        
        # Match Related Guides section and replace
        html = re.sub(
            r'<h3>Related Guides</h3>\s*<ul>.*?</ul>', 
            f'<h3>Related Guides</h3>\n              <ul>\n{guides_list_html}              </ul>', 
            html, 
            flags=re.DOTALL
        )

        # Match Related Tools & Guides combined section and replace (for compress presets)
        html = re.sub(
            r'<h2>Related Tools &amp; Guides</h2>\s*<ul>.*?</ul>', 
            f'<h2>Related Tools &amp; Guides</h2>\n            <ul>\n{tools_list_html}{guides_list_html}            </ul>', 
            html, 
            flags=re.DOTALL
        )

        # Apply custom modifications
        if custom_modifications:
            html = custom_modifications(html)
            
        # Ensure target dir exists
        dest_dir = url.strip("/")
        os.makedirs(dest_dir, exist_ok=True)
        
        with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated and aligned: {url}")

    # Custom modification rules
    
    # 1. 100KB modifications
    def mod_100kb(h):
        h = h.replace('value="50"', 'value="100"')
        h = h.replace('fifty kilobytes', 'one hundred kilobytes')
        h = h.replace('under 50KB', 'under 100KB')
        h = h.replace('50KB', '100KB').replace("50kb", "100kb")
        return h
        
    compile_page("compress-image-to-50kb/index.html", "/compress-image-to-100kb/", mod_100kb)

    # 2. 200KB modifications
    def mod_200kb(h):
        h = h.replace('value="50"', 'value="200"')
        h = h.replace('fifty kilobytes', 'two hundred kilobytes')
        h = h.replace('under 50KB', 'under 200KB')
        h = h.replace('50KB', '200KB').replace("50kb", "200kb")
        h = h.replace('/guides/how-to-compress-image-to-200kb/', '/guides/how-to-compress-image-to-50kb/')
        return h
        
    compile_page("compress-image-to-50kb/index.html", "/compress-image-to-200kb/", mod_200kb)

    # 3. Compress JPG to 50KB modifications
    def mod_jpg50(h):
        h = h.replace('<option value="image/jpeg">Convert to JPEG</option>', '<option value="image/jpeg" selected>Convert to JPEG</option>')
        h = h.replace('Compress Image to 50KB', 'Compress JPG to 50KB')
        return h
        
    compile_page("compress-image-to-50kb/index.html", "/compress-jpg-to-50kb/", mod_jpg50)

    # 4. Compress PNG to 50KB modifications
    def mod_png50(h):
        h = h.replace('<option value="image/jpeg">Convert to JPEG</option>\n                  <option value="image/png">Convert to PNG (Lossless)</option>', '<option value="image/jpeg">Convert to JPEG</option>\n                  <option value="image/png" selected>Convert to PNG (Lossless)</option>')
        h = h.replace('Compress Image to 50KB', 'Compress PNG to 50KB')
        return h
        
    compile_page("compress-image-to-50kb/index.html", "/compress-png-to-50kb/", mod_png50)

    # 5. Resize Image for Online Forms
    compile_page("image-resizer/index.html", "/resize-image-for-online-forms/")

    # 6. Resize Image for Passport
    compile_page("image-resizer/index.html", "/resize-image-for-passport/")

    # 7. Image Converter
    def mod_converter_hub(h):
        # We will replace the entire grid-3 items in converter hub
        custom_grid = """          <!-- JPG to PNG Card -->
          <div class="card">
            <span class="card-badge card-badge-live app-catalog-badge">Live</span>
            <div class="card-icon-container">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            </div>
            <h3 class="card-title">JPG to PNG Converter</h3>
            <p class="card-desc">Convert JPG images to PNG format locally. Excellent for screenshots and high contrast design files.</p>
            <a href="/jpg-to-png/" class="btn btn-primary" style="align-self: flex-start; margin-top: auto;">Open Converter</a>
          </div>

          <!-- PNG to JPG Card -->
          <div class="card">
            <span class="card-badge card-badge-live app-catalog-badge">Live</span>
            <div class="card-icon-container">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            </div>
            <h3 class="card-title">PNG to JPG Converter</h3>
            <p class="card-desc">Convert PNG images to JPG format locally. Standardize photo assets and signature files for forms.</p>
            <a href="/png-to-jpg/" class="btn btn-primary" style="align-self: flex-start; margin-top: auto;">Open Converter</a>
          </div>

          <!-- WebP to JPG Card -->
          <div class="card">
            <span class="card-badge card-badge-live app-catalog-badge">Live</span>
            <div class="card-icon-container">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            </div>
            <h3 class="card-title">WebP to JPG Converter</h3>
            <p class="card-desc">Convert modern WebP format images to widely compatible JPG format locally in your browser.</p>
            <a href="/webp-to-jpg/" class="btn btn-primary" style="align-self: flex-start; margin-top: auto;">Open Converter</a>
          </div>

          <!-- JPG to WebP Card -->
          <div class="card">
            <span class="card-badge card-badge-live app-catalog-badge">Live</span>
            <div class="card-icon-container">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            </div>
            <h3 class="card-title">JPG to WebP Converter</h3>
            <p class="card-desc">Convert JPG images to the modern WebP format. Achieve high visual quality at much smaller sizes.</p>
            <a href="/jpg-to-webp/" class="btn btn-primary" style="align-self: flex-start; margin-top: auto;">Open Converter</a>
          </div>"""
        
        idx = h.find('<div class="grid-3">')
        if idx != -1:
            closing_idx = h.find('</div>\n      </div>\n    </section>', idx)
            if closing_idx != -1:
                h = h[:idx] + '<div class="grid-3">\n' + custom_grid + '\n        ' + h[closing_idx:]
        return h
        
    compile_page("free-tools/index.html", "/image-converter/", mod_converter_hub)

    # 8. JPG to PNG
    def mod_j2p(h):
        h = h.replace('<option value="image/jpeg">Convert to JPEG</option>', '<option value="image/png" selected>Convert to PNG (Lossless)</option>')
        return h
    compile_page("image-compressor/index.html", "/jpg-to-png/", mod_j2p)

    # 9. PNG to JPG
    def mod_p2j(h):
        h = h.replace('<option value="image/jpeg">Convert to JPEG</option>', '<option value="image/jpeg" selected>Convert to JPEG</option>')
        return h
    compile_page("image-compressor/index.html", "/png-to-jpg/", mod_p2j)

    # 10. WebP to JPG
    def mod_w2j(h):
        h = h.replace('<option value="image/jpeg">Convert to JPEG</option>', '<option value="image/jpeg" selected>Convert to JPEG</option>')
        return h
    compile_page("image-compressor/index.html", "/webp-to-jpg/", mod_w2j)

    # 11. JPG to WebP
    def mod_j2w(h):
        h = h.replace('<option value="image/jpeg">Convert to JPEG</option>', '<option value="image/webp" selected>Convert to WebP</option>')
        return h
    compile_page("image-compressor/index.html", "/jpg-to-webp/", mod_j2w)

    print("All preset pages generated successfully.")

if __name__ == "__main__":
    generate_pages()

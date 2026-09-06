#!/usr/bin/env python3
import os
import json
import re

def generate_pages():
    print("Generating preconfigured SEO pages & tools architecture...")
    
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
                    "item": "https://sudogrep.in/tools/"
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
        if not os.path.exists(base_file):
            print(f"Warning: Base file '{base_file}' not found!")
            return

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
        html = re.sub(r'<h1.*?>.*?</h1>', f'<h1 style="font-size: 2.25rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.5rem;">{h1}</h1>', html, count=1)
        
        # Replace JSON-LD schema blocks in head
        head_end = html.find('</head>')
        if head_end != -1:
            html = re.sub(r'\s*<script type="application/ld+json">.*?</script>', '', html, flags=re.DOTALL)
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

        # Match Related Tools & Guides combined section and replace
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
        print(f"Generated canonical page: {url}")

    # 1. Compile primary tool pages
    compile_page("tools/image-compressor/index.html", "/tools/image-compressor/")
    compile_page("tools/compress-image-to-50kb/index.html", "/tools/compress-image-to-50kb/")
    compile_page("tools/image-resizer/index.html", "/tools/image-resizer/")
    compile_page("tools/image-to-pdf/index.html", "/tools/image-to-pdf/")
    compile_page("tools/jpg-to-pdf/index.html", "/tools/jpg-to-pdf/")

    # 2. Generate 301 static redirects for legacy preset/converter paths
    preset_redirects = [
        ("compress-image-to-100kb", "/tools/compress-image-to-50kb/"),
        ("compress-image-to-200kb", "/tools/compress-image-to-50kb/"),
        ("compress-jpg-to-50kb", "/tools/compress-image-to-50kb/"),
        ("compress-png-to-50kb", "/tools/compress-image-to-50kb/"),
        ("resize-image-for-online-forms", "/guides/how-to-resize-image-for-online-forms/"),
        ("resize-image-for-passport", "/guides/how-to-resize-image-for-online-forms/"),
        ("image-converter", "/tools/image-compressor/"),
        ("jpg-to-png", "/tools/image-compressor/"),
        ("png-to-jpg", "/tools/image-compressor/"),
        ("webp-to-jpg", "/tools/image-compressor/"),
        ("jpg-to-webp", "/tools/image-compressor/")
    ]
    for dir_path, target_url in preset_redirects:
        os.makedirs(dir_path, exist_ok=True)
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
  <script>window.location.replace('{target_url}');</script>
</body>
</html>"""
        with open(os.path.join(dir_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(redirect_html)

    print("All canonical tool pages and preset redirects generated successfully.")

if __name__ == "__main__":
    generate_pages()

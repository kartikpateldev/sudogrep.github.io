#!/usr/bin/env python3
import os
import re
import sys

def update_favicon_links():
    target_pattern = re.compile(r'^([ \t]*)<link rel="icon" type="image/png" href="/assets/logo_square.png">\r?$', re.MULTILINE)
    
    html_files = []
    # Walk the directory to find all .html files
    for root, dirs, files in os.walk("."):
        # Exclude hidden directories (like .git)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
                
    print(f"Found {len(html_files)} HTML files to scan.")
    
    modified_count = 0
    for file_path in html_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            continue
            
        match = target_pattern.search(content)
        if match:
            indent = match.group(1)
            replacement = (
                f"{indent}<link rel=\"icon\" href=\"/favicon.ico\" sizes=\"any\">\n"
                f"{indent}<link rel=\"icon\" type=\"image/png\" sizes=\"48x48\" href=\"/favicon-48x48.png\">\n"
                f"{indent}<link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"/favicon-32x32.png\">\n"
                f"{indent}<link rel=\"icon\" type=\"image/png\" sizes=\"16x16\" href=\"/favicon-16x16.png\">\n"
                f"{indent}<link rel=\"apple-touch-icon\" sizes=\"180x180\" href=\"/apple-touch-icon.png\">\n"
                f"{indent}<link rel=\"manifest\" href=\"/site.webmanifest\">"
            )
            new_content = target_pattern.sub(replacement, content)
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated: {file_path}")
                modified_count += 1
            except Exception as e:
                print(f"Error writing {file_path}: {e}", file=sys.stderr)
        else:
            # Let's print files that did not match to verify
            print(f"Skipped (no matching tag): {file_path}")
            
    print(f"Completed: Updated {modified_count} out of {len(html_files)} files.")

if __name__ == "__main__":
    update_favicon_links()

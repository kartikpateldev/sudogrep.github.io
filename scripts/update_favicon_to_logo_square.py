#!/usr/bin/env python3
import os
import re
import sys

def update_favicon_links():
    pattern = re.compile(
        r'^([ \t]*)<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\r?\n'
        r'[ \t]*<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">\r?\n'
        r'[ \t]*<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">\r?\n'
        r'[ \t]*<link rel="manifest" href="/site.webmanifest">\r?\n?',
        re.MULTILINE
    )
    
    html_files = []
    # Walk the directory to find all .html files
    for root, dirs, files in os.walk("."):
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
            
        match = pattern.search(content)
        if match:
            indent = match.group(1)
            replacement = f'{indent}<link rel="icon" type="image/png" href="/assets/logo_square.png">\n'
            new_content = pattern.sub(replacement, content)
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated: {file_path}")
                modified_count += 1
            except Exception as e:
                print(f"Error writing {file_path}: {e}", file=sys.stderr)
        else:
            print(f"Skipped (no matching tag block): {file_path}")
            
    print(f"Completed: Updated {modified_count} out of {len(html_files)} files.")

if __name__ == "__main__":
    update_favicon_links()

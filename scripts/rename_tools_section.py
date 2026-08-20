#!/usr/bin/env python3
import os
import sys

def rename_tools_references():
    html_files = []
    # Walk the directory to find all .html files (excluding hidden directories)
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files to process.")

    replacements = [
        ('href="/tools/" class="nav-link">Tools</a>', 'href="/tools/" class="nav-link">Free Tools</a>'),
        ('href="/tools/" class="nav-link active">Tools</a>', 'href="/tools/" class="nav-link active">Free Tools</a>'),
        ('href="/tools/">Tools</a>', 'href="/tools/">Free Tools</a>'),
        ('aria-current="page">Tools</span>', 'aria-current="page">Free Tools</span>'),
        ('"name": "Tools",\n        "item": "https://sudogrep.in/tools/"', '"name": "Free Tools",\n        "item": "https://sudogrep.in/tools/"'),
        ('"name": "Tools",\r\n        "item": "https://sudogrep.in/tools/"', '"name": "Free Tools",\r\n        "item": "https://sudogrep.in/tools/"'),
    ]

    modified_count = 0
    for file_path in html_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            continue

        changed = False
        new_content = content
        for original, replaced in replacements:
            if original in new_content:
                new_content = new_content.replace(original, replaced)
                changed = True

        if changed:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated: {file_path}")
                modified_count += 1
            except Exception as e:
                print(f"Error writing {file_path}: {e}", file=sys.stderr)

    print(f"Completed: Renamed references in {modified_count} out of {len(html_files)} HTML files.")

if __name__ == "__main__":
    rename_tools_references()

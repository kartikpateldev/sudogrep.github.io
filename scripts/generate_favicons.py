#!/usr/bin/env python3
import os
import json
import sys
from PIL import Image

def generate_favicons():
    source_path = "assets/logo_square.png"
    if not os.path.exists(source_path):
        print(f"Error: Source image '{source_path}' does not exist!", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading source image: {source_path}")
    try:
        img = Image.open(source_path)
    except Exception as e:
        print(f"Error opening source image: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Determine the resampling filter based on Pillow version
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        # Fallback for older Pillow versions
        resample_filter = Image.ANTIALIAS
        
    # 1. Save favicon.ico with multiple sizes (16x16, 32x32, 48x48)
    ico_path = "favicon.ico"
    print(f"Generating {ico_path}...")
    try:
        img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    except Exception as e:
        print(f"Error saving favicon.ico: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 2. Save individual PNGs
    png_specs = {
        "favicon-16x16.png": (16, 16),
        "favicon-32x32.png": (32, 32),
        "apple-touch-icon.png": (180, 180),
        "android-chrome-192x192.png": (192, 192),
        "android-chrome-512x512.png": (512, 512)
    }
    
    for filename, size in png_specs.items():
        print(f"Generating {filename} ({size[0]}x{size[1]})...")
        try:
            resized_img = img.resize(size, resample=resample_filter)
            resized_img.save(filename, format="PNG")
        except Exception as e:
            print(f"Error generating {filename}: {e}", file=sys.stderr)
            sys.exit(1)
            
    # 3. Create site.webmanifest
    manifest_path = "site.webmanifest"
    print(f"Generating {manifest_path}...")
    manifest_data = {
        "name": "SudoGrep",
        "short_name": "SudoGrep",
        "icons": [
            {
                "src": "/android-chrome-192x192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/android-chrome-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ],
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "display": "standalone"
    }
    
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
    except Exception as e:
        print(f"Error saving site.webmanifest: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Favicon generation completed successfully.")

if __name__ == "__main__":
    generate_favicons()

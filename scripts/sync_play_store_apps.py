#!/usr/bin/env python3
"""
Sync Play Store Apps
--------------------
Automatically fetches all published Android applications from Google Play Store for developer SudoGrep,
downloads app icons, feature graphics, and screenshot previews, and updates data/apps.json.
"""

import os
import sys
import re
import json
import urllib.request
from io import BytesIO
from PIL import Image
from google_play_scraper import app as fetch_app_details

SLUG_MAPPING = {
    "in.sudogrep.ghosttrap": "ghost-trap",
    "in.sudogrep.kb_snap": "kb-snap",
    "dev.kartikpatel.fileforge": "file-forge",
    "com.billreminder.bill_reminder": "billbuddy",
    "in.sudogrep.zip_connect": "zip-connect",
    "in.sudogrep.zip_connect_free": "zip-connect-plus",
    "com.kp.kartik.aarti": "aarti-sangrah"
}

PRESERVED_APP_CONFIGS = {
    "kb-snap": {
        "features": [
            "Compress photos to specific target KB sizes",
            "Batch photo resizing and image scaling",
            "Aspect ratio cropping for signature and passport photos",
            "100% offline-first processing for absolute privacy",
            "No server uploads, ads, or tracking",
            "Clean, modern user interface"
        ]
    },
    "file-forge": {
        "features": [
            "Universal image, video, and audio conversion",
            "EXIF/GPS metadata viewer and editor",
            "Document compression and PDF utilities",
            "On-device OCR text extraction",
            "Offline translation and transliteration tools",
            "Quick QR code scanner and generator"
        ]
    },
    "billbuddy": {
        "features": [
            "Unified tracking of EMIs, bills, and subscriptions",
            "Smart upcoming reminders and notifications",
            "Visual calendar interface for due dates",
            "Borrow/Lend records tracker",
            "SMS payment parsing engine",
            "CSV and PDF data export"
        ]
    },
    "zip-connect": {
        "features": [
            "Hundreds of challenging node puzzles",
            "Interactive levels with escalating difficulty",
            "Minimalist visual design with smooth transitions",
            "100% offline gameplay support",
            "No intrusive tracking or ads",
            "Quick level reset and help options"
        ]
    },
    "zip-connect-plus": {
        "features": [
            "Hundreds of challenging node puzzles",
            "Interactive levels with escalating difficulty",
            "Minimalist visual design with smooth transitions",
            "100% offline gameplay support",
            "No intrusive tracking or ads"
        ]
    },
    "aarti-sangrah": {
        "features": [
            "Comprehensive local prayer list",
            "Devotional lyrics categorized logically",
            "Adjustable font sizing and reading modes",
            "Full offline access without internet",
            "Minimalistic user interface",
            "Zero tracking or permissions"
        ]
    },
    "ghost-trap": {
        "features": [
            "Territory claiming gameplay",
            "Strategic ghost avoidance",
            "World landmark discovery",
            "Progressive difficulty",
            "Speeder, Frost and Freeze power-ups",
            "Offline play",
            "Cloud save",
            "Reward system",
            "Optional in-app purchases"
        ]
    }
}


def download_and_save_image(url, save_path, size=None):
    if not url:
        return False
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            img_data = response.read()
        img = Image.open(BytesIO(img_data))
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(save_path, 'WEBP', quality=92, optimize=True)
        return True
    except Exception as e:
        print(f"  Warning: Failed to download image from {url}: {e}", file=sys.stderr)
        return False


def get_dev_package_ids(developer_id):
    url = f"https://play.google.com/store/apps/dev?id={developer_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
        package_ids = list(set(re.findall(r'/store/apps/details\?id=([a-zA-Z0-9_\.]+)', html)))
        return package_ids
    except Exception as e:
        print(f"Error fetching developer page for ID {developer_id}: {e}", file=sys.stderr)
        return []


def sync_play_store(dev_id="7135905913091619860", apps_json_path="data/apps.json"):
    print(f"Syncing apps from Google Play Store (Developer ID: {dev_id})...")

    # Load existing apps.json to preserve any existing custom metadata if needed
    existing_apps_dict = {}
    if os.path.exists(apps_json_path):
        try:
            with open(apps_json_path, 'r', encoding='utf-8') as f:
                existing_list = json.load(f)
                for item in existing_list:
                    existing_apps_dict[item.get("package_name")] = item
                    existing_apps_dict[item.get("slug")] = item
        except Exception as e:
            print(f"Note: Could not parse existing {apps_json_path}: {e}")

    package_ids = get_dev_package_ids(dev_id)
    if not package_ids:
        print("Warning: No packages found on developer page. Using fallback package list.", file=sys.stderr)
        package_ids = list(SLUG_MAPPING.keys())

    synced_apps = []

    for pkg_id in sorted(package_ids):
        print(f"\nFetching Play Store details for package: {pkg_id}")
        try:
            detail = fetch_app_details(pkg_id, lang='en', country='us')
        except Exception as e:
            print(f"  Error fetching Play Store details for {pkg_id}: {e}", file=sys.stderr)
            if pkg_id in existing_apps_dict:
                synced_apps.append(existing_apps_dict[pkg_id])
            continue

        slug = SLUG_MAPPING.get(pkg_id)
        if not slug:
            raw_title = detail.get('title', pkg_id)
            slug = re.sub(r'[^a-z0-9]+', '-', raw_title.lower()).strip('-')

        print(f"  Mapped slug: '{slug}' | Title: '{detail.get('title')}'")

        app_dir = os.path.join("assets", "apps", slug)
        os.makedirs(app_dir, exist_ok=True)

        # Download App Icon
        icon_url = detail.get("icon")
        icon_path = os.path.join(app_dir, "icon.webp")
        if icon_url:
            print(f"  Downloading app icon...")
            download_and_save_image(icon_url, icon_path, size=(512, 512))

        # Download Feature Graphic / Header Image
        feature_url = detail.get("headerImage")
        feature_path = os.path.join(app_dir, "feature_graphic.webp")
        has_feature_graphic = False
        if feature_url:
            print(f"  Downloading feature graphic...")
            has_feature_graphic = download_and_save_image(feature_url, feature_path)

        # Download Screenshots (up to 6)
        screenshots_urls = detail.get("screenshots", [])
        saved_screenshots = []
        screenshots_dir = os.path.join(app_dir, "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        for idx, shot_url in enumerate(screenshots_urls[:6]):
            shot_path = os.path.join(screenshots_dir, f"screen_{idx + 1}.webp")
            print(f"  Downloading screenshot {idx + 1}/{min(len(screenshots_urls), 6)}...")
            if download_and_save_image(shot_url, shot_path):
                saved_screenshots.append(f"assets/apps/{slug}/screenshots/screen_{idx + 1}.webp")

        # Determine features
        features = []
        if slug in PRESERVED_APP_CONFIGS and "features" in PRESERVED_APP_CONFIGS[slug]:
            features = PRESERVED_APP_CONFIGS[slug]["features"]
        elif detail.get("description"):
            # Try to extract bullet points from description
            raw_desc = detail.get("description", "")
            bullets = re.findall(r'[\u2022\*\-]\s*(.*)', raw_desc)
            if bullets:
                features = [b.strip() for b in bullets[:6] if len(b.strip()) > 3]

        if not features:
            features = [
                "Official Google Play Store release",
                "High performance & lightweight Android optimization",
                "Designed with privacy & security first",
                "Regular updates and continuous support"
            ]

        play_store_url = detail.get("url") or f"https://play.google.com/store/apps/details?id={pkg_id}"

        app_entry = {
            "name": detail.get("title"),
            "slug": slug,
            "package_name": pkg_id,
            "play_store_url": play_store_url,
            "icon": f"assets/apps/{slug}/icon.webp",
            "feature_graphic": f"assets/apps/{slug}/feature_graphic.webp" if has_feature_graphic else "",
            "short_description": detail.get("summary") or detail.get("title"),
            "description": detail.get("description") or detail.get("summary"),
            "features": features,
            "screenshots": saved_screenshots,
            "score": detail.get("score"),
            "installs": detail.get("installs"),
            "developer": detail.get("developer", "SudoGrep"),
            "status": "Live"
        }

        synced_apps.append(app_entry)

    # Save to data/apps.json
    with open(apps_json_path, 'w', encoding='utf-8') as f:
        json.dump(synced_apps, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Successfully synced {len(synced_apps)} apps to {apps_json_path}")
    return synced_apps


if __name__ == "__main__":
    dev_id = "7135905913091619860"
    config_path = os.path.join("data", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                dev_id = cfg.get("PLAY_STORE_DEV_ID", dev_id)
        except Exception:
            pass

    sync_play_store(dev_id=dev_id)

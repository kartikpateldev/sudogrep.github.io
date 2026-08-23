#!/usr/bin/env python3
import json
import os

def update_seo_configs():
    pages_json_path = "data/pages.json"
    if not os.path.exists(pages_json_path):
        print(f"Error: {pages_json_path} not found!")
        return

    with open(pages_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. We will build a new dict
    new_data = {}

    for path, entry in data.items():
        # Skip the legacy redirect page index "/guides/" to remove it from audit checks
        if path == "/guides/":
            continue

        current_path = path
        # Rename key "/guides/..." to "/blog/..."
        if path.startswith("/guides/"):
            current_path = path.replace("/guides/", "/blog/")
            entry["url"] = current_path
            if "canonical" in entry:
                entry["canonical"] = entry["canonical"].replace("/guides/", "/blog/")

        if entry.get("schema_type") == "Article":
            entry["schema_type"] = "BlogPosting"

        # Replace internal guides links inside each page's config
        if "related_guides" in entry:
            entry["related_guides"] = [g.replace("/guides/", "/blog/") for g in entry["related_guides"]]
        if "recommended_internal_links" in entry:
            entry["recommended_internal_links"] = [l.replace("/guides/", "/blog/") for l in entry["recommended_internal_links"]]
            # Also clean up any legacy "/guides/" index links to "/blog/"
            entry["recommended_internal_links"] = [l if l != "/guides/" else "/blog/" for l in entry["recommended_internal_links"]]

        new_data[current_path] = entry

    # 2. Add the 3 missing blog posts if they are not already there
    missing_posts = {
        "/blog/how-ai-agents-are-changing-software-development/": {
            "url": "/blog/how-ai-agents-are-changing-software-development/",
            "title": "How AI Agents Are Changing Software Development | SudoGrep",
            "description": "Discover how task-oriented autonomous AI agents are moving beyond autocomplete assistants to automate software engineering workflows.",
            "h1": "How AI Agents Are Changing Software Development",
            "primary_intent": "understand ai agent impact on software development",
            "secondary_intents": [
                "ai agent developer tools",
                "autonomous coding agents"
            ],
            "primary_topic": "AI Agents",
            "secondary_topics": [
                "software engineering automation",
                "agentic workflows"
            ],
            "search_variations": [
                "ai agents software development",
                "autonomous ai coders"
            ],
            "target_entities": [
                "AI agents",
                "software engineering",
                "agentic coding"
            ],
            "related_tools": [
                "/free-tools/"
            ],
            "related_guides": [],
            "recommended_internal_links": [
                "/blog/"
            ],
            "primary_keywords": [
                "ai agents software development"
            ],
            "secondary_keywords": [
                "autonomous coding agents",
                "agentic AI"
            ],
            "canonical": "https://sudogrep.in/blog/how-ai-agents-are-changing-software-development/",
            "og_title": "How AI Agents Are Changing Software Development | SudoGrep",
            "og_description": "Discover how task-oriented autonomous AI agents are moving beyond autocomplete assistants to automate software engineering workflows.",
            "og_image": "https://sudogrep.in/assets/logo_square.png",
            "schema_type": "BlogPosting"
        },
        "/blog/flutter-app-development-trends-2026/": {
            "url": "/blog/flutter-app-development-trends-2026/",
            "title": "Flutter App Development Trends in 2026 | SudoGrep",
            "description": "Explore the top Flutter mobile engineering trends in 2026: WebAssembly (WASM), local-first databases, on-device AI integration, and riverpod patterns.",
            "h1": "Flutter App Development Trends in 2026",
            "primary_intent": "discover flutter mobile engineering trends in 2026",
            "secondary_intents": [
                "flutter webassembly WASM",
                "on-device AI integration"
            ],
            "primary_topic": "Flutter Mobile Trends",
            "secondary_topics": [
                "local-first databases",
                "riverpod patterns"
            ],
            "search_variations": [
                "flutter trends 2026",
                "flutter mobile development 2026"
            ],
            "target_entities": [
                "Flutter",
                "WASM",
                "local-first",
                "on-device AI"
            ],
            "related_tools": [
                "/free-tools/"
            ],
            "related_guides": [],
            "recommended_internal_links": [
                "/blog/"
            ],
            "primary_keywords": [
                "flutter trends 2026"
            ],
            "secondary_keywords": [
                "flutter mobile development",
                "riverpod pattern"
            ],
            "canonical": "https://sudogrep.in/blog/flutter-app-development-trends-2026/",
            "og_title": "Flutter App Development Trends in 2026 | SudoGrep",
            "og_description": "Explore the top Flutter mobile engineering trends in 2026: WebAssembly (WASM), local-first databases, on-device AI integration, and riverpod patterns.",
            "og_image": "https://sudogrep.in/assets/logo_square.png",
            "schema_type": "BlogPosting"
        },
        "/blog/best-free-image-compression-tools/": {
            "url": "/blog/best-free-image-compression-tools/",
            "title": "Best Free Image Compression Tools (Offline & Online) | SudoGrep",
            "description": "Compare the best free image compression tools. Find privacy-first client-side compressors, traditional cloud optimizers, and dev command-line tools.",
            "h1": "Best Free Image Compression Tools",
            "primary_intent": "compare the best free image compression tools",
            "secondary_intents": [
                "privacy-first client-side compressor",
                "free online image optimizer"
            ],
            "primary_topic": "Image Compression Tools",
            "secondary_topics": [
                "local offline compressor",
                "cloud image compression"
            ],
            "search_variations": [
                "best free image compression tools",
                "free image compressors online"
            ],
            "target_entities": [
                "image compression",
                "offline tools",
                "online optimizers"
            ],
            "related_tools": [
                "/image-compressor/",
                "/compress-image-to-50kb/"
            ],
            "related_guides": [],
            "recommended_internal_links": [
                "/blog/"
            ],
            "primary_keywords": [
                "best free image compression tools"
            ],
            "secondary_keywords": [
                "free image compressors",
                "offline image tools"
            ],
            "canonical": "https://sudogrep.in/blog/best-free-image-compression-tools/",
            "og_title": "Best Free Image Compression Tools (Offline & Online) | SudoGrep",
            "og_description": "Compare the best free image compression tools. Find privacy-first client-side compressors, traditional cloud optimizers, and dev command-line tools.",
            "og_image": "https://sudogrep.in/assets/logo_square.png",
            "schema_type": "BlogPosting"
        }
    }

    for path, entry in missing_posts.items():
        if path not in new_data:
            new_data[path] = entry

    # 3. Resolve keyword cannibalization conflicts
    # Let's verify and update specific pages targeting the same primary keywords
    
    # Conflict A: "compress image to 100kb"
    # - Tool: /compress-image-to-100kb/
    # - Article: /blog/how-to-compress-image-to-100kb/
    if "/compress-image-to-100kb/" in new_data:
        new_data["/compress-image-to-100kb/"]["primary_keywords"] = ["compress image to 100kb online"]
    if "/blog/how-to-compress-image-to-100kb/" in new_data:
        new_data["/blog/how-to-compress-image-to-100kb/"]["primary_keywords"] = ["how to compress image to 100kb"]

    # Conflict B: "resize image for online forms"
    # - Tool: /resize-image-for-online-forms/
    # - Article: /blog/resize-images-for-online-forms/
    if "/resize-image-for-online-forms/" in new_data:
        new_data["/resize-image-for-online-forms/"]["primary_keywords"] = ["resize image for online forms online"]
    if "/blog/resize-images-for-online-forms/" in new_data:
        new_data["/blog/resize-images-for-online-forms/"]["primary_keywords"] = ["how to resize an image for online forms"]

    # Conflict C: "custom ai solutions"
    # - Directory: /ai-solutions/
    # - Service: /services/ai-development/
    if "/ai-solutions/" in new_data:
        new_data["/ai-solutions/"]["primary_keywords"] = ["custom ai solutions and systems", "ai integration services"]
    if "/services/ai-development/" in new_data:
        new_data["/services/ai-development/"]["primary_keywords"] = ["custom ai integration services"]

    # 4. Save file
    with open(pages_json_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print("Successfully updated pages.json SEO configurations.")

if __name__ == "__main__":
    update_seo_configs()

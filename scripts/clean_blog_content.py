#!/usr/bin/env python3
import re
from pathlib import Path

CONTENT_DIR = Path("data/blog_content")

def clean_blog_content():
    for file_path in CONTENT_DIR.glob("*.html"):
        content = file_path.read_text(encoding="utf-8")
        original = content

        # 1. Replace /free-tools/ with /tools/
        content = re.sub(r'href="/free-tools/"', 'href="/tools/"', content)

        # 2. Replace old redirect URLs with canonical URLs
        content = content.replace('/guides/resize-images-for-online-forms/', '/guides/how-to-resize-image-for-online-forms/')
        content = content.replace('/guides/how-to-reduce-jpg-file-size/', '/guides/how-to-reduce-jpg-size/')

        # 3. Ensure <section class="article-faq"> is properly closed before <section class="related-resources">
        if '<section class="article-faq">' in content:
            # Check if there is a closing </section> before <section class="related-resources">
            faq_split = content.split('<section class="article-faq">')
            before_faq = faq_split[0]
            rest = faq_split[1]

            if '<section class="related-resources"' in rest:
                between_parts = rest.split('<section class="related-resources"')
                faq_body = between_parts[0]
                related_body = '<section class="related-resources"' + between_parts[1]

                if '</section>' not in faq_body:
                    faq_body = faq_body.rstrip() + '\n          </section>\n\n          '
                    content = before_faq + '<section class="article-faq">' + faq_body + related_body
            else:
                # If no related resources, check if </section> closes the faq at the end
                if '</section>' not in rest:
                    content = content.rstrip() + '\n          </section>\n'

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            print(f"Fixed {file_path.name}")
        else:
            print(f"No change for {file_path.name}")

if __name__ == "__main__":
    clean_blog_content()

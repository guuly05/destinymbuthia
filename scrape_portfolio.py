import urllib.request
import json
import re
import os
import ssl
from html.parser import HTMLParser

# Create SSL context to bypass SSL issues
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://www.destinymbuthia.com"
OUTPUT_DIR = os.path.join(os.getcwd(), "assets", "destiny_photos")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class LinkAndImgExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.images = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == 'a' and 'href' in attr_dict:
            self.links.add(attr_dict['href'])
        elif tag == 'img':
            src = attr_dict.get('data-src') or attr_dict.get('src')
            alt = attr_dict.get('alt') or 'photo'
            if src:
                self.images.append((src, alt))

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def main():
    print("--- Starting Scraping of destinymbuthia.com ---")
    
    # 1. Fetch homepage
    html = fetch_url(BASE_URL)
    if not html:
        print("Failed to load homepage.")
        return

    parser = LinkAndImgExtractor()
    parser.feed(html)
    
    # Extract interior links
    valid_links = set()
    for href in parser.links:
        if href.startswith('/') and not href.startswith('//'):
            valid_links.add(href)
        elif href.startswith(BASE_URL):
            valid_links.add(href.replace(BASE_URL, ''))
            
    print(f"Found navigation/collection links: {valid_links}")
    
    all_pages = set(['/']).union(valid_links)
    
    downloaded_count = 0
    categories_found = {}

    for page_path in all_pages:
        # Ignore external links, anchor links, mailto
        if page_path.startswith('#') or page_path.startswith('mailto:') or 'squarespace' in page_path or 'cart' in page_path:
            continue
            
        page_url = f"{BASE_URL}{page_path}"
        category_name = page_path.strip('/').replace('/', '_')
        if not category_name:
            category_name = "home"
            
        print(f"\nProcessing category/page: '{category_name}' from {page_url}")
        
        # Try fetching JSON endpoint first (Squarespace structured data)
        json_url = f"{page_url}?format=json"
        json_data = fetch_url(json_url)
        
        page_images = []
        
        if json_data:
            try:
                data = json.loads(json_data)
                
                # Check for collection items
                items = []
                if 'items' in data:
                    items = data['items']
                elif 'mainContent' in data and 'items' in data['mainContent']:
                    items = data['mainContent']['items']
                elif 'collection' in data and 'items' in data['collection']:
                    items = data['collection']['items']
                    
                for item in items:
                    img_url = item.get('assetUrl') or item.get('imageUrl')
                    title = item.get('title') or item.get('filename') or item.get('body') or 'photo'
                    if img_url:
                        page_images.append((img_url, str(title)))
            except Exception as json_err:
                print(f"JSON endpoint parsing note: {json_err}")

        # Fallback to HTML parsing if JSON didn't yield images
        if not page_images:
            page_html = fetch_url(page_url)
            page_parser = LinkAndImgExtractor()
            page_parser.feed(page_html)
            
            for src, alt in page_parser.images:
                if src.startswith('//'):
                    src = 'https:' + src
                raw_src = re.sub(r'\?.*$', '', src)
                if 'squarespace-cdn.com' in raw_src:
                    page_images.append((raw_src, alt))

        # Deduplicate images for this category
        seen_urls = set()
        unique_images = []
        for u, t in page_images:
            base_u = u.split('?')[0]
            if base_u not in seen_urls:
                seen_urls.add(base_u)
                unique_images.append((base_u, t))

        print(f"Found {len(unique_images)} unique images for category '{category_name}'")
        
        # Create category subfolder
        cat_dir = os.path.join(OUTPUT_DIR, category_name)
        os.makedirs(cat_dir, exist_ok=True)
        
        categories_found[category_name] = []
        
        for idx, (img_url, img_title) in enumerate(unique_images):
            download_url = img_url + "?format=2500w" if "?" not in img_url else img_url
            
            # Clean title for filename
            clean_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', img_title[:25]).strip('_')
            if not clean_title or clean_title == "photo":
                clean_title = f"shot"
                
            filename = f"{clean_title}_{idx+1}.jpg"
            filepath = os.path.join(cat_dir, filename)
            
            try:
                req = urllib.request.Request(download_url, headers=headers)
                with urllib.request.urlopen(req, context=ctx) as response, open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
                    
                rel_path = os.path.relpath(filepath, os.getcwd()).replace('\\', '/')
                categories_found[category_name].append({
                    "url": img_url,
                    "title": img_title,
                    "local_path": rel_path
                })
                downloaded_count += 1
                print(f" Saved: {rel_path}")
            except Exception as dl_err:
                print(f" Failed to download {download_url}: {dl_err}")

    # Save summary manifest
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(categories_found, f, indent=2)
        
    print(f"\n Scraping complete! Total downloaded: {downloaded_count} photos.")
    print(f" Manifest saved to {manifest_path}")

if __name__ == '__main__':
    main()

import urllib.request
import json
import re
import os
import ssl
from html.parser import HTMLParser

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://www.destinymbuthia.com"
OUTPUT_DIR = os.path.join(os.getcwd(), "assets", "destiny_photos")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class LinkExtractor(HTMLParser):
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
            alt = attr_dict.get('alt') or attr_dict.get('title') or ''
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

def crawl_site():
    print("--- Starting Deep Category Scraper for destinymbuthia.com ---")
    
    # Target initial sub-galleries discovered
    seed_urls = [
        '/',
        '/portfolio',
        '/fashion',
        '/portraits',
        '/landscape',
        '/photoshoots',
        '/graduates',
        '/film',
        '/digital',
        '/editorial',
        '/about'
    ]
    
    visited_pages = set()
    to_visit = set(seed_urls)
    
    # 1. Discover all interior gallery links
    while to_visit:
        path = to_visit.pop()
        if path in visited_pages or 'cart' in path or 'mailto' in path or '#' in path:
            continue
            
        visited_pages.add(path)
        url = f"{BASE_URL}{path}"
        print(f"Discovering links from: {url}")
        
        html = fetch_url(url)
        if not html:
            continue
            
        parser = LinkExtractor()
        parser.feed(html)
        
        for href in parser.links:
            if href.startswith('/') and not href.startswith('//'):
                if href not in visited_pages and not any(href.endswith(ext) for ext in ['.jpg', '.png', '.css', '.js']):
                    to_visit.add(href)
            elif href.startswith(BASE_URL):
                clean_p = href.replace(BASE_URL, '')
                if clean_p not in visited_pages:
                    to_visit.add(clean_p)

    print(f"\nAll discovered portfolio categories/pages ({len(visited_pages)}): {sorted(list(visited_pages))}")
    
    total_downloaded = 0
    categories_manifest = {}

    for page_path in sorted(list(visited_pages)):
        category_name = page_path.strip('/').replace('/', '_')
        if not category_name:
            category_name = "home"
            
        print(f"\n==========================================")
        print(f"Scraping Category: '{category_name.upper()}'")
        print(f"==========================================")
        
        page_url = f"{BASE_URL}{page_path}"
        
        # Try JSON format first (Squarespace API endpoint)
        page_images = []
        json_url = f"{page_url}?format=json"
        json_data = fetch_url(json_url)
        
        if json_data:
            try:
                data = json.loads(json_data)
                
                # Check for items inside collection or mainContent
                items = []
                if 'items' in data:
                    items = data['items']
                elif 'collection' in data and 'items' in data['collection']:
                    items = data['collection']['items']
                elif 'mainContent' in data and 'items' in data['mainContent']:
                    items = data['mainContent']['items']
                    
                for item in items:
                    img_url = item.get('assetUrl') or item.get('imageUrl')
                    title = item.get('title') or item.get('filename') or ''
                    if img_url:
                        page_images.append((img_url, title))
            except Exception as e:
                pass

        # Fallback to HTML image parsing
        page_html = fetch_url(page_url)
        if page_html:
            parser = LinkExtractor()
            parser.feed(page_html)
            for src, alt in parser.images:
                if src.startswith('//'):
                    src = 'https:' + src
                raw_src = re.sub(r'\?.*$', '', src)
                if 'squarespace-cdn.com' in raw_src:
                    page_images.append((raw_src, alt))

        # Deduplicate
        seen_urls = set()
        unique_images = []
        for u, t in page_images:
            clean_u = u.split('?')[0]
            if clean_u not in seen_urls and 'favicon' not in clean_u and 'logo' not in clean_u:
                seen_urls.add(clean_u)
                unique_images.append((clean_u, t))

        print(f"Found {len(unique_images)} images for category '{category_name}'")
        
        if not unique_images:
            continue

        # Create category folder
        cat_dir = os.path.join(OUTPUT_DIR, category_name)
        os.makedirs(cat_dir, exist_ok=True)
        
        categories_manifest[category_name] = []
        
        for idx, (img_url, img_title) in enumerate(unique_images):
            download_url = f"{img_url}?format=2500w"
            
            clean_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', img_title[:30]).strip('_')
            if not clean_title:
                clean_title = f"{category_name}_photo"
                
            filename = f"{clean_title}_{idx+1}.jpg"
            filepath = os.path.join(cat_dir, filename)
            
            try:
                req = urllib.request.Request(download_url, headers=headers)
                with urllib.request.urlopen(req, context=ctx) as resp, open(filepath, 'wb') as f:
                    f.write(resp.read())
                    
                rel_path = os.path.relpath(filepath, os.getcwd()).replace('\\', '/')
                categories_manifest[category_name].append({
                    "url": img_url,
                    "title": img_title or f"{category_name} photo {idx+1}",
                    "local_path": rel_path,
                    "category": category_name
                })
                total_downloaded += 1
                print(f"  [+] Saved [{category_name}]: {filename}")
            except Exception as dl_err:
                print(f"  [-] Error downloading {download_url}: {dl_err}")

    # Write full manifest JSON file
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(categories_manifest, f, indent=2)

    print(f"\n==========================================")
    print(f"SUCCESSFULLY SCRAPED {total_downloaded} REAL PHOTOS FROM DESTINY'S PORTFOLIO!")
    print(f"Categories Saved: {list(categories_manifest.keys())}")
    print(f"Manifest File: {manifest_path}")
    print(f"==========================================")

if __name__ == '__main__':
    crawl_site()

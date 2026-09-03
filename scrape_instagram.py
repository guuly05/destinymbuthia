import urllib.request
import json
import re
import os
import ssl
from html.parser import HTMLParser

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

USERNAME = "des.narratives"
OUTPUT_DIR = os.path.join(os.getcwd(), "assets", "destiny_photos", "instagram")
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-IG-App-ID': '936619743392459',
    'Accept-Language': 'en-US,en;q=0.9',
}

class MetaImgExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == 'meta':
            prop = attr_dict.get('property') or attr_dict.get('name')
            content = attr_dict.get('content')
            if prop in ['og:image', 'twitter:image'] and content:
                self.images.append(content)
        elif tag == 'img':
            src = attr_dict.get('src')
            if src and ('cdninstagram.com' in src or 'fbcdn.net' in src):
                self.images.append(src)

def fetch_url(url, extra_headers=None):
    req_headers = headers.copy()
    if extra_headers:
        req_headers.update(extra_headers)
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Fetch error for {url}: {e}")
        return ""

def main():
    print(f"--- Fetching Instagram media for @{USERNAME} ---")
    
    downloaded_images = []
    
    # Method 1: Web profile info API
    api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={USERNAME}"
    print(f"Trying Instagram API endpoint: {api_url}")
    json_text = fetch_url(api_url)
    
    if json_text:
        try:
            data = json.loads(json_text)
            user = data.get('data', {}).get('user', {})
            timeline = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
            
            print(f"Found {len(timeline)} timeline posts via Instagram API!")
            
            for idx, edge in enumerate(timeline):
                node = edge.get('node', {})
                display_url = node.get('display_url')
                caption = ""
                edges = node.get('edge_media_to_caption', {}).get('edges', [])
                if edges:
                    caption = edges[0].get('node', {}).get('text', '')
                    
                if display_url:
                    downloaded_images.append((display_url, caption or f"Instagram Post {idx+1}"))
        except Exception as e:
            print(f"API parse error: {e}")

    # Method 2: Fallback to profile page HTML parsing if API returned no media
    if not downloaded_images:
        profile_url = f"https://www.instagram.com/{USERNAME}/"
        print(f"Falling back to profile HTML scraping: {profile_url}")
        html = fetch_url(profile_url)
        
        if html:
            # Try searching for JSON script blocks inside HTML
            script_matches = re.findall(r'<script type="text/javascript">window\._sharedData = (.*?);</script>', html)
            if script_matches:
                try:
                    shared_data = json.loads(script_matches[0])
                    entry_data = shared_data.get('entry_data', {}).get('ProfilePage', [])
                    if entry_data:
                        user = entry_data[0].get('graphql', {}).get('user', {})
                        edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
                        for idx, edge in enumerate(edges):
                            node = edge.get('node', {})
                            url = node.get('display_url')
                            if url:
                                downloaded_images.append((url, f"Instagram Post {idx+1}"))
                except Exception as err:
                    print(f"SharedData parse error: {err}")

            # HTML meta tags fallback
            parser = MetaImgExtractor()
            parser.feed(html)
            for img_src in parser.images:
                downloaded_images.append((img_src, "Instagram Photo"))

    # Deduplicate URLs
    seen_urls = set()
    unique_photos = []
    for u, cap in downloaded_images:
        clean_u = u.split('?')[0]
        if clean_u not in seen_urls and 'profile' not in clean_u:
            seen_urls.add(clean_u)
            unique_photos.append((u, cap))

    print(f"\nTotal Instagram photos found: {len(unique_photos)}")
    
    saved_paths = []
    for idx, (img_url, cap) in enumerate(unique_photos):
        filename = f"ig_des_narratives_{idx+1}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as resp, open(filepath, 'wb') as f:
                f.write(resp.read())
            
            rel_path = os.path.relpath(filepath, os.getcwd()).replace('\\', '/')
            saved_paths.append({
                "url": img_url,
                "caption": cap,
                "local_path": rel_path
            })
            print(f" Saved Instagram Photo [{idx+1}]: {rel_path}")
        except Exception as dl_err:
            print(f" Failed to download IG photo {idx+1}: {dl_err}")

    # Write IG manifest
    ig_manifest_path = os.path.join(OUTPUT_DIR, "ig_manifest.json")
    with open(ig_manifest_path, 'w', encoding='utf-8') as f:
        json.dump(saved_paths, f, indent=2)
        
    print(f"\nInstagram Scraping Complete! {len(saved_paths)} images saved to {OUTPUT_DIR}")

if __name__ == '__main__':
    main()

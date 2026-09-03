import urllib.request
import json
import re
import os
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

USERNAME = "des.narratives"
OUTPUT_DIR = os.path.join(os.getcwd(), "assets", "destiny_photos", "instagram")
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Fetch error for {url}: {e}")
        return ""

def main():
    print(f"--- Fetching Instagram media for @{USERNAME} ---")
    
    # 1. Search engine image cache for des.narratives instagram
    search_url = f"https://html.duckduckgo.com/html/?q=site:instagram.com/des.narratives"
    print(f"Searching index for Instagram posts: {search_url}")
    html = fetch_url(search_url)
    
    post_urls = set()
    if html:
        matches = re.findall(r'instagram\.com/p/([A-Za-z0-9_\-]+)', html)
        for code in matches:
            post_urls.add(f"https://www.instagram.com/p/{code}/")
            
    print(f"Discovered Instagram post URLs: {post_urls}")
    
    found_images = []
    
    # Try fetching images from post embed pages
    for p_url in post_urls:
        embed_url = f"https://api.instagram.com/oembed/?url={p_url}"
        embed_json = fetch_url(embed_url)
        if embed_json:
            try:
                data = json.loads(embed_json)
                thumbnail_url = data.get('thumbnail_url')
                title = data.get('title') or "Instagram Shoot"
                if thumbnail_url:
                    found_images.append((thumbnail_url, title))
            except Exception as e:
                pass

    # Deduplicate
    unique_imgs = list(dict.fromkeys(found_images))
    print(f"Found {len(unique_imgs)} Instagram post images via oEmbed!")

    saved_count = 0
    for idx, (img_url, cap) in enumerate(unique_imgs):
        filename = f"ig_photo_{idx+1}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as resp, open(filepath, 'wb') as f:
                f.write(resp.read())
                
            rel_path = os.path.relpath(filepath, os.getcwd()).replace('\\', '/')
            saved_count += 1
            print(f"  [+] Saved Instagram Photo [{idx+1}]: {rel_path}")
        except Exception as err:
            print(f"  [-] Failed to download {img_url}: {err}")

    # Create an Instagram Feed Component in HTML/JS
    print(f"\nCompleted! Saved {saved_count} Instagram photos.")

if __name__ == '__main__':
    main()

import urllib.request
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
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
    print(f"--- Fetching Instagram media for @{USERNAME} via public mirrors ---")
    
    # Try public IG mirror services
    mirror_urls = [
        f"https://imginn.com/{USERNAME}/",
        f"https://www.picnob.com/profile/{USERNAME}/",
        f"https://pixwox.com/profile/{USERNAME}/"
    ]
    
    found_images = []

    for m_url in mirror_urls:
        print(f"Checking mirror: {m_url}")
        html = fetch_url(m_url)
        if not html:
            continue
            
        # Extract images from mirror HTML
        # Imginn uses <img src="..."> with scontent or cdn instagram URLs or imginn CDN
        img_matches = re.findall(r'src=["\'](https?://[^"\']+(?:scontent|cdninstagram|imginn)[^"\']+)["\']', html)
        for img in img_matches:
            if 'avatar' not in img and 'logo' not in img:
                found_images.append(img)
                
        if found_images:
            print(f" Found {len(found_images)} photos from {m_url}!")
            break

    # Deduplicate
    unique_imgs = list(dict.fromkeys(found_images))
    print(f"\nTotal unique Instagram photos found: {len(unique_imgs)}")

    saved_count = 0
    for idx, img_url in enumerate(unique_imgs):
        filename = f"ig_des_narratives_{idx+1}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as resp, open(filepath, 'wb') as f:
                f.write(resp.read())
                
            rel_path = os.path.relpath(filepath, os.getcwd()).replace('\\', '/')
            saved_count += 1
            print(f"  [+] Saved Instagram Photo [{idx+1}]: {rel_path}")
        except Exception as err:
            print(f"  [-] Failed to download IG photo {idx+1}: {err}")

    print(f"\nInstagram Scraping Complete! Downloaded {saved_count} photos.")

if __name__ == '__main__':
    main()

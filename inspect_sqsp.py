import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
}

req = urllib.request.Request("https://www.destinymbuthia.com/?format=json", headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        print("Site Title:", data.get('website', {}).get('siteTitle'))
        
        # Check navigation / site layout
        nav_items = data.get('siteLayout', {}).get('layout', [])
        print("\nSite Layout Items:")
        print(json.dumps(data.get('navigation', []), indent=2))
        
        # Check collection items if any
        main_nav = data.get('mainNav', [])
        print("\nMain Nav:")
        print(json.dumps(main_nav, indent=2))
        
        print("\nCollection:")
        coll = data.get('collection', {})
        print("Collection Title:", coll.get('title'))
        print("Collection Items Count:", len(coll.get('collections', [])) or len(coll.get('items', [])))
        
        if 'collections' in coll:
            for sub_c in coll['collections']:
                print(f" - SubCollection: {sub_c.get('title')} -> url: {sub_c.get('fullUrl')}")
                
        if 'items' in coll:
            for item in coll['items']:
                print(f" - Item: {item.get('title')} -> assetUrl: {item.get('assetUrl')}")
                
except Exception as e:
    print("Error:", e)

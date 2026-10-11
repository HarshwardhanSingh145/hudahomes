import os
import re
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 1. Read index.html to gather all URLs
with open('index.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

raw_urls = set(re.findall(r'https://almoststone\.com/([a-zA-Z0-9_\-\%/]+)', home_html))

# Filter out non-page URLs
valid_urls = []
for u in sorted(raw_urls):
    if u.startswith('wp-') or u.startswith('comments') or u.startswith('feed') or u.startswith('xmlrpc'):
        continue
    valid_urls.append(u.rstrip('/'))

print(f"Total pages to download and transform: {len(valid_urls)}")

# Header badge and VIP button HTML
HEADER_INJECTIONS = '''
<div class="hh-header-badge"><span class="hh-header-badge-dot"></span><span>Atelier Huda Homes</span></div>
<a href="https://wa.me/918058694217?text=Hello%20Abdul%20Hakim%2C%20I%20would%20like%20to%20inquire%20about%20Huda%20Homes%20luxury%20stone%20collections" target="_blank" rel="noopener" class="hh-header-vip-btn" aria-label="WhatsApp VIP Concierge">
	<svg viewBox="0 0 24 24"><path d="M12.004 2c-5.51 0-9.993 4.483-9.993 9.993 0 1.763.457 3.483 1.326 5.008L2 22l5.174-1.356a9.948 9.948 0 0 0 4.825 1.25c5.512 0 10.001-4.481 10.001-9.991C22.005 6.483 17.514 2 12.004 2zm5.845 14.238c-.244.688-1.22 1.347-1.684 1.419-.464.073-.916.297-2.955-.515-2.603-1.036-4.24-3.702-4.368-3.874-.131-.171-1.047-1.393-1.047-2.656 0-1.263.64-1.884.869-2.128.232-.244.5-.306.668-.306.168 0 .334.003.481.01.147.007.346-.056.543.422.203.49.696 1.696.757 1.821.06.125.094.272.012.434-.081.162-.122.262-.244.406-.122.144-.256.322-.366.431-.122.122-.25.253-.109.497.141.244.628 1.034 1.347 1.675.925.825 1.703 1.081 1.947 1.203.244.122.388.103.481-.003.094-.106.406-.475.516-.638.112-.162.222-.134.375-.078.153.056.969.456 1.134.54.166.081.275.122.316.191.04.07.04.403-.203 1.091z"/></svg>
	<span>VIP Concierge</span>
</a>
'''

# Footer VIP floating pill
FLOATING_CONCIERGE = '''
<!-- Floating VIP WhatsApp Glass Concierge Pill -->
<a href="https://wa.me/918058694217?text=Hello%20Abdul%20Hakim%2C%20I%20would%20like%20to%20inquire%20about%20Huda%20Homes%20luxury%20stone%20collections" target="_blank" rel="noopener" class="hh-floating-concierge" aria-label="WhatsApp VIP Concierge">
  <div class="hh-concierge-icon">
    <svg viewBox="0 0 24 24"><path d="M12.004 2c-5.51 0-9.993 4.483-9.993 9.993 0 1.763.457 3.483 1.326 5.008L2 22l5.174-1.356a9.948 9.948 0 0 0 4.825 1.25c5.512 0 10.001-4.481 10.001-9.991C22.005 6.483 17.514 2 12.004 2zm5.845 14.238c-.244.688-1.22 1.347-1.684 1.419-.464.073-.916.297-2.955-.515-2.603-1.036-4.24-3.702-4.368-3.874-.131-.171-1.047-1.393-1.047-2.656 0-1.263.64-1.884.869-2.128.232-.244.5-.306.668-.306.168 0 .334.003.481.01.147.007.346-.056.543.422.203.49.696 1.696.757 1.821.06.125.094.272.012.434-.081.162-.122.262-.244.406-.122.144-.256.322-.366.431-.122.122-.25.253-.109.497.141.244.628 1.034 1.347 1.675.925.825 1.703 1.081 1.947 1.203.244.122.388.103.481-.003.094-.106.406-.475.516-.638.112-.162.222-.134.375-.078.153.056.969.456 1.134.54.166.081.275.122.316.191.04.07.04.403-.203 1.091z"/></svg>
  </div>
  <div class="hh-concierge-text">
    <span class="hh-concierge-label">Atelier Concierge</span>
    <span class="hh-concierge-title">WhatsApp Abdul Hakim</span>
  </div>
</a>
'''

def transform_html(html, page_path):
    # 1. Glassmorphism CSS in head
    if 'glassmorphism.css' not in html:
        html = html.replace('</head>', '<link rel="stylesheet" href="/glassmorphism.css">\n</head>')

    # 2. Fix body preloader classes
    html = re.sub(r'class="([^"]*?)site-preloader--active([^"]*?)"', r'class="\1site-loaded\2"', html)

    # 3. Replace Titles and branding
    html = re.sub(r'<title>(.*?)&#8211;\s*almoststone\.com</title>', r'<title>\1&#8211; HUDA HOMES</title>', html, flags=re.IGNORECASE)
    html = re.sub(r'<title>(.*?)almoststone\.com</title>', r'<title>\1HUDA HOMES</title>', html, flags=re.IGNORECASE)
    html = html.replace('Almost Stone', 'HUDA HOMES')
    html = html.replace('almost stone', 'HUDA HOMES')
    html = html.replace('almoststone.com', 'hudahomes.in')

    # 4. Replace logos with huda-homes-logo-white.png
    # Replace src on custom-logo and rey-mobileLogo
    html = re.sub(r'src="[^"]*logo[^"]*almost[^"]*"', 'src="/huda-homes-logo-white.png"', html, flags=re.IGNORECASE)
    html = re.sub(r'srcset="[^"]*logo[^"]*almost[^"]*"', '', html, flags=re.IGNORECASE)

    # In header: add VIP Concierge button and badge if not present
    if 'hh-header-vip-btn' not in html:
        # Find elementor-widget-reycore-header-logo or rey-siteLogo
        logo_match = re.search(r'(<div class="rey-logoWrapper">.*?</div>\s*</div>)', html, re.DOTALL)
        if logo_match:
            replacement = logo_match.group(1) + HEADER_INJECTIONS
            html = html.replace(logo_match.group(1), replacement, 1)

    # 5. Inject floating concierge button before </body>
    if 'hh-floating-concierge' not in html:
        html = html.replace('</body>', FLOATING_CONCIERGE + '\n</body>')

    # 6. Normalize all links to local paths
    html = html.replace('https://almoststone.com/product/', '/product/')
    html = html.replace('https://almoststone.com/product-category/', '/product-category/')
    html = html.replace('https://almoststone.com/catalogues/', '/catalogues/')
    html = html.replace('https://almoststone.com/our-story/', '/our-story/')
    html = html.replace('https://almoststone.com/contact-us/', '/contact-us/')
    html = html.replace('https://almoststone.com/shop/', '/shop/')
    html = html.replace('https://almoststone.com/cart/', '/cart/')
    html = html.replace('https://almoststone.com/my-account/', '/my-account/')
    html = html.replace('https://almoststone.com/', '/')

    # Ensure all product / category / page links have index.html appended if relative
    # e.g., href="/product/infinity-loop/" -> href="/product/infinity-loop/index.html"
    def fix_href(m):
        path = m.group(1)
        if path.endswith('/'):
            return f'href="{path}index.html"'
        return f'href="{path}/index.html"'

    html = re.sub(r'href="(/product/[a-zA-Z0-9_\-\%]+/?)"', fix_href, html)
    html = re.sub(r'href="(/product-category/[a-zA-Z0-9_\-\%]+/?)"', fix_href, html)
    for pg in ['catalogues', 'our-story', 'contact-us', 'shop', 'cart', 'my-account']:
        html = re.sub(rf'href="/{pg}/?"', f'href="/{pg}/index.html"', html)

    # 7. Update footer contact info
    html = re.sub(r'(\+91\s*80586\s*94217|Owner:[^<]+)', 'Owner: <strong>ABDUL HAKIM</strong> | WhatsApp: <strong>+91 80586 94217</strong>', html)

    return html

def download_and_save(rel_url):
    full_url = f"https://almoststone.com/{rel_url}/"
    target_dir = os.path.join(rel_url)
    target_file = os.path.join(target_dir, "index.html")

    try:
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            data = resp.read().decode('utf-8', errors='ignore')

        transformed = transform_html(data, rel_url)
        os.makedirs(target_dir, exist_ok=True)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(transformed)
        print(f"✓ Saved {target_file} ({len(transformed)} bytes)")
        return True
    except Exception as e:
        print(f"✗ Failed {rel_url}: {e}")
        return False

# Execute concurrent downloads
print("Starting download and transformation of all pages...")
t_start = time.time()
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(download_and_save, valid_urls))

success_count = sum(1 for r in results if r)
print(f"\nDone in {time.time() - t_start:.2f}s! Successfully transformed {success_count}/{len(valid_urls)} pages.")

# Also update index.html to point to local subpages
print("\nUpdating index.html with local links...")
with open('index.html', 'r', encoding='utf-8') as f:
    home = f.read()

home = home.replace('https://almoststone.com/product/', '/product/')
home = home.replace('https://almoststone.com/product-category/', '/product-category/')
home = home.replace('https://almoststone.com/catalogues/', '/catalogues/')
home = home.replace('https://almoststone.com/our-story/', '/our-story/')
home = home.replace('https://almoststone.com/contact-us/', '/contact-us/')
home = home.replace('https://almoststone.com/shop/', '/shop/')
home = home.replace('https://almoststone.com/cart/', '/cart/')
home = home.replace('https://almoststone.com/my-account/', '/my-account/')
home = home.replace('https://almoststone.com/', '/')

def fix_home_href(m):
    path = m.group(1)
    if path.endswith('/'):
        return f'href="{path}index.html"'
    return f'href="{path}/index.html"'

home = re.sub(r'href="(/product/[a-zA-Z0-9_\-\%]+/?)"', fix_home_href, home)
home = re.sub(r'href="(/product-category/[a-zA-Z0-9_\-\%]+/?)"', fix_home_href, home)
for pg in ['catalogues', 'our-story', 'contact-us', 'shop', 'cart', 'my-account']:
    home = re.sub(rf'href="/{pg}/?"', f'href="/{pg}/index.html"', home)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(home)

print("✓ index.html successfully updated with local page links!")

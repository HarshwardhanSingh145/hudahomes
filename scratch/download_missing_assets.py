import os
import re
import glob
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_missing_assets():
    urls = set()
    for html_path in glob.glob('./**/*.html', recursive=True):
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                c = f.read()
            matches = re.findall(r'https?://(?:almoststone\.com|hudahomes\.in)/(wp-(?:content|includes)/[^\s\"\'\)\>]+)', c)
            for m in matches:
                clean = m.split('?')[0].split('#')[0]
                urls.add(clean)
        except Exception:
            pass

    missing = []
    for u in urls:
        if not os.path.exists(u):
            missing.append(u)
    return missing

def download_asset(rel_path):
    url = f"https://almoststone.com/{rel_path}"
    target_path = os.path.join(os.getcwd(), rel_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as response, open(target_path, 'wb') as out_file:
            out_file.write(response.read())
        return (True, rel_path)
    except Exception as e:
        return (False, f"{rel_path}: {e}")

def main():
    missing = get_missing_assets()
    print(f"Total missing assets to download: {len(missing)}")
    
    success = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(download_asset, path): path for path in missing}
        for future in as_completed(futures):
            ok, msg = future.result()
            if ok:
                success += 1
            else:
                failed += 1
            if (success + failed) % 100 == 0 or (success + failed) == len(missing):
                print(f"Progress: {success + failed}/{len(missing)} (Success: {success}, Failed: {failed})")

    print(f"Done! Downloaded: {success}, Failed: {failed}")

if __name__ == '__main__':
    main()

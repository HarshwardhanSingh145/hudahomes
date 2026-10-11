import os
import glob
import re

def process_html_files():
    html_files = glob.glob('./**/*.html', recursive=True)
    print(f"Found {len(html_files)} HTML files to process.")
    
    count_modified = 0
    
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            orig = content
            
            # 1. URL Path Normalization
            # Content and Includes
            content = content.replace("https://hudahomes.in/wp-content/", "/wp-content/")
            content = content.replace("https://almoststone.com/wp-content/", "/wp-content/")
            content = content.replace("http://almoststone.com/wp-content/", "/wp-content/")
            content = content.replace("https://hudahomes.in/wp-includes/", "/wp-includes/")
            content = content.replace("https://almoststone.com/wp-includes/", "/wp-includes/")
            content = content.replace("http://almoststone.com/wp-includes/", "/wp-includes/")
            
            # Products & Categories
            content = content.replace("https://hudahomes.in/product/", "/product/")
            content = content.replace("https://almoststone.com/product/", "/product/")
            content = content.replace("http://almoststone.com/product/", "/product/")
            content = content.replace("https://hudahomes.in/product-category/", "/product-category/")
            content = content.replace("https://almoststone.com/product-category/", "/product-category/")
            content = content.replace("http://almoststone.com/product-category/", "/product-category/")
            
            # Pages
            for page in ['shop', 'our-story', 'contact-us', 'catalogues', 'cart', 'my-account', 'checkout']:
                content = content.replace(f"https://hudahomes.in/{page}/", f"/{page}/")
                content = content.replace(f"https://almoststone.com/{page}/", f"/{page}/")
                content = content.replace(f"http://almoststone.com/{page}/", f"/{page}/")

            # Domain root
            content = content.replace('href="https://hudahomes.in/"', 'href="/"')
            content = content.replace('href="https://almoststone.com/"', 'href="/"')
            content = content.replace('href="http://almoststone.com/"', 'href="/"')
            content = content.replace('https://hudahomes.in/', '/')
            content = content.replace('https://almoststone.com/', '/')
            content = content.replace('http://almoststone.com/', '/')
            
            # 2. Text Branding Replacements
            content = re.sub(r'Almost\s*Stone', 'HUDA HOMES', content, flags=re.IGNORECASE)
            content = re.sub(r'almoststone\.com', 'hudahomes.in', content, flags=re.IGNORECASE)
            content = re.sub(r'almoststone', 'hudahomes', content, flags=re.IGNORECASE)

            # 3. Ensure glassmorphism.css link is in head
            if 'glassmorphism.css' not in content and '</head>' in content:
                content = content.replace('</head>', '<link rel="stylesheet" href="/glassmorphism.css">\n</head>')

            if content != orig:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count_modified += 1
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    print(f"Successfully processed {len(html_files)} files. Modified: {count_modified} files.")

if __name__ == '__main__':
    process_html_files()

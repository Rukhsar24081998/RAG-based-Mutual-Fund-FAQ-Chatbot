import csv
import os
import requests
import shutil
from urllib.parse import urlparse, unquote

SOURCES_CSV = "sources.csv"
RAW_DIR = "data/raw"

def sanitize_filename(url):
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = "unknown"
    filename = filename.replace("%20", "_")
    return filename

def download_file(url, save_path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def copy_local_file(url, save_path):
    try:
        parsed = urlparse(url)
        local_path = unquote(parsed.path)
        if os.path.exists(local_path):
            shutil.copy(local_path, save_path)
            return True
        else:
            print(f"Local file not found: {local_path}")
            return False
    except Exception as e:
        print(f"Failed to copy local file {url}: {e}")
        return False

def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    with open(SOURCES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url', '').strip()
            source_type = row.get('type', '').strip()
            
            if not url:
                continue
            
            # Determine file extension
            if url.lower().endswith('.pdf'):
                ext = '.pdf'
            elif url.lower().endswith('.txt'):
                ext = '.txt'
            else:
                ext = '.html'
            
            filename = sanitize_filename(url)
            if not filename.endswith(ext):
                filename += ext
            
            save_path = os.path.join(RAW_DIR, filename)
            
            if os.path.exists(save_path):
                print(f"Skipping {filename} - already exists")
                skipped += 1
                continue
            
            # Handle file:// URLs
            if url.startswith('file://'):
                print(f"Copying {filename}...")
                if copy_local_file(url, save_path):
                    downloaded += 1
                else:
                    failed += 1
            else:
                print(f"Downloading {filename}...")
                if download_file(url, save_path):
                    downloaded += 1
                else:
                    failed += 1
    
    print(f"\nDone! Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}")

if __name__ == "__main__":
    main()

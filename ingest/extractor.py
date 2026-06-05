import csv
import os
from pypdf import PdfReader
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"
EXTRACTED_DIR = "data/extracted"
SOURCES_CSV = "sources.csv"

def get_metadata(filename):
    with open(SOURCES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url', '')
            if filename in url or url.replace('%20', '_').endswith(filename):
                return {
                    'source': row.get('source', ''),
                    'type': row.get('type', ''),
                    'scheme': row.get('scheme', ''),
                    'url': url,
                    'doc_date': row.get('doc_date', '')
                }
    return {}

def extract_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF {file_path}: {e}")
    return text

def extract_html(file_path):
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            text = soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"Error extracting HTML {file_path}: {e}")
    return text

def extract_txt(file_path):
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error extracting TXT {file_path}: {e}")
    return text

def main():
    os.makedirs(EXTRACTED_DIR, exist_ok=True)
    
    processed = 0
    
    for filename in os.listdir(RAW_DIR):
        file_path = os.path.join(RAW_DIR, filename)
        if not os.path.isfile(file_path):
            continue
        
        print(f"Processing {filename}...")
        
        if filename.lower().endswith('.pdf'):
            text = extract_pdf(file_path)
        elif filename.lower().endswith('.html'):
            text = extract_html(file_path)
        elif filename.lower().endswith('.txt'):
            text = extract_txt(file_path)
        else:
            continue
        
        metadata = get_metadata(filename)
        
        output_filename = os.path.splitext(filename)[0] + '.txt'
        output_path = os.path.join(EXTRACTED_DIR, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"SOURCE: {metadata.get('source', '')}\n")
            f.write(f"TYPE: {metadata.get('type', '')}\n")
            f.write(f"SCHEME: {metadata.get('scheme', '')}\n")
            f.write(f"URL: {metadata.get('url', '')}\n")
            f.write(f"DOC_DATE: {metadata.get('doc_date', '')}\n")
            f.write("="*80 + "\n")
            f.write(text)
        
        processed += 1
    
    print(f"\nDone! Processed {processed} files")

if __name__ == "__main__":
    main()

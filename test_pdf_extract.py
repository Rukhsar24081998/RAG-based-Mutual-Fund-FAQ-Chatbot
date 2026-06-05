import pypdf

pdf_path = "data/raw/Fund_Facts_-HDFC_Defence_Fund_May_26.pdf"

with open(pdf_path, "rb") as f:
    reader = pypdf.PdfReader(f)
    for page_num, page in enumerate(reader.pages):
        print(f"\n--- Page {page_num + 1} ---")
        print(page.extract_text())
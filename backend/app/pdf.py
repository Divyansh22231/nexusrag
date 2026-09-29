import fitz
import re
from typing import List, Dict

def extract_text_from_pdf(pdf_bytes: bytes) -> List[Dict]:
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            # Fix glued numbers from tabular extraction (e.g. 552.00429.00 -> 552.00 429.00)
            text = re.sub(r'(\.\d{2})([0-9\-])', r'\1 \2', text)
            
            if text.strip():
                pages.append({
                    "page": page_num + 1,
                    "text": text.strip()
                })
    finally:
        doc.close()
    return pages

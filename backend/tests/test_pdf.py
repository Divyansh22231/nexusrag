from app.pdf import extract_text_from_pdf
import fitz

def test_extract_text_from_pdf(tmp_path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World PDF")
    
    pdf_path = tmp_path / "test.pdf"
    doc.save(pdf_path)
    
    with open(pdf_path, "rb") as f:
        content = f.read()
        
    pages = extract_text_from_pdf(content)
    assert len(pages) == 1
    assert "Hello World PDF" in pages[0]["text"]
    assert pages[0]["page"] == 1

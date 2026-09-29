from typing import List, Dict

def chunk_document(document_id: str, filename: str, pages: List[Dict], chunk_size: int = 4000, overlap: int = 400) -> List[Dict]:
    chunks = []
    for page_data in pages:
        text = page_data["text"]
        page_num = page_data["page"]
        
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            
            if end < len(text):
                last_space = chunk_text.rfind(" ")
                if last_space > 0:
                    end = start + last_space
                    chunk_text = text[start:end]
                    
            chunks.append({
                "document_id": document_id,
                "chunk_id": f"{document_id}_p{page_num}_{start}",
                "filename": filename,
                "page": page_num,
                "text": f"Document: {filename}\nPage: {page_num}\n{chunk_text.strip()}"
            })
            start = end - overlap
            if start < 0:
                start = 0
            if end == len(text):
                break
    return chunks

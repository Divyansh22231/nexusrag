import re
from typing import List, Dict

Q_PATTERN = re.compile(r"(?im)^\s*(?:q|question)\s*(?:no\.?\s*)?0*(\d+)(?:[\s:.-]|$)")

def normalize_q_id(q_str: str) -> str:
    match = re.search(r"(?i)^(?:q|question)\s*(?:no\.?\s*)?0*(\d+)", q_str.strip())
    if match:
        return f"Q{int(match.group(1)):02d}"
    return ""

def chunk_document(document_id: str, filename: str, pages: List[Dict], chunk_size: int = 4000, overlap: int = 400) -> List[Dict]:
    chunks = []
    current_q_id = None
    
    for page_data in pages:
        text = page_data["text"]
        page_num = page_data["page"]
        
        matches = list(Q_PATTERN.finditer(text))
        
        if not matches:
            sections = [(current_q_id, text)]
        else:
            sections = []
            if matches[0].start() > 0:
                sections.append((current_q_id, text[:matches[0].start()]))
            
            for i, match in enumerate(matches):
                q_num = int(match.group(1))
                current_q_id = f"Q{q_num:02d}"
                start_idx = match.start()
                end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
                sections.append((current_q_id, text[start_idx:end_idx]))
                
        for q_id, sec_text in sections:
            sec_text = sec_text.strip()
            if not sec_text:
                continue
                
            start = 0
            while start < len(sec_text):
                end = min(start + chunk_size, len(sec_text))
                chunk_text = sec_text[start:end]
                
                if end < len(sec_text):
                    last_space = chunk_text.rfind(" ")
                    if last_space > 0:
                        end = start + last_space
                        chunk_text = sec_text[start:end]
                        
                metadata = {
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_num,
                    "document": filename,
                    "chunk_type": "qa" if q_id else "text"
                }
                if q_id:
                    metadata["question_id"] = q_id
                    
                chunks.append({
                    "document_id": document_id,
                    "chunk_id": f"{document_id}_p{page_num}_{len(chunks)}",
                    "filename": filename,
                    "page": page_num,
                    "text": f"Document: {filename}\nPage: {page_num}\n{chunk_text.strip()}",
                    "metadata": metadata
                })
                
                start = end - overlap
                if start < 0:
                    start = 0
                if end == len(sec_text):
                    break
                    
    return chunks

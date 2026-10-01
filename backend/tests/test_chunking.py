from app.chunking import chunk_document

from app.chunking import chunk_document

def test_chunk_document_basic():
    pages = [{"page": 1, "text": "A" * 1200}]
    chunks = chunk_document("doc1", "test.pdf", pages, chunk_size=1000, overlap=200)
    
    assert len(chunks) > 1
    assert chunks[0]["document_id"] == "doc1"
    assert chunks[0]["page"] == 1
    assert "Document: test.pdf" in chunks[0]["text"]
    assert len(chunks[0]["text"]) > 1000

def test_chunk_document_q_sections():
    text = "Q01\nWhat is SQL?\nIt is a DB language.\nQ2: What is JOIN?\nIt joins tables."
    pages = [{"page": 1, "text": text}]
    chunks = chunk_document("doc2", "qa.pdf", pages, chunk_size=1000, overlap=0)
    
    assert len(chunks) == 2
    assert chunks[0]["metadata"]["question_id"] == "Q01"
    assert chunks[1]["metadata"]["question_id"] == "Q02"
    assert chunks[0]["metadata"]["chunk_type"] == "qa"
    assert chunks[1]["metadata"]["chunk_type"] == "qa"


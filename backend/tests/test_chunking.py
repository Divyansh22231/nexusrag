from app.chunking import chunk_document

def test_chunk_document():
    pages = [{"page": 1, "text": "A" * 1200}]
    chunks = chunk_document("doc1", "test.pdf", pages, chunk_size=1000, overlap=200)
    
    assert len(chunks) > 1
    assert chunks[0]["document_id"] == "doc1"
    assert chunks[0]["page"] == 1
    assert "Document: test.pdf" in chunks[0]["text"]
    assert len(chunks[0]["text"]) > 1000

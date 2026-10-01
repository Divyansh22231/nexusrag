from app.retrieval import retrieve_context
from app.chunking import normalize_q_id
from unittest.mock import patch, MagicMock

# 1. "q1" normalizes to Q01.
# 2. "Q1" normalizes to Q01.
# 3. "question 1" normalizes to Q01.
def test_normalize_q_id():
    assert normalize_q_id("q1") == "Q01"
    assert normalize_q_id("Q1") == "Q01"
    assert normalize_q_id("question 1") == "Q01"
    assert normalize_q_id("Q01") == "Q01"
    assert normalize_q_id("Question 01") == "Q01"
    assert normalize_q_id("question no 1") == "Q01"
    assert normalize_q_id("Q17") == "Q17"
    assert normalize_q_id("What is SQL?") == ""
    assert normalize_q_id("How do joins work?") == ""

# 4. Exact Q01 retrieval works when a document contains Q01.
@patch("app.retrieval.search")
def test_exact_q01_retrieval(mock_search):
    mock_search.side_effect = lambda query, k, where=None, where_document=None: [
        {"chunk_id": "c1", "text": "Q01: Logical query execution order...", "metadata": {"question_id": "Q01"}, "distance": 0.0}
    ] if where == {"question_id": "Q01"} else []

    candidates = retrieve_context("Q1")
    assert len(candidates) == 1
    assert candidates[0]["metadata"]["question_id"] == "Q01"
    assert candidates[0]["score"] == 1.0
    mock_search.assert_called_with("Q1", k=8, where={"question_id": "Q01"})

# 5. Exact Q17 retrieval works when a document contains Q17.
@patch("app.retrieval.search")
def test_exact_q17_retrieval(mock_search):
    mock_search.side_effect = lambda query, k, where=None, where_document=None: [
        {"chunk_id": "c17", "text": "Q17: Indexing in databases...", "metadata": {"question_id": "Q17"}, "distance": 0.0}
    ] if where == {"question_id": "Q17"} else []

    candidates = retrieve_context("Q17")
    assert len(candidates) == 1
    assert candidates[0]["metadata"]["question_id"] == "Q17"
    assert candidates[0]["score"] == 1.0
    mock_search.assert_called_with("Q17", k=8, where={"question_id": "Q17"})

# 6. Normal semantic questions still use the existing semantic retrieval path.
@patch("app.retrieval.search")
def test_normal_semantic_retrieval_path(mock_search):
    mock_search.side_effect = lambda query, k, where=None, where_document=None: [
        {"chunk_id": "c_sem", "text": "MySQL order of execution is FROM, WHERE, GROUP BY...", "distance": 0.15, "metadata": {}}
    ] if where is None and where_document is None else []

    candidates = retrieve_context("What is the logical query execution order in MySQL?")
    assert len(candidates) == 1
    assert candidates[0]["chunk_id"] == "c_sem"
    assert candidates[0]["score"] == 0.85
    mock_search.assert_called_once_with("What is the logical query execution order in MySQL?", k=8)

# 7. If exact Q-ID does not exist, retrieval falls back normally.
@patch("app.retrieval.search")
def test_qid_not_found_falls_back_to_semantic(mock_search):
    def side_effect(query, k, where=None, where_document=None):
        if where:
            return []  # Exact Q-ID not in document
        if not where_document:
            return [{"chunk_id": "c_sem_fb", "text": "Semantic context fallback", "distance": 0.2, "metadata": {}}]
        return []

    mock_search.side_effect = side_effect

    candidates = retrieve_context("Q99")
    assert len(candidates) == 1
    assert candidates[0]["chunk_id"] == "c_sem_fb"
    assert candidates[0]["score"] == 0.8

# 8. If semantic retrieval is insufficient, the fallback path is attempted.
@patch("app.retrieval.search")
def test_semantic_insufficient_keyword_fallback(mock_search):
    def side_effect(query, k, where=None, where_document=None):
        if where:
            return []
        if not where_document:
            # Low similarity: distance 0.85 -> similarity 0.15 < threshold 0.35
            return [{"chunk_id": "c_poor", "text": "Poor match", "distance": 0.85, "metadata": {}}]
        if where_document:
            return [{"chunk_id": "c_kw", "text": "Fallback keyword match", "distance": 0.5, "metadata": {}}]
        return []

    mock_search.side_effect = side_effect

    candidates = retrieve_context("Explain normalization rules")
    assert len(candidates) == 1
    assert candidates[0]["chunk_id"] == "c_kw"
    assert candidates[0]["score"] == 0.5

# 9. Existing grounded refusal behavior remains intact when all retrieval fails.
@patch("app.retrieval.search")
def test_all_retrieval_fail_returns_empty(mock_search):
    mock_search.return_value = []
    candidates = retrieve_context("Completely unrelated query that matches nothing")
    assert candidates == []


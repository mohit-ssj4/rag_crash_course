from src.embedding_manager import EmbeddingManager
from src.rag_retriever import RAGRetriever
from src.vector_store import VectorStore


def test_rag_retriever_initialization(monkeypatch):
    # Mock SentenceTransformer and chromadb initialization to test class mapping offline
    monkeypatch.setattr(
        "src.embedding_manager.SentenceTransformer", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "src.vector_store.chromadb.PersistentClient", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "src.vector_store.VectorStore._initialize_store", lambda *args, **kwargs: None
    )

    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()

    retriever = RAGRetriever(vector_store, embedding_manager)
    assert retriever.vector_store is vector_store
    assert retriever.embedding_manager is embedding_manager


def test_rag_retriever_empty_query(monkeypatch):
    # Mock dependencies
    monkeypatch.setattr(
        "src.embedding_manager.SentenceTransformer", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "src.vector_store.VectorStore._initialize_store", lambda *args, **kwargs: None
    )

    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()
    retriever = RAGRetriever(vector_store, embedding_manager)

    response = retriever.generate_response("")
    assert response["answer"] == "I don't know based on the available documents."
    assert response["confidence"] == "0.00%"
    assert response["sources"] == []

import json

from data_chunker import DataChunker
from data_loader import DataLoader
from embedding_manager import EmbeddingManager
from rag_retriever import RAGRetiever
from vector_store import VectorStore


def run_pipeline() -> None:
    # Step 1: Loading the txt files and converting them into Langchain documents
    data_loader = DataLoader()
    documents = data_loader.load_data()

    # Step 2: Chunking the data for embedding it into Vector DB
    data_chunker = DataChunker()
    chunks = data_chunker.chunk_data(documents)

    # Step 3: Embedding the data to convert the chunks into vectors
    embedding_manager = EmbeddingManager()
    texts = [doc.page_content for doc in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)

    # Step 4: Adding generated emeddings in the Vector store
    vector_store = VectorStore()
    vector_store.add_documents(chunks, embeddings)

    # Step 5: Retieve data from RAG
    retriever = RAGRetiever(vector_store, embedding_manager)

    while True:
        query = input("\nEnter your query: ").strip()

        if query in ["quit", "exit"]:
            break

        result = retriever.generate_response(query)
        print(f"\n\nLLM Response: {json.dumps(result, indent=4, ensure_ascii=False)}")


if __name__ == "__main__":
    run_pipeline()

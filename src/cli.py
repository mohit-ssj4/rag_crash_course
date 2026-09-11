import argparse
import sys

from src.logger import get_logger

logger = get_logger("cli")


def handle_ingest() -> None:
    """Handles offline document loading, chunking, embedding, and indexing."""
    logger.info("Starting offline data ingestion...")
    from src.data_chunker import DataChunker
    from src.data_loader import DataLoader
    from src.embedding_manager import EmbeddingManager
    from src.vector_store import VectorStore

    # Load documents
    loader = DataLoader()
    documents = loader.load_data()
    if not documents:
        logger.warning("No source documents found to ingest.")
        return

    # Chunk documents
    chunker = DataChunker()
    chunks = chunker.chunk_data(documents)
    if not chunks:
        logger.warning("No text chunks generated.")
        return

    # Generate embeddings
    manager = EmbeddingManager()
    texts = [doc.page_content for doc in chunks]
    embeddings = manager.generate_embeddings(texts)

    # Persist to vector database
    store = VectorStore()
    store.add_documents(chunks, embeddings)
    logger.info("Offline data ingestion completed successfully.")


def handle_query(query_text: str) -> None:
    """Handles executing a single RAG-based query against pre-computed index."""
    if not query_text or not query_text.strip():
        logger.warning("Empty query received.")
        return

    from src.embedding_manager import EmbeddingManager
    from src.rag_retriever import RAGRetriever
    from src.vector_store import VectorStore

    store = VectorStore()
    # Story 2.6: Verification check for empty/missing collection
    if store.collection is None or store.collection.count() == 0:
        logger.warning(
            "Database empty. Please run ingestion first via `python src/cli.py ingest`."
        )
        return

    manager = EmbeddingManager()
    retriever = RAGRetriever(store, manager)

    result = retriever.generate_response(query_text)
    print(f"\nLLM Response:\n{result.get('answer', result)}\n")


def handle_interactive() -> None:
    """Drops the user into a multi-turn interactive command loop with warm DB connections."""
    from src.embedding_manager import EmbeddingManager
    from src.rag_retriever import RAGRetriever
    from src.vector_store import VectorStore

    store = VectorStore()
    # Story 2.6: Verification check for empty/missing collection
    if store.collection is None or store.collection.count() == 0:
        logger.warning(
            "Database empty. Please run ingestion first via `python src/cli.py ingest`."
        )
        return

    manager = EmbeddingManager()
    retriever = RAGRetriever(store, manager)

    print("\n" + "=" * 50)
    print("      AURORA DYNAMICS INTERACTIVE RAG CLIENT")
    print("   Type 'exit' or 'quit' to terminate session.")
    print("=" * 50 + "\n")

    while True:
        try:
            query = input("Aurora-RAG > ").strip()
            if query.lower() in ["exit", "quit"]:
                logger.info("Terminating interactive session.")
                break
            if not query:
                continue

            result = retriever.generate_response(query)
            print(f"\nLLM Response:\n{result.get('answer', result)}\n")
        except (KeyboardInterrupt, EOFError):
            print()
            logger.info("Interactive session interrupted.")
            break


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Project Aurora - Production-Grade Decoupled RAG Command-Line Interface"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Ingest subcommand
    subparsers.add_parser(
        "ingest",
        help="Load, chunk, embed, and index text documents from data/ into ChromaDB",
    )

    # Query subcommand
    query_parser = subparsers.add_parser(
        "query", help="Execute a single semantic search and text generation sequence"
    )
    query_parser.add_argument("text", type=str, help="The search query text")

    # Interactive subcommand
    subparsers.add_parser(
        "interactive",
        help="Start an interactive multi-turn chat session using pre-computed index",
    )

    args = parser.parse_args()

    if args.command == "ingest":
        handle_ingest()
    elif args.command == "query":
        handle_query(args.text)
    elif args.command == "interactive":
        handle_interactive()
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()

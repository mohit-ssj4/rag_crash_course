from typing import Any
from src.embedding_manager import EmbeddingManager
from src.llm_client import groq_client, model_name
from src.vector_store import VectorStore
from src.logger import get_logger

logger = get_logger("rag_retriever")


class RAGRetriever:
    """
    Handles query-based retrieval from the vector store

    Args:
        vector_store: Vector store containing document embeddings
        embedding_manager: Manager for generating query embeddings
    """

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager) -> None:
        """
        Initialize the retriever

        Args:
            vector_store: Vector store containing document embeddings
            embedding_manager: Manager for generating query embeddings
        """
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def _retrieve(
        self, query: str, top_k: int = 5, score_threshold: float = 0.0
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant documents for a query

        Args:
            query: The search query
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold

        Returns:
            List of dictionaries containing retrieved documents and metadata
        """
        logger.info(f"Retrieving documents for query: '{query}'")
        logger.info(f"Top K: {top_k}, Score threshold: {score_threshold}")

        # Validate query
        if not query or not query.strip():
            logger.info("Empty query received. Returning no documents.")
            return []

        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        # Search in vector store
        if self.vector_store.collection is None:
            raise ValueError("No vector store collection loaded")

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding.tolist()], n_results=top_k
        )

        # Process results
        retrieved_docs: list[dict[str, Any]] = []

        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            ids = results["ids"][0]

            for i, (doc_id, document, metadata, distance) in enumerate(
                zip(ids, documents, metadatas, distances)
            ):
                # Convert distance to similarity score (ChromaDB uses cosine distance)
                similarity_score = 1 - distance

                if similarity_score >= score_threshold:
                    retrieved_docs.append(
                        {
                            "id": doc_id,
                            "content": document,
                            "metadata": metadata or {},
                            "similarity_score": similarity_score,
                            "distance": distance,
                            "rank": i + 1,
                        }
                    )

            logger.info(f"Retrieved {len(retrieved_docs)} documents (after filtering)")
        else:
            logger.info("No documents found")

        return retrieved_docs

    def generate_response(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
        show_sources: bool = True,
    ) -> dict[str, Any]:
        """
        Generate synthesized response for a query utilizing RAG and Groq

        Args:
            query: The user query.
            top_k: Number of semantic search results.
            min_score: Similarity score threshold.
            show_sources: Whether to return source documents in output.

        Returns:
            A dictionary with answer/sources, and confidence.
        """
        default_response = {
            "answer": "I don't know based on the available documents.",
            "sources": [],
            "confidence": "0.00%",
        }

        if not query or not query.strip():
            return default_response

        rag_results = self._retrieve(query, top_k=top_k, score_threshold=min_score)
        if not rag_results:
            return default_response

        # Prepare context and sources
        context = "\n\n".join([doc["content"] for doc in rag_results])
        sources = [
            {
                "source": (doc["metadata"] or {}).get(
                    "source_file", (doc["metadata"] or {}).get("source", "unknown")
                ),
                "score": doc["similarity_score"],
            }
            for doc in rag_results
        ]
        
        # Protect confidence score boundary constraints (0.0 to 100.0)
        raw_confidence = max([doc["similarity_score"] for doc in rag_results]) * 100
        confidence = max(0.0, min(100.0, raw_confidence))

        system_prompt = """You answer questions about Aurora Dynamics using ONLY the
provided context. Rules:
- If the context does not contain the answer, reply exactly:
  "I don't know based on the available documents."
- Never use outside knowledge and never guess.
- Mention the source file(s) your answer came from if it is present in the context"""
        prompt = f"""Use the following context to answer the question concisely.
Context:
{context}

Question: {query}"""

        response = groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        answer = response.choices[0].message.content or ""
        if not answer.strip():
            return default_response

        output: dict[str, Any] = {
            "answer": answer.strip(), 
            "confidence": f"{confidence:.2f}%"
        }

        if show_sources:
            output["sources"] = sources
        else:
            output["sources"] = []

        return output

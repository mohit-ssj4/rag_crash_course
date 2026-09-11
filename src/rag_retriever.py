from typing import Any

from embedding_manager import EmbeddingManager
from llm_client import groq_client, model_name
from vector_store import VectorStore


class RAGRetiever:
    """
    Handles query-based retrieval from the vector store

    Args:
        vector_store: Vector store containing document embeddings
        embedding_manager: Manager for generating query embeddings
    """

    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
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
        print(f"[INFO] Retrieving documents for query: '{query}'")
        print(f"[INFO] Top K: {top_k}, Score threshold: {score_threshold}")

        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        # Search in vector store
        if self.vector_store.collection == None:
            raise ValueError("No vector store collection loaded")

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding.tolist()], n_results=top_k
        )

        # Process results
        retrieved_docs = []

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
                            "metadata": metadata,
                            "similarity_score": similarity_score,
                            "distance": distance,
                            "rank": i + 1,
                        }
                    )

            print(f"[INFO] Retrieved {len(retrieved_docs)} documents (after filtering)")
        else:
            print("[INFO] No documents found")

        return retrieved_docs

    def generate_response(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
        show_sources: bool = True,
    ):
        rag_results = self._retrieve(query, top_k=top_k, score_threshold=min_score)
        if not rag_results:
            return {
                "answer": "No relevant context found.",
                "sources": [],
                "confidence": 0.0,
            }

        # Prepare context and sources
        context = "\n\n".join([doc["content"] for doc in rag_results])
        sources = [
            {
                "source": doc["metadata"].get(
                    "source_file", doc["metadata"].get("source", "unknown")
                ),
                "score": doc["similarity_score"],
            }
            for doc in rag_results
        ]
        confidence = max([doc["similarity_score"] for doc in rag_results]) * 100

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

        answer = response.choices[0].message.content

        if not answer:
            return ""

        output = {"answer": answer, "confidence": f"{confidence:.2f}%"}

        if show_sources:
            output["sources"] = sources

        return output

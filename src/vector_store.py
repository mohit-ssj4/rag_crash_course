import os
import uuid
from typing import Any

import chromadb
import numpy as np
from langchain_core.documents import Document

from src.config import COLLECTION_NAME, PERSIST_DIRECTORY
from src.logger import get_logger

logger = get_logger("vector_store")


class VectorStore:
    """
    Manages document embeddings in a ChromaDB vector store

    Args:
        collection_name: Name of the ChromaDB collection
        persist_directory: Directory to persist the vector store
    """

    def __init__(
        self,
        collection_name: str = COLLECTION_NAME,
        persist_directory: str = PERSIST_DIRECTORY,
    ) -> None:
        """
        Initialize the vector store

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the vector store
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection: Any = None
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize ChromaDB client and collection"""
        # Create persistent ChromaDB client
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        if self.client is None:
            raise ValueError("No client found")

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Vector store initialized. Collection: {self.collection_name}")
        logger.info(f"Existing documents in collection: {self.collection.count()}")

    def add_documents(self, documents: list[Document], embeddings: np.ndarray) -> None:
        """
        Add documents and their embeddings to the vector store

        Args:
            documents: List of LangChain documents
            embeddings: Corresponding embeddings for the documents
        """

        logger.info(f"Adding {len(documents)} documents to vector store")

        # Prepare data for ChromaDB
        ids = []
        metadatas = []
        documents_text = []
        embeddings_list = []

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Generate unique ID
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)

            # Prepare metadata
            metadata = dict(doc.metadata)
            metadata["doc_index"] = i
            metadata["content_length"] = len(doc.page_content)
            metadatas.append(metadata)

            # Document content
            documents_text.append(doc.page_content)

            # Embedding
            embeddings_list.append(embedding.tolist())

        # Add to collection
        try:
            if self.collection is None:
                raise ValueError("No collection found")

            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text,
            )
            logger.info(
                f"Successfully added {len(documents)} documents to vector store"
            )
            logger.info(f"Total documents in collection: {self.collection.count()}")

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

import numpy as np
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    """
    Handles document embedding generation using SentenceTransformer

    Args:
        model_name: Model name for generating embeddings
        batch_size: Size of the batch
    """

    def __init__(
        self, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32
    ) -> None:
        """
        Initialize the embedding manager

        Args:
            model_name: Model name for generating embeddings
            batch_size: Size of the batch
        """
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        self.batch_size = batch_size

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Generates emebeddings for the given documents

        Args:
            texts: List of Langchain documents

        Returns
            Numpy array of vector embeddings
        """
        print(f"[INFO] Generating embeddings for {len(texts)} texts...")

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        print(f"[INFO] Generated embeddings with shape: {embeddings.shape}")

        return embeddings

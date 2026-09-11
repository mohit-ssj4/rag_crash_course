from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE
from src.logger import get_logger

logger = get_logger("data_chunker")


class DataChunker:
    """
    Chunks the data based on the chunk_size and chunk_overlap provided

    Args:
        chunk_size: Maximum size of each chunk.
        chunk_overlap: Number of characters shared between consecutive chunks.
    """

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_data(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into smaller chunks for embedding and retrieval.

        Args:
            documents: Documents to split and chunk.

        Returns:
            A list of chunked LangChain Document objects.
        """
        if not documents:
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        chunks = splitter.split_documents(documents)

        logger.info(
            f"Split {len(documents)} documents into {len(chunks)} chunks "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})."
        )

        return chunks

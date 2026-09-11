from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DataChunker:
    """
    Chunks the data based on the chunk_size and chunk_overlap provided

    Args:
        chunk_size: Maximum size of each chunk.
        chunk_overlap: Number of characters shared between consecutive chunks.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
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

        print(
            f"[INFO] Split {len(documents)} documents into "
            f"{len(chunks)} chunks "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})."
        )

        return chunks

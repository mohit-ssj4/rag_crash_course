from pathlib import Path

from langchain_core.documents import Document


class DataLoader:
    """
    Loads data and coverts them into LangChain Documents.
    """

    def load_data(
        self,
        path: str = "data",
        glob_pattern: str = "*.txt",
    ) -> list[Document]:
        """
        Load text files from a directory into LangChain Documents.

        Args:
            path: Directory containing the source files.
            glob_pattern: Pattern used to match files.

        Returns:
            A list of LangChain Document objects.
        """
        data_path = Path(path)

        documents: list[Document] = []

        for file_path in sorted(data_path.rglob(glob_pattern)):
            content = file_path.read_text(encoding="utf-8")

            if not content.strip():
                continue

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "file_name": file_path.name,
                        "file_type": file_path.suffix,
                    },
                )
            )

        print(f"[INFO] Loaded {len(documents)} files successfully")

        return documents

from pathlib import Path
from app.core.config import BASE_DIR

from app.utils.hash_utils import file_hash
from app.utils.ingestion_registry import IngestionRegistry
from app.utils.document_metadata import extract_article_number, load_file_metadata

from app.core.dependencies import parser, chunker, vectorstore

class IngestionPipeline:

    def __init__(self):
        self.parser = parser
        self.chunker = chunker
        self.vectorstore = vectorstore

        self.registry = IngestionRegistry()

    def ingest(
        self,
        file_path: Path
    ) -> bool:

        document_hash = file_hash(
            file_path
        )

        if self.registry.is_ingested(
            document_hash
        ):
            print(
                f"[SKIP] {file_path.name}"
            )
            return False

        try:
            documents = self.parser.parse(
                file_path
            )
        except Exception as exc:
            print(
                f"[FAIL] {file_path.name}: {exc}"
            )
            return False

        file_metadata = load_file_metadata(file_path)
        for document in documents:
            document.metadata.update(file_metadata)

        chunks = self.chunker.split(
            documents
        )

        for chunk in chunks:
            article = extract_article_number(chunk.page_content)
            if article:
                chunk.metadata["article"] = article

        self.vectorstore.add_documents(
            chunks
        )

        self.registry.mark_ingested(
            document_hash,
            file_path.name
        )

        print(
            f"[OK] {file_path.name}"
        )

        return True
    
    def ingest_all(
        self,
        directory_path: Path = BASE_DIR / "data" / "raw"
    ) -> None:
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == ".pdf":
                self.ingest(
                    file_path
                )
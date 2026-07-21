from pathlib import Path
from app.core.config import BASE_DIR

from app.utils.hash_utils import file_hash
from app.utils.ingestion_registry import IngestionRegistry

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

        documents = self.parser.parse(
            file_path
        )

        chunks = self.chunker.split(
            documents
        )

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
            if file_path.is_file():
                self.ingest(
                    file_path
                )
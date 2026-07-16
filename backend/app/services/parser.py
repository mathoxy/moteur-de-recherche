from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


class DocumentParser:

    def parse(self, file_path: Path):

        loader = PyPDFLoader(str(file_path))

        return loader.load()
from langchain_chroma import Chroma
from app.core.config import PERSIST_DIRECTORY

class VectorStore:

    def __init__(
        self,
        embeddings,
        persist_directory: str = PERSIST_DIRECTORY
    ):
        self.db = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory
        )

    def add_documents(self, documents):
        self.db.add_documents(documents)

    def as_retriever(self, k):
        return self.db.as_retriever(k=k)
from langchain_chroma import Chroma


class VectorStore:

    def __init__(
        self,
        persist_directory: str,
        embeddings
    ):
        self.db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

    def add_documents(self, documents):
        self.db.add_documents(documents)

    def as_retriever(self):
        return self.db.as_retriever()
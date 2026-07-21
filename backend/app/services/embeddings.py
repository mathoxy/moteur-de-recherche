from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small"
    ):
        self.model = HuggingFaceEmbeddings(
            model_name=model_name
        )

    def get_model(self):
        return self.model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.model.embed_query(text)
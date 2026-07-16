from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3"
    ):
        self.model = HuggingFaceEmbeddings(
            model_name=model_name
        )

    def get_model(self):
        return self.model
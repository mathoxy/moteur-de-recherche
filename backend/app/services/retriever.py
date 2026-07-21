class Retriever:

    def __init__(
        self,
        vectorstore,
        k=5
    ):
        self.retriever = vectorstore.as_retriever(k)

    def retrieve(
        self,
        query: str
    ):
        return self.retriever.invoke(query)
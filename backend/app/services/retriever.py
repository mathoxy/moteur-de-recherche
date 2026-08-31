class Retriever:

    def __init__(
        self,
        vectorstore,
        k=5
    ):
        self.vectorstore = vectorstore
        self.default_k = k
        self.retriever = vectorstore.as_retriever(k)

    def retrieve(
        self,
        query: str,
        k: int | None = None
    ):
        requested_k = k or self.default_k
        candidate_k = max(requested_k * 3, requested_k, 10)

        docs = self.vectorstore.db.similarity_search(query, k=candidate_k)

        seen = set()
        unique_docs = []

        for doc in docs:
            key = (
                (doc.page_content or "").strip(),
                str(doc.metadata.get("source") or ""),
                str(doc.metadata.get("title") or ""),
                str(doc.metadata.get("document_number") or ""),
                str(doc.metadata.get("article") or ""),
            )

            if key in seen:
                continue

            seen.add(key)
            unique_docs.append(doc)

        return unique_docs[:requested_k]


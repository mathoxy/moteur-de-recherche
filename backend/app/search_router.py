from fastapi import APIRouter, Query
from app.core.dependencies import retriever

router = APIRouter(prefix="/search")


def _serialize_document(document):
    return {
        "content": document.page_content,
        "metadata": document.metadata,
    }

@router.get("/")
def search(
    q: str,
    limit: int = Query(5, ge=1, le=20),
):
    docs = retriever.retrieve(q, k=limit)

    return {
        "results": [
            _serialize_document(doc)
            for doc in docs
        ]
    }
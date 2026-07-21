from fastapi import APIRouter
from app.core.dependencies import retriever

router = APIRouter(prefix="/search")

@router.get("/")
def search(q: str):

    docs = retriever.retrieve(q)

    return {
        "results": docs
    }
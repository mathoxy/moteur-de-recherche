
from app.services.parser import DocumentParser
from app.services.chunker import DocumentChunker
from app.services.vectorstore import VectorStore
from app.services.embeddings import EmbeddingService
from app.services.retriever import Retriever

parser = DocumentParser()
chunker = DocumentChunker()
embeddings = EmbeddingService()
vectorstore = VectorStore(embeddings)
retriever = Retriever(vectorstore)
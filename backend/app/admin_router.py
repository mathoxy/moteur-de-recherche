from fastapi import APIRouter
from app.services.pipeline import IngestionPipeline
from app.services.crawler import SGGCrawler

router  = APIRouter(prefix="/admin")

@router.post("/ingest-data")
def ingest_data():

    pipeline = IngestionPipeline()

    pipeline.ingest_all()

    return {
        "message": "Data ingestion completed."
    }

@router.post("/crawl-data")
def crawl_data(pages: int):
    crawler = SGGCrawler(nbre_pages=pages)
    crawler.run()
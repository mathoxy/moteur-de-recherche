from fastapi import FastAPI
from app.admin_router import router as admin_router
from app.search_router import router as search_router

app = FastAPI(prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur mon API FastAPI"}

app.include_router(
    router=admin_router
)

app.include_router(
    router=search_router
)
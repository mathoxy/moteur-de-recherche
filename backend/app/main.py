from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin_router import router as admin_router
from app.search_router import router as search_router

app = FastAPI(title="LexAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur mon API FastAPI"}


app.include_router(router=admin_router)
app.include_router(router=search_router)
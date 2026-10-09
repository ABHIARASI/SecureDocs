
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.documents import router as document_router
from app.routers.search import router as search_router

app = FastAPI(title="SecureDocs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "SecureDocs API is running"}

app.include_router(auth_router)
app.include_router(document_router)
app.include_router(search_router)

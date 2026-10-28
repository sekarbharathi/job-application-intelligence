from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.application import Application
from app.routes.applications import router as applications_router
from app.routes.documents import router as documents_router
from app.models.document import Document

from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Application Intelligence",
    description="Job application tracking and analytics API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router)

app.include_router(documents_router)


@app.get("/")
def root():
    return {
        "message": "Job Application Intelligence API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
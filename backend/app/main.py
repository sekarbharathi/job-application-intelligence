from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.application import Application
from app.routes.applications import router as applications_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Application Intelligence",
    description="Job application tracking and analytics API",
    version="0.1.0",
)

app.include_router(applications_router)


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
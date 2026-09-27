from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router


app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
    description="AI-powered legal document drafting API.",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# API routes
app.include_router(router)


@app.get("/", tags=["system"])
def root():
    return {
        "name": "LegalEase API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok"
    }
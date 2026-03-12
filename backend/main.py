import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.routers import auth, health, insight, score, analytics, nlp
from backend.utils.database import init_db
from backend.services.scheduler_service import scheduler_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    init_db()
    scheduler_service.start()
    logger.info("Application started successfully")
    yield
    logger.info("Shutting down application...")
    scheduler_service.stop()
    logger.info("Application shut down successfully")

app = FastAPI(
    title="Wellness Dashboard API",
    description="A full-stack health and wellness tracking application",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(insight.router)
app.include_router(score.router)
app.include_router(analytics.router)
app.include_router(nlp.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Wellness Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

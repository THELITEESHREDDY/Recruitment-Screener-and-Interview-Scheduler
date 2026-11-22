from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import backend.db.init_db
from backend.db.connection import get_db
from backend.api.jobs import router as jobs_router
from backend.api.candidates import router as candidates_router
from backend.api.screening import router as screening_router
from backend.api.scheduling import router as scheduling_router
from backend.api.auth import router as auth_router
from backend.api.rankings import router as rankings_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Recruitment Screener API",
    description="AI-powered recruitment screening and interview scheduling system",
    version="1.0.0"
)

app.include_router(rankings_router)
app.include_router(auth_router)
app.include_router(screening_router)
app.include_router(candidates_router)
app.include_router(scheduling_router)
app.include_router(jobs_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
async def root():
    return {
        "message": "Recruitment Screener API is running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "sqlite"
    }
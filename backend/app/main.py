
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1 import datasets
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(datasets.router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}
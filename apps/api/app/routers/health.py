from fastapi import APIRouter
from sqlalchemy import text
from ..core.database import engine

router = APIRouter()

@router.get("/health")
def health():
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {"status": "ok", "service": "api", "db_ok": db_ok}
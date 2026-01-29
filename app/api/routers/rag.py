from fastapi import APIRouter, Depends

from app.authentication.auth import get_current_user
from ...schemas.user_schema import UserSchema, QueriesRequest
from ...db.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/v1/rag", tags=["RAG Routes"])


@router.post("/query")
async def predict_btc_price(
    query: QueriesRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    return {"message": "query endpoint"}


@router.get("/history")
async def predict_btc_price(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    return {"message": "History endpoint"}


@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    return {"message": "Health check endpoint"}

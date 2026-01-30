from fastapi import APIRouter, Depends
import time
from app.authentication.auth import get_current_user
from ...schemas.user_schema import UserSchema, QueryRequest, QueryResponse
from ...db.database import get_db
from sqlalchemy.orm import Session
from ...RAG.query import ITSmartAssistant
from ...models.user_model import Query

router = APIRouter(prefix="/api/v1/rag", tags=["RAG Routes"])

rag_instance = ITSmartAssistant()


@router.post("/query", response_model=QueryResponse)
async def get_rag_answer(
    query: QueryRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    time_start = time.time()
    rag_answer = rag_instance.ask(query.question)
    time_end = time.time()
    latency_ms = time_end - time_start

    answer = rag_answer["answer"]

    new_query = Query(
        user_id=current_user.id,
        question=query.question,
        answer=answer,
        cluster="default",
        latency_ms=latency_ms,
    )
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    return new_query


@router.get("/history")
async def get_query_history(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    queries = db.query(Query).filter(Query.user_id == current_user.id).all()
    if not queries:
        return {"message": "No queries found for the user."}

    return {"queries": queries}


@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    return {"message": "Hello backend is running fine!"}

import os
import time
from pathlib import Path
import mlflow
from fastapi import APIRouter, Depends
from app.authentication.auth import get_current_user
from ...schemas.user_schema import UserSchema, QueryRequest, QueryResponse
from ...db.database import get_db
from sqlalchemy.orm import Session
from ...RAG.query import ITSmartAssistant
from ...models.user_model import Query
from ml.cluster_model import ClusterModel


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")

router = APIRouter(prefix="/api/v1/rag", tags=["RAG Routes"])

rag_instance = ITSmartAssistant()
cluster = ClusterModel(model_path=os.path.join(BASE_DIR, "ml", "model"))


@router.post("/query", response_model=QueryResponse)
@mlflow.trace(name="RAG_Query_Endpoint")
async def get_rag_answer(
    query: QueryRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    mlflow.update_current_trace(
        tags={
            "mlflow.model_name": "IT-Support-Clustering-Model",
            "mlflow.model_version": "1",
            "model": "gemini-2.5-flash",
            "temperature": "0.7",
            "top_k": "4",
            "user_question": query.question,
        }
    )

    time_start = time.time()
    rag_answer = rag_instance.ask(query.question)
    cluster_id = cluster.predict_cluster(query.question)
    time_end = time.time()
    latency_ms = (time_end - time_start) * 1000

    mlflow.update_current_trace(
        tags={
            "final_answer": rag_answer["answer"],
            "latency_ms": f"{latency_ms:.2f}",
            "chunks_used": str(rag_answer.get("source_documents", "N/A")),
            "similarity_score": str(rag_answer.get("score", "N/A")),
        }
    )

    new_query = Query(
        user_id=current_user.id,
        question=query.question,
        answer=rag_answer["answer"],
        cluster=cluster_id,
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

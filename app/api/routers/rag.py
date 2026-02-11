import os
import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import mlflow
from app.authentication.auth import get_current_user
from ml.cluster_model import ClusterModel

from ...db.database import get_db
from ...models.user_model import Query
from ...schemas.user_schema import QueryRequest, QueryResponse, UserSchema

router = APIRouter(prefix="/api/v1/rag", tags=["RAG Routes"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")


cluster = ClusterModel(model_path=os.path.join(BASE_DIR, "ml", "model"))


@router.post("/query", response_model=QueryResponse)
async def get_rag_answer(
    query: QueryRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user),
):
    assistant = getattr(request.app.state, "rag_assistant", None)

    if not assistant:
        raise HTTPException(status_code=503, detail="RAG Assistant is still loading.")

    with mlflow.start_run(run_name="rag_query"):
        mlflow.log_param("user_id", current_user.id)
        mlflow.log_param("rag_version", "v1")

        mlflow.log_param("llm_model", "gemini-2.5-flash")
        mlflow.log_param("temperature", 0.7)
        mlflow.log_param("top_k", 5)
        mlflow.log_text(query.question, "input_question.txt")

        time_start = time.time()
        assistant = request.app.state.rag_assistant
        rag_answer = assistant.ask(query.question)

        cluster_id = cluster.predict_cluster(query.question)

        time_end = time.time()
        latency_ms = (time_end - time_start) * 1000

        mlflow.log_metric("latency_ms", latency_ms)

        mlflow.log_text(rag_answer["answer"], "generated_answer.txt")
        mlflow.log_metric("num_chunks", len(rag_answer["chunks"]))

        if "chunks" in rag_answer:
            mlflow.log_dict(rag_answer["chunks"], "retrieved_chunks.json")

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

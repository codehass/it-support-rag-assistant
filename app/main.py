from fastapi import FastAPI
from .db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from .api.routers import auth, rag
from .config import settings
import mlflow

app = FastAPI(
    title="It Support RAG API",
    description=(
        "This API provides endpoints for users to authenticate and as questions about it support"
    ),
)


mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
mlflow.set_experiment("IT_Support_RAG_Production")

origins = [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(rag.router)


@app.get("/", tags=["Home route"])
def get_home():
    return {"message": "Hello to It Support RAG API"}

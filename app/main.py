from fastapi import FastAPI
from .db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from .api.routers import auth, rag
from .config import settings
import mlflow
from .RAG.query import ITSmartAssistant
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Connecting to MLflow...")
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment("rag-queries")
    print("Loading RAG Model weights...")
    app.state.rag_assistant = ITSmartAssistant()

    yield
    print("Shutting down...")


app = FastAPI(
    title="It Support RAG API",
    lifespan=lifespan,
    description=(
        "This API provides endpoints for users to authenticate and ask questions about IT support"
    ),
)

origins = [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rag.router)


@app.get("/", tags=["Home route"])
def get_home():
    return {"message": "Hello to It Support RAG API"}

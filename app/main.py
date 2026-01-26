import os
from .models.user_model import User
from .db.database import engine, Base, get_db
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()

origins = [FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def get_home():
    return {"message": "Hello to our sentiment api!!"}

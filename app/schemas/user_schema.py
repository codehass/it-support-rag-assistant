from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class QueryResponse(BaseModel):
    id: int
    user_id: int
    question: str
    answer: str
    cluster: int
    latency_ms: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueryRequest(BaseModel):
    question: str

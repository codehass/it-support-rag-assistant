from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str

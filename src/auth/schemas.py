from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional,List
from src.books.schemas import Book

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str =Field(min_length=4,max_length=30)
    email: str = Field(max_length=50)
    password: str = Field(min_length=5)

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime
    books: List[Book]

class UserLoginModel(BaseModel):
    email: str = Field(max_length=50)
    password: str = Field(min_length=5)



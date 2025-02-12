from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(index=True, unique=True)
    password: str = Field(exclude=True)
    name: str
    email: EmailStr = Field(index=True, unique=True)
    created_at: datetime = Field(index=True)

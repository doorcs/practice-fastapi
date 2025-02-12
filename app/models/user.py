from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime

from app.models.ledger import Ledger


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(unique=True)
    password: str = Field(exclude=True)
    name: str
    email: EmailStr = Field(unique=True)
    created_at: datetime = Field(index=True)

    ledgers: list[Ledger] = Relationship()

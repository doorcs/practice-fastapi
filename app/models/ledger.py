from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.models.item import Item


class Ledger(SQLModel, table=True):
    ledger_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.user_id")
    created_at: datetime = Field(default=None)
    year: int = Field(index=True)
    month: int = Field(index=True)
    expense: int = Field(default=0)
    income: int = Field(default=0)
    items: list[Item] = Relationship()
    deleted: bool = Field(default=False, index=True)

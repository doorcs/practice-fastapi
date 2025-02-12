from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.models.item import Item


class Ledger(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner: str
    name: str
    created_at: datetime
    modified_at: datetime = Field(index=True)
    deleted: bool = Field(default=False)

    items: list[Item] = Relationship()
    expense: int = Field(default=0)
    income: int = Field(default=0)

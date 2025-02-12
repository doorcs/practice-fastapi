from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.models.item import Item


class Ledger(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner: int = Field(index=True)
    created_at: datetime
    year: int = Field(index=True)
    month: int = Field(index=True)  # SQL 쿼리 효율을 위해 year, month 필드 추가
    deleted: bool = Field(index=True, default=False)

    items: list[Item] = Relationship()
    expense: int = Field(default=0)
    income: int = Field(default=0)

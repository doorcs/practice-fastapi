from sqlmodel import SQLModel, Field
from datetime import datetime


class Item(SQLModel, table=True):
    item_id: int | None = Field(default=None, primary_key=True)
    ledger_id: int | None = Field(default=None, foreign_key="ledger.ledger_id")
    created_at: datetime = Field(default=None)  # uniqueness를 위해 created_at 필드 추가
    name: str
    price: int
    year: int = Field(index=True)
    month: int = Field(index=True)
    day: int = Field(index=True)
    deleted: bool = Field(default=False)

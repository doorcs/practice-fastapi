from sqlmodel import SQLModel, Field
from datetime import datetime


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field
    amount: int
    created_at: datetime = Field(index=True)
    deleted: bool = Field(default=False)

    ledger_id: int | None = Field(default=None, foreign_key="ledger.id")

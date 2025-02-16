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


# Relationship() 외에도 연관관계를 명확히 표현해주기 위해 back_populates 속성을 추가해주고 싶은데,
# 각각의 모델을 별도의 파일에서 관리하면 다중 상속 문제가 발생한다.
# 파일 분리에 너무 집착하지 말고, 필요에 따라 적절히 모델을 그룹화해보자

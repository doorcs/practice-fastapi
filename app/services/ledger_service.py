from sqlmodel import Session, select
from datetime import datetime
from fastapi import status

from app.models.item import Item
from app.models.ledger import Ledger
from app.models.parameters import HTTPResp


class LedgerService:
    def get_ledger(self, db: Session, user_id: int, when: datetime) -> Ledger | None:
        stmt = select(Ledger).where(
            Ledger.owner == user_id,
            Ledger.year == when.year,
            Ledger.month == when.month,
            Ledger.deleted == False,
        )
        ledger = db.exec(stmt)
        return ledger.first()

    def get_ledgers(self, db: Session, user_id: int) -> list[Ledger]:
        stmt = (
            select(Ledger)
            .where(
                Ledger.owner_id == user_id,
                Ledger.deleted == False,
            )
            .order_by(Ledger.year.desc(), Ledger.month.desc())
        )
        ledgers = db.exec(stmt).all()
        return ledgers

    def create_ledger(
        self, db: Session, user_id: int, when: datetime | None = None
    ) -> HTTPResp:
        # 1. 현재 달의 Ledger가 없는 경우
        # 2. Item insert가 발생할 때 datetime의 month가 Ledger의 Month와 다를 경우
        # -> 새로운 Ledger를 생성해주는데 사용할 함수
        now = datetime.now()
        year = when.year if when else now.year
        month = when.month if when else now.month

        ledger = Ledger(owner=user_id, created_at=now, year=year, month=month)
        try:
            db.add(ledger)
            db.commit()
            db.refresh(ledger)
        except Exception as e:
            print(e)
            return HTTPResp(
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 오류",
            )
        return HTTPResp(success=True, status=status.HTTP_201_CREATED)

    def delete_ledger(self, db: Session, user_id: int, when: datetime) -> HTTPResp:
        ledger = self.get_ledger(db, user_id, when)
        # 사용자는 soft delete 여부를 알 수 없도록, 존재하지 않는 경우와 이미 삭제된 경우를 동일하게 처리
        if ledger is None or ledger.deleted:
            return HTTPResp(
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                detail="해당 기간의 가계부가 존재하지 않습니다",
            )
        ledger.deleted = True
        try:
            db.add(ledger)
            db.commit()
            db.refresh(ledger)
        except Exception as e:
            print(e)
            return HTTPResp(
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스에 문제가 발생했습니다",
            )
        return HTTPResp(success=True, status=status.HTTP_204_NO_CONTENT)  # 삭제 성공

    def get_items(
        self,
        db: Session,
        ledger_id: int,
    ) -> list[Item]:
        stmt = (
            select(Item)
            .where(Item.ledger_id == ledger_id, Item.deleted == False)
            .order_by(Item.created_at.desc())  # 최근에 생성된 Item부터!
        )
        items = db.exec(stmt).all()
        return items

    def add_item(
        self,
        db: Session,
        user_id: int,
        name: str,
        amount: int,
        when: datetime | None = None,
    ) -> bool:
        now = datetime.now()
        ledger = self.get_ledger(db, user_id, when)
        if ledger is None or ledger.month != now.month:
            ledger = self.create_ledger(db, user_id, when)

        mod = when if when else now
        item = Item(
            name=name,
            amount=amount,
            created_at=datetime.now(),  # 시기를 지정하더라도 무조건 now()로
            modified_at=mod,  # 값이 있는 경우 쓰고, 없으면 now()
            ledger_id=ledger.id,
        )

        if amount < 0:
            ledger.expense += abs(amount)
        else:
            ledger.income += amount

        try:
            db.add(item)
            db.commit()
            db.refresh(item)
            db.refresh(ledger)
        except Exception as e:
            print(e)
            return HTTPResp(
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 오류",
            )
        return HTTPResp(success=True, status=status.HTTP_200_OK)

    def delete_item(self, db: Session, user_id: int, when: datetime, item_id: int):
        ledger = self.get_ledger(db, user_id, when)
        stmt = select(Item).where(Item.id == item_id)
        item = db.exec(stmt).first()

        # 사용자는 soft delete 여부를 알 수 없도록, 존재하지 않는 경우와 이미 삭제된 경우를 동일하게 처리
        if item is None or item.deleted:
            return HTTPResp(
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 항목입니다",
            )
        item.deleted = True

        if item.amount < 0:
            ledger.expense -= abs(item.amount)
        else:
            ledger.income -= item.amount

        try:
            db.add(item)
            db.add(ledger)
            db.commit()
            db.refresh(item)
            db.refresh(ledger)
        except Exception as e:
            print(e)
            return HTTPResp(
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스에 문제가 발생했습니다",
            )
        return HTTPResp(success=True, status=status.HTTP_204_NO_CONTENT)  # 삭제 성공

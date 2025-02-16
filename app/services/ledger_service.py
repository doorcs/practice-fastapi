from sqlmodel import Session, select
from datetime import datetime
from fastapi import status

from app.models.item import Item
from app.models.ledger import Ledger
from app.models.parameters import HTTPResp


class LedgerService:
    def ledger_exists(self, db: Session, user_id: int, year: int, month: int) -> bool:
        stmt = select(Ledger).where(
            Ledger.user_id == user_id,
            Ledger.year == year,
            Ledger.month == month,
            Ledger.deleted == False,
        )
        ledger = db.exec(stmt).first()
        # 해당 년, 월에 해당하는 (삭제되지 않은)Ledger가 있는지 확인하고, 있으면 True 없으면 False
        return True if ledger is not None else False

    def get_ledger(  # 반드시 Ledger 객체를 return (없을 경우 만들어서 return)
        self, db: Session, user_id: int, year: int, month: int
    ) -> Ledger:
        if self.ledger_exists(db, user_id, year, month):
            stmt = select(Ledger).where(
                Ledger.user_id == user_id,
                Ledger.year == year,
                Ledger.month == month,
                Ledger.deleted == False,
            )  # 쿼리가 중복되는 문제를 어떻게 해결할 수 있을까? 더 고민해보기
            return db.exec(stmt).first()
        return self.create_ledger(db, user_id, year, month)

    def get_ledgers(self, db: Session, user_id: int) -> list[Ledger]:
        stmt = (
            select(Ledger)
            .where(
                Ledger.user_id == user_id,
                Ledger.deleted == False,
            )
            .order_by(Ledger.year.desc(), Ledger.month.desc())
        )
        ledgers = db.exec(stmt).all()
        return ledgers

    def create_ledger(
        self,
        db: Session,
        user_id: int,
        year: int | None = None,
        month: int | None = None,
    ) -> Ledger:
        now = datetime.now()
        year = year if year else now.year
        month = month if month else now.month

        ledger = Ledger(user_id=user_id, created_at=now, year=year, month=month)
        try:
            db.add(ledger)
            db.commit()
            db.refresh(ledger)
        except Exception as e:
            print(e)
            raise HTTPResp(
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 오류",
            )
        return ledger

    def delete_ledger(
        self, db: Session, user_id: int, year: int, month: int
    ) -> HTTPResp:
        if not self.ledger_exists(db, user_id, year, month):
            return HTTPResp(
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                detail="해당 기간의 가계부가 존재하지 않습니다",
            )
        ledger = self.get_ledger(db, user_id, year, month)
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
        user_id: int,
        year: int | None = None,
        month: int | None = None,
    ) -> list[Item]:
        now = datetime.now()
        year = year if year else now.year
        month = month if month else now.month
        # get_ledger()는 반드시 성공하는 함수
        ledger = self.get_ledger(db, user_id, year, month)
        stmt = (
            select(Item)
            .where(Item.ledger_id == ledger.ledger_id, Item.deleted == False)
            .order_by(Item.day.desc())  # 가장 최근 날짜부터!
        )
        items = db.exec(stmt).all()
        return items

    def add_item(
        self,
        db: Session,
        user_id: int,
        name: str,
        price: int,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> HTTPResp:
        now = datetime.now()
        year = year if year else now.year
        month = month if month else now.month
        day = day if day else now.day
        # get_ledger()는 반드시 성공하는 함수
        ledger = self.get_ledger(db, user_id, year, month)

        item = Item(
            ledger_id=ledger.ledger_id,
            created_at=now,
            name=name,
            price=price,
            year=year,
            month=month,
            day=day,
        )

        if price < 0:
            ledger.expense += abs(price)
        else:
            ledger.income += price

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
        return HTTPResp(success=True, status=status.HTTP_200_OK)

    def delete_item(
        self, db: Session, user_id: int, year: int, month: int, item_id: int
    ) -> HTTPResp:
        ledger = self.get_ledger(db, user_id, year, month)
        stmt = select(Item).where(Item.item_id == item_id)
        item = db.exec(stmt).first()

        if item is None or item.deleted:
            return HTTPResp(
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 항목입니다",
            )
        item.deleted = True

        if item.price < 0:
            ledger.expense -= abs(item.price)
        else:
            ledger.income -= item.price

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

    def modify_item(
        self,
        db: Session,
        user_id: int,
        year: int,
        month: int,
        item_id: int,
        name: str,
        price: int,
        mod_year: int | None = None,
        mod_month: int | None = None,
        mod_day: int | None = None,
    ) -> HTTPResp:
        if not self.ledger_exists(db, user_id, year, month):
            return HTTPResp(
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 항목입니다",
            )

        stmt = select(Item).where(Item.item_id == item_id)
        item = db.exec(stmt).first()

        if item is None or item.deleted:
            return HTTPResp(
                success=False,
                status=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 항목입니다",
            )
        mod_year = mod_year if mod_year is not None else year
        mod_month = mod_month if mod_month is not None else month
        item.year = mod_year
        item.month = mod_month
        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if mod_day is not None:
            item.day = mod_day

        if year != mod_year or month != mod_month:
            src_ledger = self.get_ledger(db, user_id, year, month)
            dst_ledger = self.get_ledger(db, user_id, mod_year, mod_month)
            item.ledger_id = dst_ledger.ledger_id
            if item.price > 0:
                src_ledger.expense -= item.price
                dst_ledger.expense += item.price
            else:  # item.price <= 0
                src_ledger.income += item.price
                src_ledger.income -= item.price

        try:
            db.add(item)
            db.add(src_ledger)
            db.add(dst_ledger)
            db.commit()
            db.refresh(item)
            db.refresh(src_ledger)
            db.refresh(dst_ledger)
        except Exception as e:
            print(e)
            return HTTPResp(
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스에 문제가 발생했습니다",
            )
        return HTTPResp(success=True, status=status.HTTP_200_OK)

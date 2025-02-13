from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from datetime import datetime, timedelta, timezone

from app.models.parameters import HTTPResp, ItemsReq
from app.models.ledger import Ledger
from app.models.item import Item
from app.dependencies.db import get_db_session
from app.dependencies.id import get_user
from app.services.ledger_service import LedgerService

router = APIRouter(prefix="/v1/ledgers")


@router.get("/{YYYY_MM_DD}")
def get_items(
    YYYY_MM_DD: str,
    db=Depends(get_db_session),
    user_id=Depends(get_user),
    ledgerService: LedgerService = Depends(),
) -> HTTPResp | list[Item]:
    if user_id is None:
        return HTTPResp(
            success=False,
            status=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다",
        )
    li = YYYY_MM_DD.split("_")
    year = int(li[0])
    month = int(li[1])

    items = ledgerService.get_items(db, user_id, year, month)
    if len(items) < 1:
        return HTTPResp(
            success=False,
            status=status.HTTP_204_NO_CONTENT,
            detail="해당 기간의 가계부가 존재하지 않습니다",
        )
    return items


@router.delete("/{YYYY_MM_DD}")
def delete_ledger(
    YYYY_MM_DD: str,
    db=Depends(get_db_session),
    user_id=Depends(get_user),
    ledgerService: LedgerService = Depends(),
) -> HTTPResp:
    if user_id is None:
        return HTTPResp(
            success=False,
            status=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다",
        )
    li = YYYY_MM_DD.split("_")
    year = int(li[0])
    month = int(li[1])
    return ledgerService.delete_ledger(
        db, user_id, int(year), int(month)
    )  # delete_ledger() 리턴타입은 HTTPResp, 성공 | 실패 | DB오류 모두 delete_ledger()에서 처리함


@router.post("/{YYYY_MM_DD}")
def add_item(
    YYYY_MM_DD: str,
    name: str,
    price: int,
    db=Depends(get_db_session),
    user_id=Depends(get_user),
    ledgerService: LedgerService = Depends(),
) -> HTTPResp:
    if user_id is None:
        return HTTPResp(
            success=False,
            status=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다",
        )
    li = YYYY_MM_DD.split("_")
    year = int(li[0])
    month = int(li[1])
    day = int(li[2])

    return ledgerService.add_item(db, user_id, name, price, year, month, day)


@router.delete("/{YYYY_MM_DD}/{item_id}")
def delete_item(
    YYYY_MM_DD: str,
    item_id: int,
    db=Depends(get_db_session),
    user_id=Depends(get_user),
    ledgerService: LedgerService = Depends(),
) -> HTTPResp:
    if user_id is None:
        return HTTPResp(
            success=False,
            status=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다",
        )
    li = YYYY_MM_DD.split("_")
    year = int(li[0])
    month = int(li[1])

    return ledgerService.delete_item(db, user_id, year, month, item_id)

from fastapi import APIRouter, Depends, Response, status, Cookie
from datetime import datetime, timedelta, timezone

from app.models.parameters import AuthSignupReq, AuthSigninReq, HTTPResp
from app.services.auth_service import AuthService
from app.dependencies.jwt import JWTUtil
from app.dependencies.db import get_db_session


router = APIRouter(prefix="/v1/auth")


@router.post("/signup")
def auth_signup(
    req: AuthSignupReq,
    response: Response,
    db=Depends(get_db_session),
    jwtUtil: JWTUtil = Depends(),
    authService: AuthService = Depends(),
) -> HTTPResp:
    res = authService.signup(db, req.login_id, req.password, req.name, req.email)
    if not res.success:
        return res
    res.detail = "회원가입 성공"

    user = authService.get_user(db, req.login_id)
    jwt = jwtUtil.create_token(user.model_dump())
    response.set_cookie(
        key="jwt",
        value=jwt,
        # jwtUtil.decode_token()을 호출해 exp 필드를 추출하는것은 너무 비효율적이므로, create_token()에서 exp 필드를 추가하는 로직을 가져와 사용함
        expires=datetime.now(timezone.utc) + timedelta(minutes=60),
        httponly=True,
    )
    return res


@router.post("/signin")
def auth_signin(
    req: AuthSigninReq,
    response: Response,
    db=Depends(get_db_session),
    jwtUtil: JWTUtil = Depends(),
    authService: AuthService = Depends(),
) -> HTTPResp:
    res = authService.signin(db, req.login_id, req.password)
    if not res.success:
        return res
    res.detail = "로그인 성공"

    user = authService.get_user(db, req.login_id)
    jwt = jwtUtil.create_token(user.model_dump())
    response.set_cookie(
        key="jwt",
        value=jwt,
        # jwtUtil.decode_token()을 호출해 exp 필드를 추출하는것은 너무 비효율적이므로, create_token()에서 exp 필드를 추가하는 로직을 가져와 사용함
        expires=datetime.now(timezone.utc) + timedelta(minutes=60),
        httponly=True,
    )
    return res


@router.get("/signout")
def auth_signout(
    response: Response, jwt: str | None = Cookie(default=None)
) -> HTTPResp:
    if jwt is None:
        return HTTPResp(
            success=False,
            status=status.HTTP_400_BAD_REQUEST,
            detail="로그인 상태가 아닙니다",
        )
    response.delete_cookie(key="jwt")
    return HTTPResp(success=True, status=status.HTTP_200_OK, detail="로그아웃 성공")

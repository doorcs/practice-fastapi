from fastapi import Cookie, Depends
from jose import JWTError

from app.dependencies.jwt import JWTUtil


def get_user(
    jwtUtil: JWTUtil = Depends(), jwt: str | None = Cookie(default=None)
) -> int | None:
    if jwt is None:
        return None

    try:
        payload = jwtUtil.decode_token(jwt)
    except JWTError as e:
        print(e)
        return None

    return int(payload.get("user_id"))

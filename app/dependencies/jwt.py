from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError

import env  # 표준 라이브러리 아님

env = env.get_settings()
SECRET_KEY = env.jwt_secret
ALGORITHM = env.algorithm


class JWTUtil:
    def create_token(
        self, payload: dict, expires_delta: timedelta | None = timedelta(minutes=60)
    ):
        payload.update({"exp": datetime.now(timezone.utc) + expires_delta})
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except (
            ExpiredSignatureError
        ):  # jwt.decode()는 기본적으로 "exp" 필드에 대한 검사를 수행!
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

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
    ) -> str:
        payload.update({"exp": datetime.now(timezone.utc) + expires_delta})
        del payload["deleted"]
        del payload["created_at"]
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        # jwt.decode()는 기본적으로 "exp" 필드에 대한 검사를 수행!
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        # 위조/변조된 토큰일 경우 ( 토큰 signature 검증에 실패했을 경우 )
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

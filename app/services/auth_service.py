from sqlmodel import Session, select
from datetime import datetime
from fastapi import status
import bcrypt

from app.models.user import User
from app.models.parameters import AuthResp


class AuthService:
    def hash_password(self, pw: str) -> str:
        return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, input_pw: str, pw: str) -> bool:
        return bcrypt.checkpw(input_pw.encode("utf-8"), pw)

    def check_id_dup(self, db: Session, login_id: str) -> bool:
        stmt = select(User).where(User.login_id == login_id)
        results = db.exec(stmt)
        if results.first() is None:
            return False
        return True

    def check_email_dup(self, db: Session, email: str) -> bool:
        stmt = select(User).where(User.email == email)
        results = db.exec(stmt)
        if results.first() is None:
            return False
        return True

    def get_user(self, db: Session, login_id: str) -> User | None:
        stmt = select(User).where(User.login_id == login_id)
        results = db.exec(stmt)
        return results.first()  # None일 경우 None을 반환!

    # 중복 가입을 어떻게 처리하는 것이 좋을까? 일단 이메일, 로그인 아이디 중복 검증
    def signup(
        self, db: Session, login_id: str, pw: str, name: str, email: str
    ) -> AuthResp:
        password = self.hash_password(pw)
        user = User(
            login_id=login_id,
            password=password,
            name=name,
            email=email,
            created_at=datetime.now(),
        )

        if self.check_id_dup(db, login_id):
            return AuthResp(
                success=False,
                status=status.HTTP_409_CONFLICT,
                detail="이미 가입된 아이디입니다",
            )

        if self.check_email_dup(db, email):
            return AuthResp(
                success=False,
                status=status.HTTP_409_CONFLICT,
                detail="이미 가입된 메일 주소입니다",
            )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as e:
            print(e)
            return AuthResp(
                success=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스에 문제가 발생했습니다",
            )
        return AuthResp(success=True, status=status.HTTP_201_CREATED)

    def signin(self, db: Session, login_id: str, pw: str) -> AuthResp:
        user = self.get_user(db, login_id)
        if user is None:
            return AuthResp(
                success=False,
                status=status.HTTP_401_UNAUTHORIZED,
                detail="존재하지 않는 사용자 정보입니다",
            )
        if self.verify_password(pw, user.password):
            return AuthResp(success=True, status=status.HTTP_200_OK)
        return AuthResp(
            success=False,
            status=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 틀립니다",
        )

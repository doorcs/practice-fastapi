from pydantic import BaseModel, EmailStr


class AuthSignupReq(BaseModel):
    login_id: str
    password: str
    name: str
    email: EmailStr


class AuthSigninReq(BaseModel):
    login_id: str
    password: str


class HTTPResp(BaseModel):
    success: bool
    status: int
    detail: str | None = None

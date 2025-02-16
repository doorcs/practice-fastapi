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


# 성공/실패 응답을 모두 HTTPResp라는 클래스로 감싸서 보내주는건 별로 좋은 생각이 아닌 것 같다.
# 서버에서 응답의 success필드를 False로 설정해서 보내줘도 response.ok 가 true를 반환하기 때문에
# 프론트엔드에서 모든 ok 요청을 파싱해 필드 값을 조회해야 하는데, response가 semantic하지 않을 뿐 아니라 프론트엔드 코드의 복잡성이 증가하고, 직관적이지도 않다
# 요청과 응답을 어떻게 구조화하면 좋을지 고민해보자

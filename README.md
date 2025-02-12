## Practice-FastAPI

- Python의 [FastAPI](https://fastapi.tiangolo.com) 프레임워크를 활용해 간단한 API 서버 구현해보기

## About

> Python 3.13.1 used : 파이썬 3.13.1 버전을 사용했습니다
- 가상환경 설정
  - python -m venv .venv
  - source .venv/bin/activate
    - 또는, pyenv와 pyenv-virtualenv를 활용한 가상환경 설정
    - `pyenv virtualenv 3.13.1 fastapi && pyenv local fastapi`
- 필요한 라이브러리 설치
  - pip install "fastapi[standard]" sqlmodel pydantic_settings bcrypt python-jose
    - 또는, `requirements.txt` 파일을 통해 개발환경과 동일한 버전의 라이브러리 설치
    - `pip install -r requirements.txt`
    <!-- requirements.txt를 만드려면, `pip freeze > requirements.txt` ( redirect를 통해 pip freeze 출력을 저장 ) -->

## etc

- 직접 구현한 모듈 import 구문은 다른 import 구문과 한 줄 띄워 구분함
- BLACK formatter를 활용해 자동 포매팅 ( format on save: Y )
- 리턴 타입을 `ReturnType | None` 대신, `ReturnType` 단일 타입으로 두고, 예외는 HTTPException raise 처리
- Union Type Hinting 사용 ( detail: str | None = None )
  - Python 3.10에 도입된 파이프 연산자(|) 활용
  - Python<3.10에선:
    - `from typing import Optional` 추가 후,
    - `detail: Optional[str] = None` 처럼 사용

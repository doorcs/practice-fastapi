from fastapi import FastAPI

from app.routers import auth_router
from app.dependencies.db import db_init

db_init()

app = FastAPI()
app.include_router(auth_router.router)

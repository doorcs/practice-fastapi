from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import auth_router
from app.dependencies.db import db_init


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router.router)

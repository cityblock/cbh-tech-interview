import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from server.db.engine import Session
from server.db.migrate import migrate
from server.db.seed import seed

PORT = int(os.environ.get("PORT") or 4000)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    migrate()
    with Session() as db:
        seed(db)
    yield


app = FastAPI(lifespan=lifespan)


def dev() -> None:
    uvicorn.run("server.index:app", host="localhost", port=PORT, reload=True)

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from server.context import Context
from server.db.engine import Session
from server.db.migrate import migrate
from server.db.seed import seed
from server.schema import schema

PORT = int(os.environ.get("PORT") or 4000)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    migrate()
    with Session() as db:
        seed(db)
    print(f"🚀 GraphQL server ready at http://localhost:{PORT}/graphql")
    yield


async def get_context() -> AsyncIterator[Context]:
    with Session() as db:
        yield Context(db=db)


app = FastAPI(lifespan=lifespan)
app.include_router(GraphQLRouter(schema, context_getter=get_context), prefix="/graphql")


def dev() -> None:
    uvicorn.run("server.index:app", host="localhost", port=PORT, reload=True)

import os

import uvicorn
from fastapi import FastAPI

PORT = int(os.environ.get("PORT") or 4000)

app = FastAPI()


def dev() -> None:
    uvicorn.run("server.index:app", host="localhost", port=PORT, reload=True)

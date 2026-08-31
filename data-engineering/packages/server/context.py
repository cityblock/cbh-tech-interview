from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext


# Strawberry's FastAPI integration rejects any context that is neither a dict
# nor a BaseContext subclass, and BaseContext sets its attributes in __init__.
class Context(BaseContext):
    def __init__(self, db: Session) -> None:
        super().__init__()
        self.db = db

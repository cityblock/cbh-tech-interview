from sqlalchemy.orm import Session

from server.db.seeds.users import seed as seed_users


def seed(db: Session) -> None:
    seed_users(db)

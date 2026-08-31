import json

import strawberry
from sqlalchemy import select

from server.context import Context
from server.db.models import User as UserRow
from server.types import UpdateUserInput, User, UserAvailability


def hydrate(row: UserRow) -> User:
    return User(
        id=strawberry.ID(row.id),
        firstName=row.firstName,
        lastName=row.lastName,
        phoneNumber=row.phoneNumber,
        availability=UserAvailability(**json.loads(row.availability)),
    )


@strawberry.type
class Query:
    @strawberry.field
    def users(self, info: strawberry.Info[Context]) -> list[User]:
        rows = info.context.db.execute(select(UserRow).order_by(UserRow.firstName)).scalars().all()
        return [hydrate(row) for row in rows]

    @strawberry.field
    def user(self, info: strawberry.Info[Context], id: strawberry.ID) -> User | None:
        row = info.context.db.get(UserRow, id)
        return hydrate(row) if row else None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_user(
        self,
        info: strawberry.Info[Context],
        id: strawberry.ID,
        input: UpdateUserInput,
    ) -> User:
        db = info.context.db

        row = db.get(UserRow, id)
        if row is not None:
            if input.firstName is not strawberry.UNSET:
                row.firstName = input.firstName
            if input.lastName is not strawberry.UNSET:
                row.lastName = input.lastName
            if input.phoneNumber is not strawberry.UNSET:
                row.phoneNumber = input.phoneNumber
            if input.availability is not strawberry.UNSET:
                row.availability = json.dumps(
                    {"availableDays": input.availability.availableDays},
                    separators=(",", ":"),
                )
            db.commit()

        row = db.get(UserRow, id)
        if row is None:
            raise Exception(f"User {id} not found")
        return hydrate(row)

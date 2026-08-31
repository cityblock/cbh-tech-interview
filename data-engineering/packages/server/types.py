import strawberry


@strawberry.type
class UserAvailability:
    availableDays: list[str]


@strawberry.type
class User:
    id: strawberry.ID
    firstName: str
    lastName: str
    phoneNumber: str
    availability: UserAvailability


@strawberry.input
class UserAvailabilityInput:
    availableDays: list[str]


@strawberry.input
class UpdateUserInput:
    # UNSET is the analog of an absent key in TypeScript: it keeps these fields
    # defaultless in the schema and lets a resolver tell "omitted" from "null".
    firstName: str | None = strawberry.UNSET
    lastName: str | None = strawberry.UNSET
    phoneNumber: str | None = strawberry.UNSET
    availability: UserAvailabilityInput | None = strawberry.UNSET

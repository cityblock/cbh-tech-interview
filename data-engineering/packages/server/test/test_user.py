from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from strawberry.fastapi import GraphQLRouter

from server.context import Context
from server.db.engine import Session, engine
from server.db.migrate import migrate
from server.db.seed import seed
from server.schema import schema


async def get_context() -> AsyncIterator[Context]:
    with Session() as db:
        yield Context(db=db)


app = FastAPI()
app.include_router(GraphQLRouter(schema, context_getter=get_context), prefix="/graphql")
client = TestClient(app)


def gql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    res = client.post("/graphql", json={"query": query, "variables": variables})
    return res.json()


@pytest.fixture(scope="module", autouse=True)
def seeded() -> Iterator[None]:
    migrate()
    with Session() as db:
        seed(db)
    yield
    engine.dispose()


class TestUserResolvers:
    def test_lists_seeded_users_with_parsed_availability(self) -> None:
        result = gql("{ users { id firstName availability { availableDays } } }")
        assert result.get("errors") is None
        assert len(result["data"]["users"]) > 0
        assert isinstance(result["data"]["users"][0]["availability"]["availableDays"], list)

    def test_updates_phone_number_and_availability(self) -> None:
        users = gql("{ users { id } }")
        id = users["data"]["users"][0]["id"]

        updated = gql(
            """mutation U($id: ID!, $input: UpdateUserInput!) {
                updateUser(id: $id, input: $input) {
                    id phoneNumber availability { availableDays }
                }
            }""",
            {
                "id": id,
                "input": {
                    "phoneNumber": "+15550000000",
                    "availability": {"availableDays": ["Mon"]},
                },
            },
        )
        assert updated.get("errors") is None
        assert updated["data"]["updateUser"]["phoneNumber"] == "+15550000000"
        assert updated["data"]["updateUser"]["availability"]["availableDays"] == ["Mon"]

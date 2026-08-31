from typing import Any

from server.context import Context
from server.db.engine import Session
from server.schema import schema


# Without JavaScript the browser cannot hold GraphQL state, so pages execute
# their documents against the schema in-process rather than over HTTP. The seam
# is unchanged: the form still reads and writes availability through GraphQL.
async def execute(document: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    with Session() as db:
        result = await schema.execute(
            document,
            variable_values=variables,
            context_value=Context(db=db),
        )

    if result.errors:
        raise result.errors[0]
    return result.data or {}

import strawberry
from strawberry.schema.config import StrawberryConfig

from server.resolvers.user import Mutation, Query

# auto_camel_case is what turns update_user into updateUser, keeping the schema
# identical to the software-engineering track's SDL.
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(auto_camel_case=True),
)

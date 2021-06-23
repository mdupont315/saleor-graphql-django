import graphene
# from ..decorators import permission_required

from .types import Store
from ..account.types import User
from ..core.fields import FilterInputConnectionField
from .filters import StoreFilterInput
from .sorters import StoreSortingInput
from .mutations.stores import (
    StoreCreate,
    StoreDelete,
    StoreUpdate,
)
from .resolvers import (
    resolve_store,
    resolve_stores,
    resolve_user_store
)

class StoreQueries(graphene.ObjectType):
    store = graphene.Field(
        Store,
        id=graphene.Argument(
            graphene.ID,
            description="ID of the store.",
        ),
        description="Look up a store by ID.",
    )
    stores = FilterInputConnectionField(
        Store,
        filter=StoreFilterInput(description="Filtering options for store."),
        sort_by=StoreSortingInput(description="Sort store."),
        description="List of the store.",
    )
    user_store = graphene.Field(
        User,
        store_id=graphene.Argument(
            graphene.ID,
            description="ID of the owner.",
        ),
        description="Look up a owner by ID.",
    )

    def resolve_store(self, info, id=None, slug=None):
        return resolve_store(info, id, slug)

    def resolve_stores(self, info, **kwargs):
        return resolve_stores(info, **kwargs)

    def resolve_user_store(self, info, store_id=None, slug=None):
        return resolve_user_store(info, store_id, slug)

class StoreMutations(graphene.ObjectType):
    # store mutations
    store_create = StoreCreate.Field()
    store_delete = StoreDelete.Field()
    store_update = StoreUpdate.Field()

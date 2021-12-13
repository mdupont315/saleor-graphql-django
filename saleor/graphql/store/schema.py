import graphene

from saleor.views import sio

from ..account.types import User
from ..core.fields import FilterInputConnectionField
from .filters import StoreFilterInput
from .mutations.stores import (MyStoreUpdate, StoreCreate, StoreDelete,
                               StoreUpdate,TestSubscription)
from .resolvers import (resolve_my_store, resolve_store, resolve_stores,
                        resolve_user_store)
from .sorters import StoreSortingInput
from .types import Store

# from ..decorators import permission_required


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
    my_store = graphene.Field(
        Store,
        description="Look up a store by ID.",
    )

    def resolve_store(self, info, id=None, slug=None):
        return resolve_store(info, id, slug)

    def resolve_stores(self, info, **kwargs):
        return resolve_stores(info, **kwargs)

    def resolve_user_store(self, info, store_id=None, slug=None):
        return resolve_user_store(info, store_id, slug)

    def resolve_my_store(self, info, **kwargs):
        return resolve_my_store(info, **kwargs)

class StoreMutations(graphene.ObjectType):
    # store mutations
    store_create = StoreCreate.Field()
    test_subscription = TestSubscription.Field()

    store_delete = StoreDelete.Field()
    store_update = StoreUpdate.Field()
    my_store_update = MyStoreUpdate.Field()

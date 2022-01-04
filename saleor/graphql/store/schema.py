import graphene

from saleor.views import sio

from ..account.types import User
from ..core.fields import FilterInputConnectionField
from .filters import CustomDomainFilterInput, StoreFilterInput
from .mutations.stores import (CustomDomainBulkDelete, CustomDomainCreate, CustomDomainDelete, CustomDomainUpdate, MyStoreUpdate, StoreCreate, StoreDelete,
                               StoreUpdate,TestSubscription)
from .resolvers import (resolve_custom_domain, resolve_custom_domains, resolve_my_store, resolve_store, resolve_stores,
                        resolve_user_store)
from .sorters import StoreSortingInput,CustomDomainSortInput
from .types import CustomDomain, Store

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

    custom_domains = FilterInputConnectionField(
        CustomDomain,
        filter=CustomDomainFilterInput(description="Filtering table services."),
        sort_by=CustomDomainSortInput(description="Sort table services."),
        description="List of the table service.",
    )

    custom_domain = graphene.Field(
        CustomDomain,
        id=graphene.Argument(
            graphene.ID,
            description="ID of table service.",
        ),
        description="Get table service.",
    )

    def resolve_store(self, info, id=None, slug=None):
        return resolve_store(info, id, slug)

    def resolve_stores(self, info, **kwargs):
        return resolve_stores(info, **kwargs)

    def resolve_user_store(self, info, store_id=None, slug=None):
        return resolve_user_store(info, store_id, slug)

    def resolve_my_store(self, info, **kwargs):
        return resolve_my_store(info, **kwargs)

    def resolve_custom_domains(self, info, **kwargs):
        return resolve_custom_domains(info, **kwargs)

    def resolve_custom_domain(self, info, id=None, **kwargs):
        return resolve_custom_domain(info, id, **kwargs)

class StoreMutations(graphene.ObjectType):
    # store mutations
    store_create = StoreCreate.Field()
    test_subscription = TestSubscription.Field()

    store_delete = StoreDelete.Field()
    store_update = StoreUpdate.Field()
    my_store_update = MyStoreUpdate.Field()

    custom_domain_create = CustomDomainCreate.Field()
    custom_domain_update = CustomDomainUpdate.Field()
    custom_domain_delete = CustomDomainDelete.Field()
    custom_domain_bulk_delete = CustomDomainBulkDelete.Field()

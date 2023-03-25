from saleor.graphql.table_service.filters import TableServiceFilterInput
from saleor.graphql.table_service.sorters import TableServiceSortInput
from saleor.graphql.table_service.types import TableService
import graphene
from ..decorators import permission_required
from ..core.fields import FilterInputConnectionField
from .resolvers import resolve_table_services, resolve_table_service
from ...core.permissions import TableServicePermissions
from .mutations import (
    TableServiceCreate,
    TableServiceUpdate,
    TableServiceDelete,
    TableServiceBulkDelete,
)

class TableServiceQueries(graphene.ObjectType):
    table_services = FilterInputConnectionField(
        TableService,
        filter=TableServiceFilterInput(description="Filtering table services."),
        sort_by=TableServiceSortInput(description="Sort table services."),
        description="List of the table service.",
    )

    table_service = graphene.Field(
        TableService,
        id=graphene.Argument(
            graphene.ID,
            description="ID of table service.",
        ),
        description="Get table service.",
    )

    @permission_required(TableServicePermissions.MANAGE_TABLE_SERVICE)
    def resolve_table_services(self, info, **kwargs):
        return resolve_table_services(info, **kwargs)

    # @permission_required(TableServicePermissions.MANAGE_TABLE_SERVICE)
    def resolve_table_service(self, info, id=None, **kwargs):
        return resolve_table_service(info, id, **kwargs)

class TableServiceMutations(graphene.ObjectType):
    table_service_create = TableServiceCreate.Field()
    table_service_update = TableServiceUpdate.Field()
    table_service_delete = TableServiceDelete.Field()
    table_service_bulk_delete = TableServiceBulkDelete.Field()

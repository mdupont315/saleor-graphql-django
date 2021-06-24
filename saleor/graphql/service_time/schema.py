from saleor.graphql.service_time.mutations import ServiceTimeCreate
from .types import ServiceTime
import graphene
from ..decorators import permission_required
from ..core.fields import FilterInputConnectionField
from .resolvers import resolve_service_time

class ServiceTimeQueries(graphene.ObjectType):
    servie_times = FilterInputConnectionField(
        ServiceTime,
        description="List of the servicetime.",
    )

    def resolve_servie_times(self, **kwargs):
        return resolve_service_time(self, **kwargs)

# class ServiceTimeMutations(graphene.ObjectType):
#     # store mutations
#     service_time_create = ServiceTimeCreate.Field()
    # service_time_update = ServiceTimeUpdate.Field()

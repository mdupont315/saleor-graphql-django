from .types import Option
import graphene
from ..decorators import permission_required
from ..core.fields import FilterInputConnectionField
# from .resolvers import resolve_service_time
from .mutations import (
    OptionCreate,
)

# class ServiceTimeQueries(graphene.ObjectType):
#     service_times = FilterInputConnectionField(
#         ServiceTime,
#         description="List of the servicetime.",
#     )

#     def resolve_servie_times(self, info, **kwargs):
#         return resolve_service_time(self, info, **kwargs)

class OptionMutations(graphene.ObjectType):
    # store mutations
    option_create = OptionCreate.Field()
    # service_time_update = ServiceTimeUpdate.Field()

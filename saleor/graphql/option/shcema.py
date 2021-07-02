from .types import Option, OptionValue
import graphene
from ..decorators import permission_required
from ..core.fields import FilterInputConnectionField
from .resolvers import resolve_options, resolve_option, resolve_option_values
from .mutations import (
    OptionCreate,
    OptionUpdate,
    OptionDelete,
    UpdateOptionValue,
    DeleteBulkOptionValue,
)

class OptionQueries(graphene.ObjectType):
    options = FilterInputConnectionField(
        Option,
        description="List of the servicetime.",
    )

    option = graphene.Field(
        Option,
        id=graphene.Argument(
            graphene.ID,
            description="ID of the store.",
        ),
        description="List of the servicetime.",
    )

    option_values = FilterInputConnectionField(
        OptionValue,
        id=graphene.Argument(
            graphene.ID,
            description="ID of the option.",
        ),
        description="List of the servicetime.",
    )

    def resolve_options(self, info, **kwargs):
        return resolve_options(self, info, **kwargs)

    def resolve_option(self, info, id=None):
        return resolve_option(self, info, id)

    def resolve_option_values(self, info, id=None, **kwargs):
        return resolve_option_values(self, info, id, **kwargs)

class OptionMutations(graphene.ObjectType):
    # store mutations
    option_create = OptionCreate.Field()
    option_update = OptionUpdate.Field()
    option_delete = OptionDelete.Field()
    option_value_update = UpdateOptionValue.Field()
    bulk_option_value_delete = DeleteBulkOptionValue.Field()

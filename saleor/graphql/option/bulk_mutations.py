import graphene
from ..core.mutations import ModelBulkDeleteMutation
from ...product import models
from ...core.permissions import ProductPermissions
from ..core.types.common import OptionError

class OptionBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = graphene.List(
            graphene.ID, required=True, description="List of option IDs to delete."
        )

    class Meta:
        description = "Deletes options."
        model = models.Option
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_errors"
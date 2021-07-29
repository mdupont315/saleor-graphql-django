from ..core.types.common import TableServiceError
import graphene
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ...table_service import models
from ...core.permissions import TableServicePermissions

class TableServiceInput(graphene.InputObjectType):
    table_name = graphene.String(
        description="table name",
        required=True
    )
    table_qr_code = graphene.String(
        description="table qr code",
    )


class TableServiceCreate(ModelMutation):
    class Arguments:
        input = TableServiceInput(
            required=True, description="Fields required to create table service."
        )

    class Meta:
        description = "Creates a table service with QR code."
        model = models.TableService
        permissions = (TableServicePermissions.MANAGE_TABLE_SERVICE,)
        error_type_class = TableServiceError
        error_type_field = "table_service_errors"


class TableServiceUpdate(TableServiceCreate):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a table service to update.")
        input = TableServiceInput(
            required=True, description="Fields required to table service time."
        )

    class Meta:
        description = "Update service time."
        model = models.TableService
        permissions = (TableServicePermissions.MANAGE_TABLE_SERVICE,)
        error_type_class = TableServiceError
        error_type_field = "table_service_errors"

class TableServiceDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of an attribute to delete.")

    class Meta:
        description = "Update service time."
        model = models.TableService
        permissions = (TableServicePermissions.MANAGE_TABLE_SERVICE,)
        error_type_class = TableServiceError
        error_type_field = "table_service_errors"

class TableServiceBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = graphene.List(
            graphene.ID, required=True, description="List of attribute IDs to delete."
        )

    class Meta:
        description = "Update service time."
        model = models.TableService
        permissions = (TableServicePermissions.MANAGE_TABLE_SERVICE,)
        error_type_class = TableServiceError
        error_type_field = "table_service_errors"
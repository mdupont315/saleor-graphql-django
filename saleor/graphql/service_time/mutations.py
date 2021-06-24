from saleor.graphql.core.types.common import ServiceTimeError
import graphene
from ..core.mutations import ModelMutation
from ...service_time import models
from ...core.permissions import StorePermissions

class ServiceTimeInput(graphene.InputObjectType):
    # Delivery
    dl_delivery_time = graphene.Int(
       required=True,
       description="Delivery service time."
    )
    dl_time_gap = graphene.Int(
        required=True,
       description="Delivery service gap."
    )
    dl_as_soon_as_posible = graphene.Boolean(
        required=True,
       description="Delivery as_soon_as_posible flag."
    )
    dl_allow_preorder = graphene.Boolean(
        required=True,
       description="Delivery dl_allow_preorder flag."
    )
    dl_preorder_day = graphene.Int(
       required=True,
       description="Delivery preorder day."
    )
    dl_same_day_order = graphene.Boolean(
        required=True,
       description="Delivery dl_same_day_order flag."
    )
    dl_service_time = graphene.JSONString(
        required=True,
       description="Delivery service time setting.")

    # Pickup
    pu_delivery_time = graphene.Int(
       required=True,
       description="Pickup service time."
    )
    pu_time_gap = graphene.Int(
        required=True,
       description="Pickup service gap."
    )
    pu_as_soon_as_posible = graphene.Boolean(
        required=True,
       description="Pickup as_soon_as_posible flag."
    )
    pu_allow_preorder = graphene.Boolean(
        required=True,
       description="Pickup dl_allow_preorder flag."
    )
    pu_preorder_day = graphene.Int(
       required=True,
       description="Pickup preorder day."
    )
    pu_same_day_order = graphene.Boolean(
        required=True,
       description="Pickup dl_same_day_order flag."
    )
    pu_service_time = graphene.JSONString(
        required=True,
       description="Pickup service time setting.")


class ServiceTimeCreate(ModelMutation):
    class Arguments:
        input = ServiceTimeInput(
            required=True, description="Fields required to create service time."
        )

    class Meta:
        description = "Creates service time."
        model = models.ServiceTime
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = ServiceTimeError
        error_type_field = "store_errors"


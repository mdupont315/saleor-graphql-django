import graphene
from ...servicetime import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata

class ServiceTime(CountableDjangoObjectType):
    dl_delivery_time = graphene.Int(description="Delivery time setting")
    dl_time_gap = graphene.Int(description="Time gap setting")
    dl_as_soon_as_posible = graphene.Boolean(description="As soon as posible setting")
    dl_allow_preorder = graphene.Boolean(description="allow preorder setting")
    dl_preorder_day = graphene.Int(description="Delivery time setting")
    dl_same_day_order = graphene.Boolean(description="same day ỏder setting")
    dl_service_time = graphene.String(
        description="Service time.",
    )

    pu_delivery_time = graphene.Int(description="Delivery time setting")
    pu_time_gap = graphene.Int(description="Time gap setting")
    pu_as_soon_as_posible = graphene.Boolean(description="As soon as posible setting")
    pu_allow_preorder = graphene.Boolean(description="allow preorder setting")
    pu_preorder_day = graphene.Int(description="Delivery time setting")
    pu_same_day_order = graphene.Boolean(description="same day ỏder setting")
    pu_service_time = graphene.String(
        description="Service time.",
    )
    class Meta:
        description = (
            "Service time config"
        )
        only_fields = [
            "dl_delivery_time",
            "dl_time_gap",
            "dl_as_soon_as_posible",
            "dl_allow_preorder",
            "dl_preorder_day",
            "dl_same_day_order",
            "dl_service_time",
            "pu_delivery_time",
            "pu_time_gap",
            "pu_as_soon_as_posible",
            "pu_allow_preorder",
            "pu_preorder_day",
            "pu_same_day_order",
            "pu_service_time",
            "id",
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.ServiceTime
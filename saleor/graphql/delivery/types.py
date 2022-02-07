import graphene 
from ...delivery import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata


class Delivery(CountableDjangoObjectType):
    delivery_area = graphene.JSONString(
        description="Delivery area setting."
    )
    delivery_fee = graphene.Float(
        description="Delivery fee setting."
    )
    from_delivery = graphene.Float(
        description="Fee delivery from setting."
    )
    min_order = graphene.Float(
        description="Min order value setting."
    )
    enable_for_big_order = graphene.Boolean(
        description="Min order value setting."
    )
    enable_custom_delivery_fee = graphene.Boolean(
        description="Custom delivery fee setting."
    )

    
    class Meta:
        description = (
            "Delivery Setting."
        )
        only_fields = [
            "delivery_area",
            "delivery_fee",
            "from_delivery",
            "min_order",
            "enable_for_big_order",
            "enable_custom_delivery_fee",
            "id"
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.Delivery

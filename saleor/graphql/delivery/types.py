import graphene 
from graphene_django import DjangoObjectType
from ...delivery import models
from ..core.connection import CountableDjangoObjectType


class Delivery(CountableDjangoObjectType):
    delivery_area = graphene.String()
    delivery_fee = graphene.Float()
    from_delivery = graphene.Float()
    min_order = graphene.Float()
    class Meta:
        model = models.Delivery
        field = [
            "id",
            "delivery_area",
            "delivery_fee",
            "from_delivery",
            "min_order"
        ]
from graphene_django import DjangoObjectType
from ...delivery import models

class Delivery(DjangoObjectType):
    class Meta:
        model = models.Delivery
        field = ("id",  "delivery_area", "delivery_fee", "from_delivery", "min_order")
import graphene 

from graphene_django import DjangoObjectType
from ...delivery import models
from .types import Delivery

from .types import(
    resolve_deliveries,
    resolve_delivery
)

from .mutations.deliveries import(
    DeliveryCreate,
    DeliveryUpdate,
    DeliveryDelete
)

class DeliveryQuery(graphene.ObjectType):
    delivery = graphene.Field(Delivery, id=graphene.Int())
    deliveries = graphene.List(Delivery)

    def resolve_deliveries(self, info, **kwargs):
        return resolve_deliveries(info, **kwargs)

    def resolve_delivery(self, info, **kwargs):
        id = kwargs.get('id')

        return resolve_delivery(info, **kwargs)

class DeliveryMutation(graphene.ObjectType):
    create_delivery = DeliveryCreate.Field()
    update_delivery = DeliveryUpdate.Field()
    delete_delivery = DeliveryDelete.Field()
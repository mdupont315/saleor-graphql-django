import graphene 

from graphene_django import DjangoObjectType
from ...delivery import models
from .types import Delivery

from .resolvers import(
    resolve_deliveries,
    resolve_delivery
)

from .mutations.deliveries import(
    CreateDelivery,
    UpdateDelivery,
    # DeliveryDelete
)

class DeliveryQueries(graphene.ObjectType):
    delivery = graphene.Field(Delivery, id=graphene.Int())
    deliveries = graphene.List(Delivery)

    def resolve_deliveries(self, info, **kwargs):
        return resolve_deliveries(info, **kwargs)

    def resolve_delivery(self, info, **kwargs):
        id = kwargs.get('id')

        return resolve_delivery(info, id = id)


        
class DeliveryMutations(graphene.ObjectType):
    create_delivery = CreateDelivery.Field()
    update_delivery = UpdateDelivery.Field()
    # delete_delivery = DeliveryDelete.Field()
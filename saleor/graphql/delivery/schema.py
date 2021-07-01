import graphene 
from .types import Delivery
from .resolvers import(
    resolve_deliveries,
    resolve_delivery
)
from .mutations.deliveries import(
    DeliveryCreate,
    DeliveryUpdate,
)

class DeliveryQueries(graphene.ObjectType):
    delivery = graphene.Field(
        Delivery, 
        id=graphene.Argument(
            graphene.ID,
            description="ID of the delivery."
        ),
        description="Look up the delivery."
    )
    deliveries = graphene.List(
        Delivery,
        description="List of the deliveries"
    )

    def resolve_deliveries(self, info, **kwargs):
        return resolve_deliveries(info, **kwargs)

    def resolve_delivery(self, info, id=None):
        return resolve_delivery(info, id)


        
class DeliveryMutations(graphene.ObjectType):
    delivery_create = DeliveryCreate.Field()
    delivery_update = DeliveryUpdate.Field()

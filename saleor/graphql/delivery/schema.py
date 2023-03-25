import graphene 
from .types import Delivery
from ..core.fields import FilterInputConnectionField
from .resolvers import(
    resolve_deliveries,
    resolve_delivery
)
from .mutations.deliveries import(
    DeliveryCreate,
    DeliveryUpdate,
)

class DeliveryQueries(graphene.ObjectType):
    current_delivery = graphene.Field(
        Delivery, 
        description="Look up the delivery."
    )
    deliveries = graphene.List(
        Delivery,
        description="List of the deliveries"
    )

    def resolve_deliveries(self, info, **kwargs):
        return resolve_deliveries(info, **kwargs)

    def resolve_current_delivery(self, info, **kwargs):
        return resolve_delivery(info, **kwargs)


        
class DeliveryMutations(graphene.ObjectType):
    delivery_create = DeliveryCreate.Field()
    delivery_update = DeliveryUpdate.Field()

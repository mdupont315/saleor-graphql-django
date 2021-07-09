import graphene 
from ...delivery import models

def resolve_deliveries(info, **kwargs):
    return models.Delivery.objects.all()

def resolve_delivery(info, **kwargs):
    # _type, store_pk = graphene.Node.from_global_id(id)
    # store = models.Store.objects.get(pk=store_pk)
    delivery = models.Delivery.objects.first()
    return delivery





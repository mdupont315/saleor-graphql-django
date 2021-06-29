import graphene 
from ...delivery import models

def resolve_deliveries(info, **kwargs):
    return models.Delivery.objects.all();

def resolve_delivery( info, deliveryId=None):

    delivery = models.Delivery.objects.get(id=deliveryId)
    return delivery





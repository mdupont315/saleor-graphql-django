import graphene 

from graphene_django import DjangoObjectType
from ...delivery import models

def resolve_deliveries(info, **kwargs):
    return models.Delivery.objects.all();

def resolve_delivery( info, **kwargs):
    id = kwargs.get('id')

    if id is not None:
        return models.Delivery.objects.get(pk=id)

    return None
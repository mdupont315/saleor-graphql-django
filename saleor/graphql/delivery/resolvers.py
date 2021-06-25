import graphene 

from graphene_django import DjangoObjectType
from ...delivery import models

def resolve_deliveries(self, info, **kwargs):
    return models.Delivery.objects.all();

def resolve_delivery(self, info, **kwargs):
    id = kwargs.get('id')

    return models.Delivery.objects.get(pk=id)
from graphene_django import DjangoObjectType
from ...delivery import models

class Delivery(DjangoObjectType):
    class Meta:
        model = models.Delivery
        field = '__all__'
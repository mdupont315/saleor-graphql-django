import graphene
from ...servicetime import models

def resolve_service_time(self, info, **kwargs):
    return models.ServiceTime.objects.all()


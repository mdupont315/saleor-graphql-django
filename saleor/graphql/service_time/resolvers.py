import graphene
from ...service_time import models

def resolve_service_time(info, **_kwargs):
    return models.ServiceTime.objects.all()


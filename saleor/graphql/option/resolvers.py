import graphene
from graphql_relay.node.node import from_global_id
from ...product import models

def resolve_options(self, info, **kwargs):
    return models.Option.objects.all()

def resolve_option(self, info, id):
    _type , _pk = from_global_id(id)
    return models.Option.objects.prefetch_related().get(pk=_pk)

def resolve_option_values(self, info, id):
    _type , _pk = from_global_id(id)
    option = models.Option.objects.get(pk=_pk)
    if(option):
        return models.OptionValue.objects.prefetch_related().get(option=option)
    return []
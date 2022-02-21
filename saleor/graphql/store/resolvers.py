import graphene
from graphql_relay.node.node import from_global_id

from ...store import models
from ..core.validators import validate_one_of_args_is_in_query
from .types import Store
from ...account.models import User
from django.core.exceptions import BadRequest


def resolve_user_store(info, store_id, slug=None):
    _type, store_pk = graphene.Node.from_global_id(store_id)
    user = User.objects.filter(store_id=store_pk).first()
    return user

def resolve_store(info, global_page_id=None, slug=None):
    validate_one_of_args_is_in_query("id", global_page_id, "slug", slug)
    user = info.context.user

    if slug is not None:
        store = models.Store.objects.visible_to_user(user).filter(slug=slug).first()
    else:
        _type, store_pk = graphene.Node.from_global_id(global_page_id)
        store = models.Store.objects.all().filter(pk=store_pk).first()
    return store


def resolve_stores(info, **_kwargs):
    return models.Store.objects.all()

def resolve_my_store(info, **_kwargs):
    return models.Store.objects.all().first()

def resolve_custom_domains(info, **_kwargs):
    return models.CustomDomain.objects.all()

def resolve_custom_domain(info, id, **_kwargs):
    _type , _pk = from_global_id(id)
    domain = models.CustomDomain.objects.filter(id=_pk).first()
    if not domain:
        raise BadRequest("domain doesn't exists")
    return domain

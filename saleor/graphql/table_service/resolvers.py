from graphql_relay.node.node import from_global_id
from ...table_service import models, error_codes
from django.core.exceptions import BadRequest, ValidationError

def resolve_table_services(info, **_kwargs):
    return models.TableService.objects.all()

def resolve_table_service(info, id, **_kwargs):
    _type , _pk = from_global_id(id)
    table = models.TableService.objects.filter(id=_pk).first()
    if not table:
        raise BadRequest(
                "QR code doesn't exists"
            )
    return table

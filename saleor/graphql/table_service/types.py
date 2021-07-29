import graphene
from ...table_service import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata

class TableService(CountableDjangoObjectType):
    
    class Meta:
        description = (
            "Service time config"
        )
        only_fields = [
            "table_name",
            "table_qr_code",
            "id",
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.TableService
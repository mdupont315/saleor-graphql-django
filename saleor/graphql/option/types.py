import graphene
from ...product import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata

class Option(CountableDjangoObjectType):
    name = graphene.String(description="Name")
    type = graphene.String(description="Type")
    required = graphene.Boolean(description="required")
    description = graphene.String(description="Description")

    class Meta:
        description = (
            "Option"
        )
        only_fields = [
            "name",
            "type",
            "required",
            "description",
            "id",
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.Option
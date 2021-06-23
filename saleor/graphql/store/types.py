import graphene

from ...store import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata
from ..core.types import Image

class Store(CountableDjangoObjectType):
    name = graphene.String(
        description="The store name.",
        required=True,
    )
    domain = graphene.String(
        description="The store description.",
    )
    logo = graphene.Field(Image, size=graphene.Int(description="Logo of store."))
    cover_photo = graphene.Field(Image, size=graphene.Int(description="Background of store."))

    class Meta:
        description = (
            "A static page that can be manually added by a shop operator through the "
            "dashboard."
        )
        only_fields = [
            "name",
            "domain",
            "logo",
            "cover_photo",
            "id",
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.Store
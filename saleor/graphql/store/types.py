import graphene

from ...store import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata
from ..core.types import Image

class Store(CountableDjangoObjectType):
    name = graphene.String(
        description="The store name.",
        required=False,
    )
    domain = graphene.String(
        description="The store description.",
        required=False
    )
    logo = graphene.Field(Image, size=graphene.Int(description="Logo of store."), required=False)
    cover_photo = graphene.Field(Image, size=graphene.Int(description="Background of store."), required=False)

    #Emergency setting feature
    webshop_status = graphene.DateTime(
        description="Webshop status setting.",
        required=False
    )
    delivery_status = graphene.DateTime(
        description="Delivery status setting.",
        required=False
    )
    pickup_status =graphene.DateTime(
        description="Pickup status setting.",
        required=False
    )

    #New order notifications
    email_notifications = graphene.Boolean(description="Enable notification", required=False)
    email_address = graphene.String(description="Email for notification", required=False)

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
            "webshop_status",
            "delivery_status",
            "pickup_status",
            "email_notifications",
            "email_address",
            "id",
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.Store
    
    @staticmethod
    def resolve_logo(root: models.Store, info, size=None, **_kwargs):
        if root.logo:
            return Image.get_adjusted(
                image=root.logo,
                alt=None,
                size=size,
                rendition_key_set="store_logo",
                info=info,
            )
    
    @staticmethod
    def resolve_cover_photo(root: models.Store, info, size=None, **_kwargs):
        if root.cover_photo:
            return Image.get_adjusted(
                image=root.cover_photo,
                alt=None,
                size=size,
                rendition_key_set="store_cover_photo",
                info=info,
            )
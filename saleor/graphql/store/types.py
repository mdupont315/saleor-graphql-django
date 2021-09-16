import graphene

from ...store import models
from ..core.connection import CountableDjangoObjectType
from ..core.types import Image
from ..meta.types import ObjectWithMetadata


class Store(CountableDjangoObjectType):
    name = graphene.String(
        description="The store name.",
        required=False,
    )
    domain = graphene.String(
        description="The store description.",
        required=False
    )
    logo = graphene.Field(Image, size=graphene.Int(
        description="Logo of store."), required=False)
    favicon = graphene.Field(Image, size=graphene.Int(
        description="Logo of store."), required=False)
    cover_photo = graphene.Field(Image, size=graphene.Int(
        description="Background of store."), required=False)
    phone = graphene.String(
        description="phone of store.",
        required=False)
    address = graphene.String(
        description="phone of store.",
        required=False)

    # Emergency setting feature
    webshop_status = graphene.DateTime(
        description="Webshop status setting.",
        required=False
    )
    delivery_status = graphene.DateTime(
        description="Delivery status setting.",
        required=False
    )
    pickup_status = graphene.DateTime(
        description="Pickup status setting.",
        required=False
    )
    table_service_status = graphene.DateTime(
        description="Pickup status setting.",
        required=False
    )

    # New order notifications
    email_notifications = graphene.Boolean(
        description="Enable notification", required=False)
    email_address = graphene.String(
        description="Email for notification", required=False)

    # New order notifications
    enable_transaction_fee = graphene.Boolean(
        description="Enable for all fee", required=False)
    contant_enable = graphene.Boolean(
        description="Enable transaction cost for contant", required=False)
    contant_cost = graphene.Float(
        description="Transaction cost for contant", required=False)
    stripe_enable = graphene.Boolean(
        description="Enable transaction cost for stripe", required=False)
    stripe_cost = graphene.Float(
        description="Transaction cost for stripe", required=False)
    #Index payment methods
    index_cash = graphene.Int(description="Index cash", required=False)
    index_stripe = graphene.Int(description="Index stripe", required=False)

    class Meta:
        description = (
            "A static page that can be manually added by a shop operator through the "
            "dashboard."
        )
        only_fields = [
            "name",
            "domain",
            "logo",
            "favicon",
            "cover_photo",
            "phone",
            "address",
            "postal_code",
            "city",
            "webshop_status",
            "delivery_status",
            "pickup_status",
            "table_service_status",
            "email_notifications",
            "email_address",
            "contant_enable",
            "contant_cost",
            "stripe_enable",
            "stripe_cost",
            "index_cash",
            "index_stripe",
            "enable_transaction_fee",
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
    def resolve_favicon(root: models.Store, info, size=None, **_kwargs):
        if root.favicon:
            return Image.get_adjusted(
                image=root.favicon,
                alt=None,
                size=size,
                rendition_key_set="store_favicon",
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

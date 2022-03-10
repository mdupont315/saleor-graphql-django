import graphene
from django_prices.models import MoneyField

from saleor.core.tracing import traced_resolver
from saleor.graphql.channel.types import Channel

from ...product import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata


class OptionValueChannelListing(CountableDjangoObjectType):
    price = MoneyField(description="Price")
    channel = graphene.Field(
        type=Channel
    )
    class Meta:
        description = (
            "OptionValueChannelListing"
        )
        only_fields = [
            "channel",
            "price",
            "id",
        ]
        interfaces = [graphene.relay.Node]
        model = models.OptionValueChannelListing

class OptionValue(CountableDjangoObjectType):
    name = graphene.String(description="Name")
    channel_listing = graphene.List(
        OptionValueChannelListing,
        description="The main thumbnail for a product.",
    )
    class Meta:
        description = (
            "OptionValue"
        )
        only_fields = [
            "option",
            "name",
            "id",
            "sort_order"
        ]
        interfaces = [graphene.relay.Node]
        model = models.OptionValue
    
    @staticmethod
    @traced_resolver
    def resolve_channel_listing(root: models.OptionValue, info, **_kwargs):
        return root.option_value_channels.all()

class Option(CountableDjangoObjectType):
    name = graphene.String(description="Name")
    type = graphene.String(description="Type")
    required = graphene.Boolean(description="required")
    description = graphene.String(description="Description")
    option_values = graphene.List(
        OptionValue,
        description="The main thumbnail for a product.",
    )

    class Meta:
        description = (
            "Option"
        )
        only_fields = [
            "option_values",
            "name",
            "type",
            "required",
            "description",
            "id",
            "sort_order",
            "max_options",
            "enable",
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.Option

    @staticmethod
    @traced_resolver
    def resolve_option_values(root: models.Option, info, **_kwargs):
        return root.option_values.all()

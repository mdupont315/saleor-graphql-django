from saleor.graphql.channel.types import Channel
from saleor.graphql.core.fields import ChannelContextFilterConnectionField
import graphene
from ...product import models
from ..core.connection import CountableDjangoObjectType
from ..meta.types import ObjectWithMetadata

class OptionValueChannelListing(CountableDjangoObjectType):
    price = graphene.Float(description="Price")
    # channel = graphene.Field(
    #     type=Channel
    # )
    class Meta:
        description = (
            "OptionValueChannelListing"
        )
        only_fields = [
            "price",
            "id",
        ]
        interfaces = [graphene.relay.Node]
        model = models.OptionValueChannelListing

class OptionValue(CountableDjangoObjectType):
    name = graphene.String(description="Name")
    # option_value_channels = graphene.List(
    #     OptionValueChannelListing,
    #     description="List of OptionValueChannel.",
    # )

    class Meta:
        description = (
            "OptionValue"
        )
        only_fields = [
            "name",
            "id",
        ]
        interfaces = [graphene.relay.Node]
        model = models.OptionValue

class Option(CountableDjangoObjectType):
    name = graphene.String(description="Name")
    type = graphene.String(description="Type")
    required = graphene.Boolean(description="required")
    description = graphene.String(description="Description")
    option_values = graphene.List(
        graphene.NonNull(OptionValue),
        description="The main thumbnail for a product.",
    )

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
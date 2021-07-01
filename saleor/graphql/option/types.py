from saleor.core.tracing import traced_resolver
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

    class Meta:
        description = (
            "OptionValue"
        )
        only_fields = [
            "option",
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
        ]
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.Option
    
    @staticmethod
    @traced_resolver
    def resolve_option_values(root: models.Option, info, **_kwargs):
        return root.option_values.all()
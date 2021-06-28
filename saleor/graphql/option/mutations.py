from graphql_relay.node.node import from_global_id
from .types import Option
import graphene
from ..core.mutations import ModelMutation
from ...product import models
from ...core.permissions import ProductPermissions
from ..core.types.common import OptionError
from ...channel import models as channel_models


class OptionValue(graphene.InputObjectType):
    channel_id = graphene.String(required=True, description="Channel")
    price = graphene.Float(required=True, description="Channel")

class OptionCreateInput(graphene.InputObjectType):
    name = graphene.String(required=True, description="Name")
    values = graphene.List(
        OptionValue, description="Values"
    )
    required = graphene.Boolean(description="Required")
    type = graphene.String(required=True, description="Type")

class OptionCreate(ModelMutation):
    option = graphene.Field(Option, description="The created attribute.")

    class Arguments:
        input = OptionCreateInput(
            required=True, description="Fields required to create an attribute."
        )
    
    class Meta:
        description = "Create option for product."
        model = models.Option
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_errors"
    
    def create_option_value(value, option_id):
        option_value = models.ProductOptionValue()
        option_value.price = value["price"]
        _type , _pk = from_global_id(value["channel_id"])
        option_value.channel = channel_models.Channel.objects.get(pk = _pk)
        option_value.option = models.Option.objects.get(pk = option_id)
        option_value.save()

    @classmethod
    def perform_mutation(cls, root, info, **data):
        option = super().perform_mutation(root, info, **data)

        if(data["input"]["values"]):
            for value in data["input"]["values"]:
                cls.create_option_value(value, option.option.id)
            
        return option
from graphql_relay.node.node import from_global_id
from .types import Option
import graphene
from ..core.mutations import ModelDeleteMutation, ModelMutation
from ...product import models
from ...core.permissions import ProductPermissions
from ..core.types.common import OptionError
from ...channel import models as channel_models


class OptionValueChannelInput(graphene.InputObjectType):
    channel_id = graphene.String(required=True, description="Channel")
    price = graphene.Float(required=True, description="Channel")

class OptionValueInput(graphene.InputObjectType):
    name = graphene.String(required=True, description="Name")
    channel_listing = graphene.List(
        OptionValueChannelInput, description="channel_listing"
    )

class OptionCreateInput(graphene.InputObjectType):
    name = graphene.String(required=True, description="Name")
    values = graphene.List(
        OptionValueInput, description="Values"
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

    @classmethod
    def create_option_value_channel(cls, value, option_value_id):
        option_value_channel = models.OptionValueChannelListing()
        option_value_channel.price = value["price"]
        _type , _pk = from_global_id(value["channel_id"])
        option_value_channel.channel = channel_models.Channel.objects.get(pk = _pk)
        option_value_channel.option_value = models.OptionValue.objects.get(pk = option_value_id)
        option_value_channel.save()
    
    @classmethod
    def create_option_value(cls, value, option_id):
        option_value = models.OptionValue()
        option_value.name = value["name"]
        option_value.option = models.Option.objects.get(pk = option_id)
        option_value.save()
        channel_listing = value["channel_listing"]
        if(channel_listing):
            for channel in channel_listing:
                cls.create_option_value_channel(channel, option_value.id)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        option = super().perform_mutation(root, info, **data)

        if(data["input"]["values"]):
            for value in data["input"]["values"]:
                cls.create_option_value(value, option.option.id)
            
        return option

class OptionUpdateInput(graphene.InputObjectType):
    name = graphene.String(required=True, description="Name")
    add_values = graphene.List(
        OptionValueInput, description="Values"
    )
    delete_values = graphene.List(
        graphene.ID,
        name="removeValues",
        description="IDs of values to be removed.",
    )
    required = graphene.Boolean(description="Required")
    type = graphene.String(required=True, description="Type")


class OptionUpdate(ModelMutation):
    option = graphene.Field(Option, description="The created attribute.")

    class Arguments:
        id = graphene.ID(required=True, description="ID of a option to update.")
        input = OptionUpdateInput(
            required=True, description="Fields required to create an attribute."
        )
    
    class Meta:
        description = "Create option for product."
        model = models.Option
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_errors"
    
    def create_option_value_channel(value, option_value_id):
        option_value_channel = models.OptionValueChannelListing()
        option_value_channel.price = value["price"]
        _type , _pk = from_global_id(value["channel_id"])
        option_value_channel.channel = channel_models.Channel.objects.get(pk = _pk)
        option_value_channel.option_value = models.OptionValue.objects.get(pk = option_value_id)
        option_value_channel.save()
    
    @classmethod
    def create_option_value(cls, value, option_id):
        option_value = models.OptionValue()
        option_value.name = value["name"]
        _type , _pk = from_global_id(option_id)
        option_value.option = models.Option.objects.get(pk = _pk)
        option_value.save()
        channel_listing = value["channel_listing"]
        if(channel_listing):
            for channel in channel_listing:
                cls.create_option_value_channel(channel, option_value.id)
    
    def delete_option_value(option_id):
        _type , _pk = from_global_id(option_id)
        option_value = models.ProductOptionValue.objects.get(pk=_pk)
        if(option_value):
            option_value.delete()


    @classmethod
    def perform_mutation(cls, root, info, **data):
        option = super().perform_mutation(root, info, **data)

        add_values = data["input"].get("add_values") or []

        if(add_values):
            for value in add_values:
                cls.create_option_value(value, data["id"])


        delete_values = data["input"].get("delete_values") or []
        if(delete_values):
            for value in delete_values:
                cls.delete_option_value(value["id"])
            
        return option

class OptionDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of an option to delete.")

    class Meta:
        description = "Create option for product."
        model = models.Option
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_errors"

class OptionValueChannelUpdateInput(OptionValueChannelInput):
    id = graphene.ID(required=True, description="ID of an option to update.")

class UpdateOptionValueInput(graphene.InputObjectType):
    name = graphene.String(required=True, description="Name")
    channel_listing_update = graphene.List(
        OptionValueChannelUpdateInput, description="channel_listing"
    )
class UpdateOptionValue(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of an option to update.")
        input = UpdateOptionValueInput(
            required=True, description=""
        )

    class Meta:
        description = "Create option for product."
        model = models.OptionValue
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_errors"


    def create_option_value_channel(value, option_value_id):
        option_value_channel = models.OptionValueChannelListing()
        option_value_channel.price = value["price"]
        _type , _pk = from_global_id(value["channel_id"])
        option_value_channel.channel = channel_models.Channel.objects.get(pk = _pk)
        option_value_channel.option_value = models.OptionValue.objects.get(pk = option_value_id)
        option_value_channel.save()

    @classmethod
    def update_option_value_channel(cls, channel, option_value_id):
        if channel["channel_id"]:
            _type , _pk = from_global_id(channel["id"])
            option_value_channel = models.OptionValueChannelListing.objects.get(pk=_pk)
            option_value_channel.price = channel["price"]
            option_value_channel.save()
        else:
            cls.create_option_value_channel(channel, option_value_id)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        option_value = super().perform_mutation(root, info, **data)
        channel_listing_update = data["input"]["channel_listing_update"]
        if(channel_listing_update):
            for channel in channel_listing_update:
                cls.update_option_value_channel(channel, option_value.option_value.id)
            
        return option_value
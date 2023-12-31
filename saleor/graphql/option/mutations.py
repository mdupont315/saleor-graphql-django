from optparse import OptionValueError
import graphene
from graphql_relay.node.node import from_global_id
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.core.enums import CollectionErrorCode

from saleor.graphql.core.scalars import Decimal
from saleor.graphql.core.utils import from_global_id_or_error
from saleor.graphql.core.utils.reordering import perform_reordering

from ...channel import models as channel_models
from ...core.permissions import ProductPermissions
from ...product import models
from ..core.mutations import (BaseMutation, ModelBulkDeleteMutation, ModelDeleteMutation,
                              ModelMutation)
from ..core.types.common import OptionError
from .types import Option, OptionValue
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class OptionValueChannelInput(graphene.InputObjectType):
    channel_id = graphene.String(required=True, description="Channel")
    price = Decimal(required=True, description="Channel")
    currency = graphene.String(required=True, description="currency")


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
    max_options = graphene.Int(description="Max multiple options")
    enable = graphene.Boolean(description="Enable")


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
        option_value_channel.price_amount = value["price"]
        option_value_channel.currency = value["currency"]
        _type, _pk = from_global_id(value["channel_id"])
        option_value_channel.channel = channel_models.Channel.objects.get(pk=_pk)
        option_value_channel.option_value = models.OptionValue.objects.get(
            pk=option_value_id)
        option_value_channel.save()

    @classmethod
    def create_option_value(cls, value, option_id):
        option_value = models.OptionValue()
        option_value.name = value["name"]
        option_value.option = models.Option.objects.get(pk=option_id)
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
    name = graphene.String(required=False, description="Name")
    add_values = graphene.List(
        OptionValueInput, description="Values"
    )
    delete_values = graphene.List(
        graphene.ID,
        name="removeValues",
        description="IDs of values to be removed.",
    )
    required = graphene.Boolean(description="Required")
    type = graphene.String(required=False, description="Type")
    max_options = graphene.Int(description="Max multiple options")
    enable = graphene.Boolean(description="Enable")


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

    @classmethod
    def create_option_value_channel(cls, value, option_value_id):
        option_value_channel = models.OptionValueChannelListing()
        option_value_channel.price_amount = value["price"]
        option_value_channel.currency = value["currency"]
        _type, _pk = from_global_id(value["channel_id"])
        option_value_channel.channel = channel_models.Channel.objects.get(pk=_pk)
        option_value_channel.option_value = models.OptionValue.objects.get(
            pk=option_value_id)
        option_value_channel.save()

    @classmethod
    def create_option_value(cls, value, option_id):
        option_value = models.OptionValue()
        option_value.name = value["name"]
        _type, _pk = from_global_id(option_id)
        option_value.option = models.Option.objects.get(pk=_pk)
        option_value.save()
        channel_listing = value["channel_listing"]
        if(channel_listing):
            for channel in channel_listing:
                cls.create_option_value_channel(channel, option_value.id)

    def delete_option_value(option_id):
        _type, _pk = from_global_id(option_id)
        option_value = models.OptionValue.objects.get(pk=_pk)
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
                cls.delete_option_value(value)

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
        option_value_channel.price_amount = value["price"]
        _type, _pk = from_global_id(value["channel_id"])
        option_value_channel.channel = channel_models.Channel.objects.get(pk=_pk)
        option_value_channel.option_value = models.OptionValue.objects.get(
            pk=option_value_id)
        option_value_channel.save()

    @classmethod
    def update_option_value_channel(cls, channel, option_value_id):
        if channel["channel_id"]:
            _type, _pk = from_global_id(channel["id"])
            option_value_channel = models.OptionValueChannelListing.objects.get(pk=_pk)
            option_value_channel.price_amount = channel["price"]
            option_value_channel.save()
        else:
            cls.create_option_value_channel(channel, option_value_id)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        option_value = super().perform_mutation(root, info, **data)
        channel_listing_update = data["input"]["channel_listing_update"]
        if(channel_listing_update):
            for channel in channel_listing_update:
                cls.update_option_value_channel(channel, option_value.optionValue.id)

        return option_value


class DeleteBulkOptionValue(ModelBulkDeleteMutation):
    class Arguments:
        ids = graphene.List(
            graphene.ID,
            required=True,
            description="List of option value IDs to delete."
        )

    class Meta:
        description = "Deletes list of option values."
        model = models.OptionValue
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_errors"
class MoveOptionInput(graphene.InputObjectType):
    option_id = graphene.ID(
        description="The ID of the option to move.", required=True
    )
    sort_order = graphene.Int(
        description=(
            "The relative sorting position of the product (from -inf to +inf) "
            "starting from the first given product's actual position."
            "1 moves the item one position forward, -1 moves the item one position "
            "backward, 0 leaves the item unchanged."
        )
    )

class MoveOptionValueInput(graphene.InputObjectType):
    option_value_id = graphene.ID(
        description="The ID of the option value to move.", required=True
    )
    sort_order = graphene.Int(
        description=(
            "The relative sorting position of the option value (from -inf to +inf) "
            "starting from the first given option value's actual position."
            "1 moves the item one position forward, -1 moves the item one position "
            "backward, 0 leaves the item unchanged."
        )
    )
class ReorderOptions(BaseMutation):
    # products = graphene.Field(Product, description="Related checkout object.")
    class Meta:
        description = "Reorder the products of a collection."
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_errors"

    class Arguments:
        moves = graphene.List(
            MoveOptionInput,
            required=True,
            description="The products position operations.",
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        moves = data["moves"]
        operations = {}
        products = models.Option.objects.all()

        for move_info in moves:
            product_pk = cls.get_global_id_or_error(
                move_info.option_id, only_type=Option, field="moves"
            )
            try:
                m2m_info = products.get(pk=int(product_pk))
            except ObjectDoesNotExist:
                raise ValidationError(
                    {
                        "moves": ValidationError(
                            f"Couldn't resolve to a product: {move_info.option_id}",
                            code=CollectionErrorCode.NOT_FOUND.value,
                        )
                    }
                )
            operations[m2m_info.pk] = move_info.sort_order

        with traced_atomic_transaction():
            perform_reordering(products, operations)
        # product=ChannelContext(node=product, channel_slug=None)
        # print(product, "-----------------move")

        return ReorderOptions()

class ReorderOptionValues(BaseMutation):
    # products = graphene.Field(Product, description="Related checkout object.")
    class Meta:
        description = "Reorder the values of a option."
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = OptionError
        error_type_field = "option_value_errors"

    class Arguments:
        option_id = graphene.ID(required=True, description="The option id.")
        moves = graphene.List(
            MoveOptionValueInput,
            required=True,
            description="The option value position operations.",
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        moves = data["moves"]
        option_id = data["option_id"]
        _type, _pk = from_global_id(option_id)
        operations = {}
        products = models.OptionValue.objects.all().filter(option_id=_pk)

        for move_info in moves:
            product_pk = cls.get_global_id_or_error(
                move_info.option_value_id, only_type=OptionValue, field="moves"
            )
            try:
                m2m_info = products.get(pk=int(product_pk))
            except ObjectDoesNotExist:
                raise ValidationError(
                    {
                        "moves": ValidationError(
                            f"Couldn't resolve to a product: {move_info.option_value_id}",
                            code=CollectionErrorCode.NOT_FOUND.value,
                        )
                    }
                )
            operations[m2m_info.pk] = move_info.sort_order

        with traced_atomic_transaction():
            perform_reordering(products, operations)
        # product=ChannelContext(node=product, channel_slug=None)
        # print(product, "-----------------move")

        return ReorderOptionValues()
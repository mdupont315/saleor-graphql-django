import graphene 
from ....delivery import models
from ...core.types.common import DeliveryError
from ...core.mutations import  ModelMutation
from ..types import Delivery
from saleor.graphql.core.scalars import Decimal
from ...core.scalars import PositiveDecimal


class DeliveryInput(graphene.InputObjectType):
    delivery_area = graphene.JSONString(
        required=True, 
        description="Delivery area."
    )
    delivery_fee = PositiveDecimal(description="Cost price of the variant in channel.")
    from_delivery = PositiveDecimal(description="Cost price of the variant in channel.")
    min_order = PositiveDecimal(description="Cost price of the variant in channel.")
    enable_for_big_order = graphene.Boolean(
        required=False, 
        description="Enable for big order."
    )
    enable_minimum_delivery_order_value  = graphene.Boolean(
        required=False, 
        description="Custom min order."
    )

class DeliveryCreate(ModelMutation):
    class Arguments:
        input = DeliveryInput(
            required=True, 
            description="Fields required to create delivery setting."
        )
    
    class Meta:
        description = "Creates a new delivery."
        model = models.Delivery
        error_type_class = DeliveryError
        error_type_field = "delivery_errors"

class DeliveryUpdateInput(graphene.InputObjectType):
    delivery_area = graphene.JSONString(
        required=False, 
        description="Delivery area."
    )
    delivery_fee = PositiveDecimal(description="Cost price of the variant in channel.")
    from_delivery = PositiveDecimal(description="Cost price of the variant in channel.")
    min_order = PositiveDecimal(description="Cost price of the variant in channel.")
    enable_for_big_order = graphene.Boolean(
        required=False, 
        description="Min order value."
    )
    enable_custom_delivery_fee = graphene.Boolean(
        required=False, 
        description="Custom delivery fee."
    )
    enable_minimum_delivery_order_value  = graphene.Boolean(
        required=False, 
        description="Custom min order."
    )

class DeliveryUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True,description="ID of a delivery to update.")
        input = DeliveryUpdateInput(
            required=True, description="Fields required to update a delivery."
        )

    class Meta:
        description = "Updates a delivery."
        model = models.Delivery
        error_type_class = DeliveryError
        error_type_field = "delivery_errors"
    
    # delivery = graphene.Field(Delivery)
    # @staticmethod
    # def mutate(root,info,id,input=None):
    #     delivery_instance = models.Delivery.objects.get(pk=id)
    #     if delivery_instance:
    #         delivery_instance.delivery_area = input.delivery_area
    #         delivery_instance.delivery_fee = input.delivery_fee
    #         delivery_instance.from_delivery = input.from_delivery
    #         delivery_instance.min_order = input.min_order
    #         delivery_instance.save()
            
    #         return DeliveryUpdate(delivery=delivery_instance)
        
    #     return DeliveryUpdate(delivery=None)

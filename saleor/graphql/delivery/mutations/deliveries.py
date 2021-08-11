import graphene 
from ....delivery import models
from ...core.types.common import DeliveryError
from ...core.mutations import  ModelMutation
from ..types import Delivery


class DeliveryInput(graphene.InputObjectType):
    delivery_area = graphene.JSONString(
        required=True, 
        description="Delivery area."
    )
    delivery_fee = graphene.Float(
        required=True, 
        description="Delivery fee."
    )
    from_delivery = graphene.Float(
        required=True, 
        description="Free delivery from."
    )
    min_order = graphene.Float(
        required=True, 
        description="Min order value."
    )
    enable_for_big_order = graphene.Boolean(
        required=False, 
        description="Enable for big order."
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
    delivery_fee = graphene.Float(
        required=False, 
        description="Delivery fee."
    )
    from_delivery = graphene.Float(
        required=False, 
        description="Free delivery from."
    )
    min_order = graphene.Float(
        required=False, 
        description="Min order value."
    )
    enable_for_big_order = graphene.Float(
        required=False, 
        description="Min order value."
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

import graphene 
from graphene_django import DjangoObjectType

from ....delivery import models
from ..types import Delivery
from ...core.types.common import DeliveryError
from ...core.mutations import  ModelMutation


class DeliveryInput(graphene.InputObjectType):
    delivery_area = graphene.String()
    delivery_fee = graphene.Float()
    from_delivery = graphene.Float()
    min_order = graphene.Float()

class CreateDelivery(ModelMutation):
    class Argument:
        input = DeliveryInput(required=True)

    delivery = graphene.Field(Delivery)

    @staticmethod
    def mutate(root, info, input=None):
        delivery_instance = models.Delivery(
            delivery_area = input.delivery_area,
            delivery_fee = input.delivery_fee,
            from_delivery = input.free_delivery,
            min_order = input.min_order
        )
        delivery_instance.save()

        return DeliveryCreate(delivery=delivery_instance)

    class Meta:
        description = "Creates a new delivery."
        model = models.Delivery
        error_type_class = DeliveryError
        error_type_field = "delivery_errors"

class UpdateDelivery(ModelMutation):
    class Argument:
        input = DeliveryInput(required=True)

    delivery = graphene.Field(Delivery)

    @staticmethod
    def mutate(root, info, input=None):
        delivery_instance = models.Delivery.objects.get(pk=input.id)

        if delivery_instance:
            delivery_instance.delivery_area = input.delivery_area
            delivery_instance.delivery_fee = input.delivery_fee
            delivery_instance.from_delivery = input.from_delivery
            delivery_instance.min_order = input.min_order
            delivery_instance.save()

            return DeliveryUpdate(delivery=delivery_instance)
        
        return DeliveryUpdate(delivery=None)   

    class Meta:
        description = "Updates a delivery."
        model = models.Delivery
        error_type_class = DeliveryError
        error_type_field = "dilivery_errors"

# class DeliveryDelete(graphene.Mutation):
#     class Argument:
#         id = graphene.ID()

#     delivery =graphene.Field(Delivery)

#     @staticmethod
#     def mutation(root, info, id):
#         delivery_instance = models.Delivery.objects.get(pk=id)
#         delivery_instance.delete()

#         return None
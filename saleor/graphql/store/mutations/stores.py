from collections import defaultdict
from datetime import date
from logging import fatal

import graphene
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from saleor.account.models import User
from saleor.delivery.models import Delivery
from saleor.graphql.utils.validators import check_super_user
from saleor.servicetime.models import ServiceTime
from saleor.store.error_codes import StoreErrorCode

from ....account.error_codes import AccountErrorCode
from ....core.exceptions import PermissionDenied
from ....core.permissions import StorePermissions, get_permissions_default
from ....core.utils.url import validate_storefront_url
from ....store import models
from ....store.utils import delete_stores
from ...core.mutations import ModelDeleteMutation, ModelMutation
from ...core.types import Upload
from ...core.types.common import StoreError
from ..types import Store


class StoreInput(graphene.InputObjectType):
    name = graphene.String(description="Store name.")
    domain = graphene.String(description="Store domain.")
    email = graphene.String(description="The email address of the user.", required=True)
    password = graphene.String(description="Password.", required=True)


class StoreCreate(ModelMutation):
    class Arguments:
        input = StoreInput(
            required=True, description="Fields required to create a store."
        )

    class Meta:
        description = "Creates a new store."
        model = models.Store
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)

        # Validate for create user
        if not settings.ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL:
            return cleaned_input
        elif not data.get("redirect_url"):
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        "This field is required.", code=AccountErrorCode.REQUIRED
                    )
                }
            )

        try:
            validate_storefront_url(data["redirect_url"])
        except ValidationError as error:
            raise ValidationError(
                {
                    "redirect_url": ValidationError(
                        error.message, code=AccountErrorCode.INVALID
                    )
                }
            )

        password = data["password"]
        try:
            password_validation.validate_password(password, instance)
        except ValidationError as error:
            raise ValidationError({"password": error})

        return cleaned_input

    def create_group_data(name, permissions, users):
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.add(*permissions)
        group.user_set.add(*users)
        return group

    @classmethod
    def perform_mutation(cls, root, info, **data):
        # check if is super user
        check_super_user(info.context)

        retval = super().perform_mutation(root, info, **data)

        # create user
        user = User()
        user.is_supplier = True
        user.store_id = retval.store.id
        user.email = data["input"]["email"]
        password = data["input"]["password"]
        user.set_password(password)
        user.save()

        permissions = get_permissions_default()
        for permission in permissions:
            base_name = permission.codename.split("_")[1:]
            group_name = " ".join(base_name)
            group_name += " management"
            group_name = group_name.capitalize()
            cls.create_group_data(group_name, [permission], [user])

        # create default service time
        delivery = Delivery()
        delivery.store_id = retval.store.id
        delivery.delivery_area = {"areas": []}
        delivery.save()

        # create default service time
        service_time = ServiceTime()
        service_time.store_id = retval.store.id

        service_time.dl_allow_preorder = False
        service_time.dl_as_soon_as_posible = False
        service_time.dl_delivery_time = 10
        service_time.dl_preorder_day = 1
        service_time.dl_same_day_order = False
        service_time.dl_service_time = {"dl": [{"days": [
            False, False, False, False, False, False, False], "open":"00:05", "close":"23:55"}]}
        # service_time.dl_service_time = None
        service_time.dl_time_gap = 10

        service_time.pu_allow_preorder = False
        service_time.pu_as_soon_as_posible = False
        service_time.pu_delivery_time = 10
        service_time.pu_preorder_day = 1
        service_time.pu_same_day_order = False
        service_time.pu_service_time = {"pu": [{"days": [
            False, False, False, False, False, False, False], "open":"00:05", "close":"23:55"}]}
        # service_time.pu_service_time = None
        service_time.pu_time_gap = 10

        service_time.table_service_time = {"tb": [{"days": [
            False, False, False, False, False, False, False], "open":"00:05", "close":"23:55"}]}

        service_time.save()
        return retval


class StoreUpdateInput(graphene.InputObjectType):
    name = graphene.String(description="Store name.")
    domain = graphene.String(description="Store domain")
    address = graphene.String(description="Store address.")
    phone = graphene.String(description="Store phone.")
    postal_code = graphene.String(description="postal code.")
    city = graphene.String(description="city of strore.")
    logo = Upload(description="Logo image file.")
    favicon = Upload(description="Logo image file.")
    cover_photo = Upload(description="Cover photo image file.")
  
    # Emergency setting feature
    webshop_status = graphene.DateTime(
        description="Webshop status setting."
    )
    delivery_status = graphene.DateTime(
        description="Delivery status setting."
    )
    pickup_status = graphene.DateTime(
        description="Pickup status setting."
    )
    table_service_status = graphene.DateTime(
        description="Pickup status setting."
    )

    # New order notifications
    email_notifications = graphene.Boolean(description="Enable notification")
    email_address = graphene.String(description="Email for notification")
    pos_enable = graphene.Boolean(description="Enable POS")

    # Transaction cost
    enable_transaction_fee = graphene.Boolean(description="Enable transaction all fee")
    contant_enable = graphene.Boolean(description="Enable transaction cost for contant")
    contant_cost = graphene.Float(description="Transaction cost for contant")
    stripe_enable = graphene.Boolean(description="Enable transaction cost for stripe")
    stripe_cost = graphene.Float(description="Transaction cost for stripe")
    index_cash = graphene.Int(description="Index cash")
    index_stripe = graphene.Int(description="Index stripe")

class StoreUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a store to update.")
        input = StoreUpdateInput(
            required=True, description="Fields required to update a store."
        )

    class Meta:
        description = "Updates a store."
        model = models.Store
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"


class MyStoreUpdate(ModelMutation):
    class Arguments:
        input = StoreUpdateInput(
            required=True, description="Fields required to update a store."
        )

    class Meta:
        description = "Updates a store."
        model = models.Store
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

    @classmethod
    def perform_mutation(cls, root, info, **data):
        input = data.get("input")
        my_store = models.Store.objects.first()
        if my_store:
            for field_name, field_item in input._meta.fields.items():
                if field_name in input:
                    value = input[field_name]
                    setattr(my_store, field_name, value)
            my_store.save()
            return cls.success_response(my_store)
        raise ValidationError(
            {
                "store": ValidationError(
                    "Store does not exists.",
                    code=StoreErrorCode.NOT_EXISTS,
                )
            }
        )


class StoreDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a store to delete.")

    class Meta:
        description = "Deletes a store."
        model = models.Store
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        if not cls.check_permissions(info.context):
            raise PermissionDenied()
        # check if is super user
        check_super_user(info.context)
        node_id = data.get("id")
        instance = cls.get_node_or_error(info, node_id, only_type=Store)

        db_id = instance.id
        delete_stores([db_id])
        instance.id = db_id
        return cls.success_response(instance)

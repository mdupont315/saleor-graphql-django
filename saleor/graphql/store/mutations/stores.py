# from typing_extensions import Required
from django_multitenant.utils import unset_current_tenant
import graphene
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from collections import defaultdict
import os

from graphql_relay.node.node import from_global_id

from saleor.account.models import User
from saleor.delivery.models import Delivery
from saleor.graphql.notifications.schema import LiveNotification
from saleor.graphql.utils.validators import check_super_user
from saleor.route53 import check_exist_record,create_new_record, delete_record, update_record
from saleor.servicetime.models import ServiceTime
from saleor.store.error_codes import StoreErrorCode

from ....account.error_codes import AccountErrorCode
from ....core.exceptions import DomainIsExist, PermissionDenied
from ....core.permissions import StorePermissions, get_permissions_default
from ....core.utils.url import validate_storefront_url
from ....store import models
from ....store.utils import delete_stores, verify_ssl
from ...core.mutations import BaseBulkMutation, BaseMutation, ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ...core.types import Upload
from ...core.types.common import StoreError
from ..types import Store


class StoreInput(graphene.InputObjectType):
    name = graphene.String(description="Store name.")
    domain = graphene.String(description="Store domain.")
    email = graphene.String(description="The email address of the user.", required=True)
    password = graphene.String(description="Password.", required=True)
    postal_code = graphene.String(description="Postal code.")
    address = graphene.String(description="Address.")
    phone = graphene.String(description="Phone.")
    city = graphene.String(description="City.")
    description = graphene.String(description="Description.")

class TestInput(graphene.InputObjectType):
    text: graphene.String(description="Store name.")
class StoreCreate(ModelMutation):
    class Arguments:
        input = StoreInput(
            required=True, description="Fields required to create a store."
        )

    class Meta:
        description = "Creates a new store."
        model = models.Store
        # permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

    # @classmethod
    # def clean_instance(cls, info, instance):
    #     errors = defaultdict(list)
    #     cls.check_exist_domain(info, [instance], "domain", errors)
    #     if errors:
    #         raise ValidationError(errors)
    # @classmethod
    # def check_exist_domain(cls, info, instances, field, errors):
    #    pass

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        # Validate for create user
        

      
        password = data["password"]
        try:
            password_validation.validate_password(password, instance)
        except ValidationError as error:
            raise ValidationError({"password": error})
        
        try:     
            if check_exist_record(data["domain"]):
                raise DomainIsExist()
        except ValidationError as error:
            error.code = StoreErrorCode.ALREADY_EXISTS.value
            raise ValidationError({"domain": error})
        
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

        return cleaned_input

    def create_group_data(name, permissions, users):
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.add(*permissions)
        group.user_set.add(*users)
        return group

    @classmethod
    def perform_mutation(cls, root, info, **data):
        # check if is super user
        # check_super_user(info.context)
        unset_current_tenant()
        domain="{}.{}".format(data["input"]["domain"],os.environ.get('STATIC_DOMAIN'))
        index = 1;
        while True: 
            if not check_exist_record(domain):
                break
            data_domain = '{}-{}'.format(data["input"]["domain"],index)
            domain = '{}.{}'.format(data_domain,os.environ.get('STATIC_DOMAIN'))
            index = index+1

        data["input"]["domain"]=domain
        data["input"]["description"]='{} is open for online takeaway orders'.format(data["input"]["name"])
        retval = super().perform_mutation(root, info, **data)
        create_new_record(domain)
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
        # print("----3")

        # create default service time
        delivery = Delivery()
        delivery.store_id = retval.store.id
        delivery.delivery_area = {"areas": []}
        delivery.save()
        # print("----4")

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
        # print("----5")

        return retval

class TestSubscription(BaseMutation):
    class Arguments:
        text =graphene.String("Text string")

    class Meta:
        description = "Creates a new store."
        error_type_class = StoreError
        error_type_field = "store_errors"

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        text = data["text"]
        LiveNotification.new_message("store_id",text)
        super().perform_mutation(_root, info, **data)
        
        return TestSubscription()


class StoreUpdateInput(graphene.InputObjectType):
    name = graphene.String(description="Store name.")
    domain = graphene.String(description="Store domain")
    address = graphene.String(description="Store address.")
    description = graphene.String(description="Store description.")
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

    # Custom domain
    custom_domain_enable = graphene.Boolean(description="Enable custom domain")


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

    # @classmethod
    # def perform_mutation(cls, _root, info, **data):
    #     input = data.get("input")
    #     my_store = models.Store.objects.first()
    #     print(my_store.domain)
    #     if my_store:
    #         for field_name, field_item in input._meta.fields.items():
    #             if field_name in input:
    #                 value = input[field_name]
    #                 if field_name=="domain" and value != my_store.domain:
    #                     domain = '{}.{}'.format(value,os.environ.get('STATIC_DOMAIN'))
    #                     update_record(domain, my_store.domain)
    #                     setattr(my_store, "domain", domain)
    #                 setattr(my_store, field_name, value)   
    #         my_store.save()
    #         return cls.success_response(my_store)
    #     raise ValidationError(
    #         {
    #             "store": ValidationError(
    #                 "Store does not exists.",
    #                 code=StoreErrorCode.NOT_EXISTS,
    #             )
    #         }
    #     )

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
                    # print(field_name,"============",value)

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
        # domain = "{}.{}".format(instance.domain, os.environ.get('STATIC_DOMAIN'))
        db_id = instance.id
        delete_stores([db_id])
        if check_exist_record(instance.domain):
            delete_record(instance.domain)
        instance.id = db_id
        return cls.success_response(instance)


        
# api domain ==============================================================
class DomainCustomInput(graphene.InputObjectType):
    domain_custom = graphene.String(
        description="domain",
    )
    status = graphene.Boolean(
        description="status of domain",
    )

class MultipleDomainCustomInput(graphene.InputObjectType):
    domains = graphene.List(DomainCustomInput,
    required=True,)


class CustomDomainCreate(ModelMutation):
    class Arguments:
        input = DomainCustomInput(
            required=True, description="Fields required to create table service."
        )

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        # validate table name
        domain_custom = cleaned_input["domain_custom"]
        check_domain = models.CustomDomain.objects.filter(domain_custom=domain_custom).first()
        if check_domain:
            raise ValidationError(
                {
                    "domain_custom": ValidationError(
                        "domain already exists.",
                        code=StoreErrorCode.ALREADY_EXISTS,
                    )
                }
            )
        return cleaned_input
    @classmethod
    def perform_mutation(cls, _root, info, **data):
        # verify ssl here
        return super().perform_mutation(_root, info, **data)

    class Meta:
        description = "Creates domain."
        model = models.CustomDomain
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

class CustomDomainUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a table service to update.")
        input = DomainCustomInput(
            required=True, description="Fields required to table service time."
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        # validate table name
        input = data.get("input")
        domain_custom = input.get("domain_custom", None)
        if domain_custom:
            _type , current_domain_pk = from_global_id(data["id"])
            domain = models.CustomDomain.objects.filter(domain_custom=domain_custom).first()
            if domain and domain.id != int(current_domain_pk):
                raise ValidationError(
                    {
                        "domain_custom": ValidationError(
                            "domain already exists.",
                            code=StoreErrorCode.ALREADY_EXISTS,
                        )
                    }
                )
        return super().perform_mutation(_root, info, **data)
    
    class Meta:
        description = "Update domain."
        model = models.CustomDomain
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

class CustomDomainDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of an attribute to delete.")

    class Meta:
        description = "delete domain."
        model = models.CustomDomain
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

class CustomDomainBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = graphene.List(
            graphene.ID, required=True, description="List of attribute IDs to delete."
        )

    class Meta:
        description = "bulk delete store."
        model = models.CustomDomain
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"

class CustomDomainsVerifySSL(ModelMutation):
    class Arguments:
        input = MultipleDomainCustomInput(required=True, description="Fields required to table service time.")

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        # validate table name
        list_domain = data['input']['domains']
        for i in range(len(list_domain)):
            models.CustomDomain.objects.filter(domain_custom=data['input']['domains'][i]['domain_custom']).update(status=not verify_ssl(list_domain[i].domain_custom))
            
        return super().perform_mutation(_root, info, **data)

    class Meta:
        description = "verify domains."
        model = models.CustomDomain
        permissions = (StorePermissions.MANAGE_STORES,)
        error_type_class = StoreError
        error_type_field = "store_errors"
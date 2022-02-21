from typing import Union

from django.conf import settings
from django.db import models
from django.utils import timezone
from versatileimagefield.fields import VersatileImageField

from ..core.models import CustomQueryset, MultitenantModelWithMetadata
from ..core.permissions import StorePermissions
from ..core.utils.translations import TranslationProxy
from ..seo.models import SeoModel


class StoresQueryset(CustomQueryset):
    def visible_to_user(self, requestor: Union["User", "App"]):
        try:
            if requestor.is_superuser:
                return self.all()

            store_pk = requestor.store_id
            return self.filter(pk=store_pk)
        except:
            return None


class Store(MultitenantModelWithMetadata, SeoModel):
    tenant_id = 'id'
    name = models.CharField(max_length=256)
    domain = models.CharField(max_length=256)
    favicon = VersatileImageField(
        upload_to="store-media", blank=True, null=True
    )
    logo = VersatileImageField(
        upload_to="store-media", blank=True, null=True
    )
    cover_photo = VersatileImageField(
        upload_to="store-media", blank=True, null=True
    )
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    pos_enable = models.BooleanField(blank=True, null=True, default=False)
    custom_domain_enable = models.BooleanField(blank=True, null=True, default=False)
    description = models.TextField(blank=True,  null=True)

    # Emergency setting feature
    webshop_status = models.DateTimeField(blank=True, null=True)
    delivery_status = models.DateTimeField(blank=True, null=True)
    pickup_status = models.DateTimeField(blank=True, null=True)
    table_service_status = models.DateTimeField(blank=True, null=True)

    # New order notifications
    email_notifications = models.BooleanField(blank=True, null=True, default=False)
    email_address = models.EmailField(blank=True, null=True)

    # Transaction cost
    enable_transaction_fee = models.BooleanField(blank=True, null=True, default=False)
    contant_enable = models.BooleanField(blank=True, null=True, default=False)
    contant_cost = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    stripe_enable = models.BooleanField(blank=True, null=True, default=False)
    stripe_cost = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )

    # Index payment methods
    index_stripe = models.IntegerField(
        default=1,
    )
    index_cash = models.IntegerField(
        default=0,
    )

    objects = StoresQueryset.as_manager()
    translated = TranslationProxy()

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("name", "pk")
        app_label = "store"
        permissions = (
            (
                StorePermissions.MANAGE_STORES.codename,
                "Manage store.",
            ),
        )


class CustomDomain(MultitenantModelWithMetadata):
    store = models.ForeignKey(
        Store,
        related_name="customdomain",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_id ='store_id'
    domain_custom = models.CharField(max_length=256, null=False, blank=False, unique=True)
    status = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        ordering = ("domain_custom", "pk")
        app_label = "store"
        permissions = (
            (
                StorePermissions.MANAGE_STORES.codename,
                "Manage store.",
            ),
        )
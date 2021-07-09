from django.db import models
from versatileimagefield.fields import VersatileImageField
from ..core.utils.translations import TranslationProxy
from ..core.models import CustomQueryset, MultitenantModelWithMetadata
from ..seo.models import SeoModel
from django.utils import timezone
from typing import Union
from ..core.permissions import StorePermissions

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
    logo = VersatileImageField(
        upload_to="store-media", blank=True, null=True
    )
    cover_photo = VersatileImageField(
        upload_to="store-media", blank=True, null=True
    )
    date_joined = models.DateTimeField(default=timezone.now, editable=False)

    #Emergency setting feature
    webshop_status = models.DateTimeField(blank=True, null=True)
    delivery_status = models.DateTimeField(blank=True, null=True)
    pickup_status = models.DateTimeField(blank=True, null=True)

    #New order notifications
    email_notifications = models.BooleanField(blank=True, null=True,default=False)
    email_address = models.EmailField(blank=True, null=True)

    #Transaction cost
    contant_enable = models.BooleanField(blank=True, null=True,default=False)
    contant_cost = models.FloatField(blank=True, null=True, default=0)
    stripe_enable = models.BooleanField(blank=True, null=True,default=False)
    stripe_cost = models.FloatField(blank=True, null=True, default=0)

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
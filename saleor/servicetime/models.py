from saleor.store.models import Store
from django.db import models
from ..core.models import MultitenantModelWithMetadata
from ..core.permissions import ServiceTimePermissions
from ..core.db.fields import SanitizedJSONField
from ..core.utils.editorjs import clean_editor_js

class ServiceTime(MultitenantModelWithMetadata):
    store = models.ForeignKey(
        Store,
        related_name="service_times",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_id='store_id'
    dl_delivery_time = models.IntegerField(blank=True, null=True ,default=10)
    dl_time_gap = models.IntegerField(blank=True, null=True, default=10)
    dl_as_soon_as_posible = models.BooleanField(blank=True, null=True, default=False)
    dl_allow_preorder = models.BooleanField(blank=True, null=True, default=False)
    dl_preorder_day = models.IntegerField(blank=True, null=True, default=0)
    dl_same_day_order = models.BooleanField(blank=True, null=True, default=False)
    dl_service_time = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)

    pu_delivery_time = models.IntegerField(blank=True, null=True ,default=10)
    pu_time_gap = models.IntegerField(blank=True, null=True, default=10)
    pu_as_soon_as_posible = models.BooleanField(blank=True, null=True, default=False)
    pu_allow_preorder = models.BooleanField(blank=True, null=True, default=False)
    pu_preorder_day = models.IntegerField(blank=True, null=True, default=0)
    pu_same_day_order = models.BooleanField(blank=True, null=True, default=False)
    pu_service_time = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("store_id", "pk")
        app_label = "servicetime"
        permissions = (
            (
                ServiceTimePermissions.MANAGE_SERVICE_TIME.codename,
                "Service time.",
            ),
        )
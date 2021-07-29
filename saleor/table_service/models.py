from saleor.store.models import Store
from django.db import models
from ..core.models import MultitenantModelWithMetadata
from ..core.permissions import TableServicePermissions
from ..core.db.fields import SanitizedJSONField

class TableService(MultitenantModelWithMetadata):
    store = models.ForeignKey(
        Store,
        related_name="table_services",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_id ='store_id'
    table_name = models.CharField(max_length=100, null=False, blank=False)
    table_qr_code = models.CharField(max_length=500,null=False, blank=False)

    class Meta:
        ordering = ("table_name", "pk")
        app_label = "table_service"
        permissions = (
            (
                TableServicePermissions.MANAGE_TABLE_SERVICE.codename,
                "Table service.",
            ),
        )
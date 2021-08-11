from saleor import settings
from django.db import models
from saleor.store.models import Store
from ..core.db.fields import SanitizedJSONField
from ..core.utils.editorjs import clean_editor_js
from ..core.models import MultitenantModelWithMetadata

# Create your models here.
class Delivery(MultitenantModelWithMetadata):
    store = models.ForeignKey(
        Store,
        related_name="deliveries",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_id='store_id'
    delivery_area = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)
    delivery_fee = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    from_delivery = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    min_order = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    enable_for_big_order = models.BooleanField(
        default=False
    )
    
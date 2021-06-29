from django.db import models
from ..core.db.fields import SanitizedJSONField
from ..core.utils.editorjs import clean_editor_js

# Create your models here.
class Delivery(models.Model):
    delivery_area = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)
    delivery_fee = models.FloatField(blank=True, null=True, default=0)
    from_delivery = models.FloatField(blank=True, null=True, default=0)
    min_order = models.FloatField(blank=True, null=True, default=0)

    
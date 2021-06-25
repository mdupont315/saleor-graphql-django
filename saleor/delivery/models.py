from django.db import models

# Create your models here.
class Delivery(models.Model):
    delivery_area = models.CharField(max_length=256)
    delivery_fee = models.FloatField()
    from_delivery = models.FloatField()
    min_order = models.FloatField()

    
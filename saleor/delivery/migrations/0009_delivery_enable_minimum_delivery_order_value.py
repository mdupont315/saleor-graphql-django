# Generated by Django 3.2.4 on 2022-03-11 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0008_delivery_enable_custom_delivery_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='enable_minimum_delivery_order_value',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 3.2.4 on 2022-02-07 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0007_delivery_enable_for_big_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='enable_custom_delivery_fee',
            field=models.BooleanField(default=False),
        ),
    ]
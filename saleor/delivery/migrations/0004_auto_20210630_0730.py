# Generated by Django 3.2.4 on 2021-06-30 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0003_alter_delivery_delivery_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='delivery_fee',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='from_delivery',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='min_order',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]

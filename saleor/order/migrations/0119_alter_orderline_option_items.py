# Generated by Django 3.2.4 on 2021-07-21 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0118_orderline_option_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='option_items',
            field=models.JSONField(blank=True, null=True),
        ),
    ]

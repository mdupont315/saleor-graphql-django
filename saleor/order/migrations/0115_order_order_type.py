# Generated by Django 3.2.4 on 2021-07-16 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0114_alter_order_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_type',
            field=models.Field(choices=[('delivery', 'Delivery'), ('pickup', 'Pickup')], default='pickup', max_length=35),
        ),
    ]

# Generated by Django 3.2.4 on 2021-10-29 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0159_auto_20211029_0458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='sku',
            field=models.CharField(blank=True, max_length=255, unique=True),
        ),
    ]
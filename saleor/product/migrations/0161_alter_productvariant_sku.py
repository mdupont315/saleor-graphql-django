# Generated by Django 3.2.4 on 2021-10-29 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0160_alter_productvariant_sku'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='sku',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

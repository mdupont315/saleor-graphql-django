# Generated by Django 3.2.4 on 2021-08-09 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_store_table_service_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='city',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]

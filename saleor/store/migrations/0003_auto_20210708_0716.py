# Generated by Django 3.2.4 on 2021-07-08 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20210706_0841'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='contant_cost',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='contant_enable',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='stripe_cost',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='stripe_enable',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]

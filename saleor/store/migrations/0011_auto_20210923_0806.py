# Generated by Django 3.2.4 on 2021-09-23 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_auto_20210914_0427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='index_cash',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='store',
            name='index_stripe',
            field=models.IntegerField(default=1),
        ),
    ]

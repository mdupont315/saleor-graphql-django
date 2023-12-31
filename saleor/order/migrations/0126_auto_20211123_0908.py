# Generated by Django 3.2.4 on 2021-11-23 09:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0031_auto_20210623_1449'),
        ('channel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0056_auto_20210722_0449'),
        ('order', '0125_auto_20211119_0455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='channel.channel'),
        ),
        migrations.AlterField(
            model_name='order',
            name='original',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.order'),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.address'),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='shipping.shippingmethod'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
    ]

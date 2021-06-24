# Generated by Django 3.2.4 on 2021-06-23 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
        ('wishlist', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wishlists', to='store.store'),
        ),
    ]

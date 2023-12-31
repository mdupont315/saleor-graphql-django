# Generated by Django 3.2.4 on 2022-02-28 12:28

from django.db import migrations, models
import django.db.models.deletion
import django_multitenant.mixins
import saleor.core.utils.json_serializer
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_remove_store_favicon_pwa'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaviconPwa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_metadata', models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('image', versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to='store-media')),
                ('type', models.CharField(max_length=256)),
                ('size', models.IntegerField(default=256)),
                ('store', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='faviconpwa', to='store.store')),
            ],
            options={
                'ordering': ('size', 'pk'),
                'permissions': (('manage_stores', 'Manage store.'),),
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
        ),
    ]

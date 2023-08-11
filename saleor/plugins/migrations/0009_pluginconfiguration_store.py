# Generated by Django 3.2.4 on 2021-08-09 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_auto_20210809_0747'),
        ('plugins', '0008_pluginconfiguration_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='pluginconfiguration',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plugins', to='store.store'),
        ),
    ]
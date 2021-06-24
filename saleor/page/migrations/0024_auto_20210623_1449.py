# Generated by Django 3.2.4 on 2021-06-23 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
        ('page', '0023_auto_20210526_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pages', to='store.store'),
        ),
        migrations.AddField(
            model_name='pagetype',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='page_types', to='store.store'),
        ),
    ]

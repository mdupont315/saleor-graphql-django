# Generated by Django 2.2.3 on 2019-07-15 07:47

from django.db import migrations
from html_to_draftjs import html_to_draftjs


def convert_products_html_to_json(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    qs = Product.objects.filter(description_json={})

    for product in qs:
        product.description_json = html_to_draftjs(product.description)
        product.save(update_fields=["description_json"])

    ProductTranslation = apps.get_model("product", "ProductTranslation")
    qs = ProductTranslation.objects.filter(description_json={})

    for translation in qs:
        translation.description_json = html_to_draftjs(translation.description)
        translation.save(update_fields=["description_json"])


class Migration(migrations.Migration):

    dependencies = [("product", "0095_auto_20190618_0842")]

    operations = [
        migrations.RunPython(convert_products_html_to_json),
        migrations.RemoveField(model_name="product", name="description"),
        migrations.RemoveField(model_name="producttranslation", name="description"),
    ]

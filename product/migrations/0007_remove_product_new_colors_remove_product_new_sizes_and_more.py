# Generated by Django 4.2 on 2023-11-15 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0006_remove_product_colors_remove_product_sizes_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="new_colors",
        ),
        migrations.RemoveField(
            model_name="product",
            name="new_sizes",
        ),
        migrations.AddField(
            model_name="product",
            name="colors",
            field=models.ManyToManyField(
                through="product.ProductColor", to="product.coloroption"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="sizes",
            field=models.ManyToManyField(
                through="product.ProductSize", to="product.sizeoption"
            ),
        ),
    ]
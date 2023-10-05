# Generated by Django 4.2 on 2023-10-04 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0011_rename_amount_stock_product_amount_in_stock"),
        ("vendors", "0001_initial"),
        ("payment", "0004_order_amount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="product.product",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="vendors",
            field=models.ManyToManyField(
                blank=True, related_name="orders", to="vendors.vendor"
            ),
        ),
    ]

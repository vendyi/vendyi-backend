# Generated by Django 4.2 on 2023-09-28 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitem",
            name="color",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="size",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

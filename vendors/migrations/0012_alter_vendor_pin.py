# Generated by Django 4.2 on 2023-11-10 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0011_alter_vendoractivehours_options_alter_vendor_pin"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="pin",
            field=models.CharField(max_length=5),
        ),
    ]

# Generated by Django 4.2 on 2023-11-10 23:57

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0013_alter_vendor_pin"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="pin",
            field=django_cryptography.fields.encrypt(
                models.CharField(blank=True, max_length=5, null=True)
            ),
        ),
    ]